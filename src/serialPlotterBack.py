import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from sklearn.naive_bayes import GaussianNB
import threading
import time
import csv

# --- CONFIGURACIONES GLOBALES BIOMETRÍA ---
PASSWORD_ADMIN = "nordic123"
MAX_USUARIOS = 5
UMBRAL_CONFIANZA = 0.85

# --- FUNCIONES DE EXTRACCIÓN Y SISTEMA BIOMÉTRICO ---
def calcular_caracteristicas(frecuencias, magnitudes, fases):
    frecuencias = np.array(frecuencias)
    magnitudes = np.array(magnitudes)
    fases = np.array(fases)

    # Cálculo de Resistencia (R) y Reactancia (X) a partir de los datos polares
    R = magnitudes * np.cos(fases)
    X = magnitudes * np.sin(fases)

    max_mag = np.max(magnitudes)

    # Espacio log-log (usamos abs() para evitar errores matemáticos con reactancia negativa)
    log_freq = np.log10(frecuencias)
    log_mag = np.log10(magnitudes)
    log_R = np.log10(np.abs(R))
    log_X = np.log10(np.abs(X))

    # Ajuste lineal (regresión)
    slope_mag, int_mag = np.polyfit(log_freq, log_mag, 1)
    slope_R, int_R = np.polyfit(log_freq, log_R, 1)
    slope_X, int_X = np.polyfit(log_freq, log_X, 1)

    return [max_mag, slope_mag, int_mag, slope_R, int_R, slope_X, int_X]

class SistemaBiometrico:
    def __init__(self):
        self.modelo_nb = GaussianNB()
        self.usuarios_registrados = {}
        self.dataset_features = []
        self.dataset_labels = []
        self.modelo_entrenado = False

    def entrenar_modelo(self):
        if len(self.usuarios_registrados) > 0:
            self.modelo_nb.fit(self.dataset_features, self.dataset_labels)
            self.modelo_entrenado = True

    def agregar_usuario(self, nombre, features_list):
        nuevo_id = len(self.usuarios_registrados)
        self.usuarios_registrados[nuevo_id] = nombre

        for features in features_list:
            self.dataset_features.append(features)
            self.dataset_labels.append(nuevo_id)

        self.entrenar_modelo()

    def identificar_usuario(self, features_desconocidas):
        if not self.modelo_entrenado:
            return False, "Sistema no configurado.", 0.0

        probabilidad = self.modelo_nb.predict_proba([features_desconocidas])[0]
        max_prob = np.max(probabilidad)
        id_estimado = np.argmax(probabilidad)

        if max_prob >= UMBRAL_CONFIANZA:
            return True, f"Bienvenido, {self.usuarios_registrados[id_estimado]}", max_prob
        else:
            return False, "Acceso denegado", max_prob

class SerialPlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("AD5940 Serial Plotter")

        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_event = threading.Event()

        self.sistema = SistemaBiometrico()

        # Data storage for plotting
        self.frequencies = []
        self.magnitudes = []
        self.phases = []

        # --- GUI Elements ---
        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        # Set theme if available
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        self.status_var = tk.StringVar(value="Ready")

        # Top Control Frame
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.pack(side=tk.TOP, fill="x")

        # Serial Port Configuration Frame
        serial_frame = ttk.LabelFrame(control_frame, text="Serial Connection", padding="10")
        serial_frame.pack(side=tk.LEFT, fill="y", padx=(0, 5))

        ttk.Label(serial_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.port_combobox = ttk.Combobox(serial_frame, width=20)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.refresh_ports()
        ttk.Button(serial_frame, text="↻ Refresh", command=self.refresh_ports, width=10).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(serial_frame, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.baud_rate_entry = ttk.Entry(serial_frame, width=20)
        self.baud_rate_entry.insert(0, "115200") # Default baud rate
        self.baud_rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.connect_button = ttk.Button(serial_frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(serial_frame, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Command Frame
        command_frame = ttk.LabelFrame(control_frame, text="Acquisition & Data", padding="10")
        command_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0))

        command_frame.columnconfigure(0, weight=1)
        command_frame.columnconfigure(1, weight=1)
        command_frame.columnconfigure(2, weight=1)

        self.send_button = ttk.Button(command_frame, text="▶ Start Acquisition", command=self.start_acquisition, state=tk.DISABLED)
        self.send_button.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(command_frame, text="✖ Clear Plot", command=self.clear_data)
        self.clear_button.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")

        self.save_button = ttk.Button(command_frame, text="💾 Save CSV", command=self.save_data)
        self.save_button.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")

        # Biometrics Frame
        bio_frame = ttk.LabelFrame(control_frame, text="Biometrics", padding="10")
        bio_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0))
        bio_frame.columnconfigure(0, weight=1)
        bio_frame.columnconfigure(1, weight=1)

        self.identify_btn = ttk.Button(bio_frame, text="👤 Identify User", command=self.start_identification, state=tk.DISABLED)
        self.identify_btn.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        self.admin_btn = ttk.Button(bio_frame, text="⚙️ Admin Panel", command=self.open_admin_panel)
        self.admin_btn.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        self.bio_result_var = tk.StringVar(value="Esperando...")
        self.bio_result_lbl = ttk.Label(bio_frame, textvariable=self.bio_result_var, font=("Helvetica", 10, "bold"))
        self.bio_result_lbl.grid(row=1, column=0, columnspan=2, pady=5)

        # Plot Frame
        self.plot_frame = ttk.Frame(self.master, padding="10")
        self.plot_frame.pack(side=tk.TOP, fill="both", expand=True)

        # Status Bar
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, msg):
        self.master.after(0, lambda: self.status_var.set(msg))

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        # Esto creará una lista con el nombre del puerto (ej. /dev/ttyACM0)
        port_list = [port.device for port in ports]

        self.port_combobox['values'] = port_list

        if port_list:
            # Intentar seleccionar automáticamente el que parece un Arduino
            arduino_port = next((p for p in port_list if "ACM" in p or "USB" in p), port_list[0])
            self.port_combobox.set(arduino_port)
        else:
            self.port_combobox.set("")

    def connect_serial(self):
        port = self.port_combobox.get()
        baud_rate = self.baud_rate_entry.get()
        try:
            self.serial_port = serial.Serial(port, int(baud_rate), timeout=1)
            self.is_connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.identify_btn.config(state=tk.NORMAL)
            self.set_status(f"Connected to {port} at {baud_rate} bps")
        except Exception as e:
            messagebox.showerror("Serial Connection Error", str(e))
            self.set_status("Connection failed.")
            self.is_connected = False

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.stop_event.set() # Signal the thread to stop if it's running
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=2) # Wait for thread to finish
            self.serial_port.close()
            self.is_connected = False
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            self.identify_btn.config(state=tk.DISABLED)
            self.set_status("Disconnected from serial port.")

    def setup_plot(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.suptitle("AD5940 BIA Data", fontsize=14, fontweight='bold')
        self.fig.tight_layout(pad=3.0)

        self.line_mag, = self.ax1.plot([], [], 'r-o', label='Magnitude (Ohm)', linewidth=2, markersize=4)
        self.ax1.set_ylabel('Magnitude (Ohm)', fontweight='bold')
        self.ax1.set_xscale('log')
        self.ax1.grid(True, which="both", ls="--", alpha=0.5)
        self.ax1.legend()

        self.line_phase, = self.ax2.plot([], [], 'b-o', label='Phase (deg)', linewidth=2, markersize=4)
        self.ax2.set_xlabel('Frequency (Hz)', fontweight='bold')
        self.ax2.set_ylabel('Phase (deg)', fontweight='bold')
        self.ax2.set_xscale('log')
        self.ax2.grid(True, which="both", ls="--", alpha=0.5)
        self.ax2.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()

        self.canvas.draw()

    def update_plot(self):
        self.line_mag.set_data(self.frequencies, self.magnitudes)
        self.line_phase.set_data(self.frequencies, self.phases)

        # Autoscale axes based on new data
        if self.frequencies:
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.ax1.set_xlim(min(self.frequencies) * 0.9, max(self.frequencies) * 1.1)
            self.ax2.set_xlim(min(self.frequencies) * 0.9, max(self.frequencies) * 1.1)

        self.canvas.draw_idle()

    def read_serial_data(self, mode="single", user_name=""):
        num_points = 48
        num_sweeps = 5 if mode == "register" else 1
        sweeps_features = []

        try:
            self.master.after(0, self.disable_buttons)

            for sweep in range(num_sweeps):
                if self.stop_event.is_set():
                    break

                if mode == "register":
                    self.set_status(f"Acquiring sweep {sweep+1}/{num_sweeps}...")
                else:
                    self.set_status("Acquiring data...")

                self.frequencies = []
                self.magnitudes = []
                self.phases = []
                self.master.after(0, self.update_plot)

                self.serial_port.flushInput()
                self.serial_port.write(b"send\n")

                received_points = 0
                for i in range(num_points):
                    if self.stop_event.is_set():
                        break
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            data = [float(x) for x in line.split(',')]
                            if len(data) >= 3:
                                self.frequencies.append(data[0])
                                self.magnitudes.append(data[1])
                                wrapped_phase = ((data[2] + 180) % 360) - 180
                                self.phases.append(wrapped_phase)
                                received_points += 1

                                # Actualización de gráfica en tiempo real (cada 4 puntos para evitar lag)
                                if received_points % 4 == 0:
                                    self.master.after(0, self.update_plot)
                        except ValueError:
                            print(f"Skipping malformed line: {line}")

                # Actualización final para garantizar graficar el último punto del barrido
                self.master.after(0, self.update_plot)

                if received_points > 0 and not self.stop_event.is_set():
                    features = calcular_caracteristicas(self.frequencies, self.magnitudes, self.phases)
                    sweeps_features.append(features)

                if sweep < num_sweeps - 1 and not self.stop_event.is_set():
                    time.sleep(0.5)

            if not self.stop_event.is_set():
                if mode == "identify" and sweeps_features:
                    self.master.after(0, lambda: self.process_identification(sweeps_features[0]))
                elif mode == "register":
                    if len(sweeps_features) == num_sweeps:
                        self.master.after(0, lambda: self.process_registration(user_name, sweeps_features))
                    else:
                        self.set_status("Registro incompleto.")
                else:
                    self.set_status(f"Acquisition complete. {received_points} points received.")
            else:
                self.set_status("Acquisition stopped.")

        except serial.SerialException as e:
            messagebox.showerror("Serial Read Error", str(e))
            self.set_status("Serial Read Error.")
            self.master.after(0, self.disconnect_serial)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error during acquisition.")
        finally:
            self.master.after(0, self.enable_buttons)

    def clear_data(self):
        self.frequencies = []
        self.magnitudes = []
        self.phases = []
        self.update_plot()
        self.set_status("Plot cleared.")

    def save_data(self):
        if not self.frequencies:
            messagebox.showwarning("No Data", "There is no data to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save BIA Data"
        )
        if filepath:
            try:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Frequency (Hz)", "Magnitude (Ohm)", "Phase (deg)"])
                    for freq, mag, phase in zip(self.frequencies, self.magnitudes, self.phases):
                        writer.writerow([freq, mag, phase])
                self.set_status(f"Data successfully saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error Saving File", str(e))
                self.set_status("Failed to save data.")

    def start_acquisition(self):
        self.start_acquisition_task("single")

    def start_identification(self):
        self.start_acquisition_task("identify")

    def start_registration(self, user_name):
        self.start_acquisition_task("register", user_name)

    def start_acquisition_task(self, mode="single", user_name=""):
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a serial port first.")
            return

        self.stop_event.clear() # Clear stop event for new acquisition
        self.read_thread = threading.Thread(target=self.read_serial_data, args=(mode, user_name))
        self.read_thread.daemon = True # Allow the main program to exit even if thread is running
        self.read_thread.start()

    def disable_buttons(self):
        self.send_button.config(state=tk.DISABLED)
        self.identify_btn.config(state=tk.DISABLED)
        self.admin_btn.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.admin_btn.config(state=tk.NORMAL)
        if self.is_connected:
            self.send_button.config(state=tk.NORMAL)
            self.identify_btn.config(state=tk.NORMAL)

    def process_identification(self, features):
        success, msg, max_prob = self.sistema.identificar_usuario(features)
        color = "green" if success else "red"
        self.bio_result_var.set(f"{msg} ({max_prob*100:.1f}%)")
        self.bio_result_lbl.config(foreground=color)

    def process_registration(self, user_name, sweeps_features):
        self.sistema.agregar_usuario(user_name, sweeps_features)
        self.bio_result_var.set(f"Usuario {user_name} registrado")
        self.bio_result_lbl.config(foreground="green")
        messagebox.showinfo("Registro Exitoso", f"Usuario '{user_name}' registrado exitosamente en la base de datos.")

    def open_admin_panel(self):
        pwd = simpledialog.askstring("Admin Login", "Ingrese contraseña de administrador:", show='*')
        if pwd != PASSWORD_ADMIN:
            if pwd is not None:
                messagebox.showerror("Error", "Contraseña incorrecta")
            return

        admin_win = tk.Toplevel(self.master)
        admin_win.title("Panel de Administrador")
        admin_win.geometry("350x300")

        ttk.Label(admin_win, text=f"Usuarios Registrados: {len(self.sistema.usuarios_registrados)}/{MAX_USUARIOS}", font=("Helvetica", 10, "bold")).pack(pady=10)

        listbox = tk.Listbox(admin_win, height=5)
        for uid, unombre in self.sistema.usuarios_registrados.items():
            listbox.insert(tk.END, f"ID {uid}: {unombre}")
        listbox.pack(fill=tk.BOTH, padx=20, pady=5)

        ttk.Label(admin_win, text="Nombre del nuevo usuario:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(admin_win, textvariable=name_var).pack(padx=20, fill=tk.X)

        def on_register():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Atención", "El nombre no puede estar vacío.")
                return
            if len(self.sistema.usuarios_registrados) >= MAX_USUARIOS:
                messagebox.showerror("Error", f"Límite de {MAX_USUARIOS} usuarios alcanzado.")
                return

            admin_win.destroy()
            messagebox.showinfo("Registro", "Se iniciará la recopilación de 5 mediciones. Mantenga el brazo quieto.")
            self.start_registration(name)

        ttk.Button(admin_win, text="Iniciar Registro (5 barridos)", command=on_register).pack(pady=15)

    def on_closing(self):
        if self.is_connected:
            self.disconnect_serial()
        self.master.destroy()
        plt.close(self.fig) # Close the matplotlib figure

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
