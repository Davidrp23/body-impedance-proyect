import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import threading
import time
import csv
import os
import hashlib
import sqlite3
import json
from scipy.optimize import least_squares

# --- CONFIGURACIONES GLOBALES ---
PASSWORD_DB_FILE = "secret.dat"
DEFAULT_PASSWORD = "nordic123"
DB_FILE = "biometria.db"
MAX_USUARIOS = 5
UMBRAL_CONFIANZA = 0.85

# --- FUNCIONES DE SEGURIDAD Y BASE DE DATOS ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_hash, provided_password):
    return stored_hash == hash_password(provided_password)

def initialize_password():
    if not os.path.exists(PASSWORD_DB_FILE):
        with open(PASSWORD_DB_FILE, "w") as f:
            f.write(hash_password(DEFAULT_PASSWORD))

def get_stored_hash():
    with open(PASSWORD_DB_FILE, "r") as f:
        return f.read().strip()

def update_stored_hash(new_password):
    with open(PASSWORD_DB_FILE, "w") as f:
        f.write(hash_password(new_password))

def init_db():
    """Inicializa la base de datos SQLite y crea las tablas si no existen."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS caracteristicas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, features TEXT)''')
    conn.commit()
    conn.close()

# --- FUNCIONES DE EXTRACCIÓN MATEMÁTICA ---
def fit_cole_model_ideal(frecuencias, magnitudes, fases):
    f = np.array(frecuencias)
    mag = np.array(magnitudes)
    fases_rad = np.radians(np.array(fases))
    
    Z_real_data = mag * np.cos(fases_rad)
    Z_imag_data = mag * np.sin(fases_rad)
    
    def residual(params):
        R0, Rinf, fc = params
        if fc <= 0: return np.ones(2 * len(f)) * 1e6
        omega_ratio = f / fc
        den = 1 + omega_ratio**2
        Z_model_real = Rinf + (R0 - Rinf) / den
        Z_model_imag = -(R0 - Rinf) * omega_ratio / den
        return np.concatenate((Z_model_real - Z_real_data, Z_model_imag - Z_imag_data))
        
    R0_guess = mag[0] if len(mag) > 0 else 1000.0
    Rinf_guess = mag[-1] if len(mag) > 0 else 100.0
    fc_guess = 50000.0
    
    p0 = [R0_guess, Rinf_guess, fc_guess]
    bounds = ([0, 0, 1.0], [np.inf, np.inf, 1e7])
    
    try:
        res = least_squares(residual, p0, bounds=bounds, method='trf')
        return list(res.x)
    except Exception as e:
        print(f"Error ajustando el modelo: {e}")
        return p0

def calcular_caracteristicas(frecuencias, magnitudes, fases, metodo="Regresión Lineal"):
    if metodo == "Cole-Cole (Ideal)":
        return fit_cole_model_ideal(frecuencias, magnitudes, fases)
        
    frecuencias = np.array(frecuencias)
    magnitudes = np.array(magnitudes)
    fases = np.array(fases)
    
    R = magnitudes * np.cos(fases)
    X = magnitudes * np.sin(fases)
    max_mag = np.max(magnitudes)
    
    log_freq = np.log10(frecuencias)
    log_mag = np.log10(magnitudes)
    log_R = np.log10(np.maximum(np.abs(R), 1e-6))
    log_X = np.log10(np.maximum(np.abs(X), 1e-6))
    
    slope_mag, int_mag = np.polyfit(log_freq, log_mag, 1)
    slope_R, int_R = np.polyfit(log_freq, log_R, 1)
    slope_X, int_X = np.polyfit(log_freq, log_X, 1)
    
    return [max_mag, slope_mag, int_mag, slope_R, int_R, slope_X, int_X]

# --- SISTEMA BIOMÉTRICO (AHORA CONECTADO A SQLITE) ---
class SistemaBiometrico:
    def __init__(self):
        self.usuarios_registrados = {} 
        self.dataset_features = []
        self.dataset_labels = []
        self.modelo_entrenado = False
        self.cargar_desde_db()

    def cargar_desde_db(self):
        """Carga los usuarios y sus características desde SQLite a la memoria RAM."""
        self.usuarios_registrados.clear()
        self.dataset_features.clear()
        self.dataset_labels.clear()
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute("SELECT id, nombre FROM usuarios")
        for row in c.fetchall():
            self.usuarios_registrados[row[0]] = row[1]
            
        c.execute("SELECT usuario_id, features FROM caracteristicas")
        for row in c.fetchall():
            uid = row[0]
            feats = json.loads(row[1])
            self.dataset_labels.append(uid)
            self.dataset_features.append(feats)
            
        conn.close()
        self.entrenar_modelo()

    def entrenar_modelo(self):
        self.modelo_entrenado = len(self.usuarios_registrados) > 0

    def agregar_usuario(self, nombre, features_list):
        """Guarda un nuevo usuario en la base de datos y actualiza la RAM."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
        nuevo_id = c.lastrowid
        
        for features in features_list:
            # Guardamos el array de características como un texto JSON
            c.execute("INSERT INTO caracteristicas (usuario_id, features) VALUES (?, ?)", 
                      (nuevo_id, json.dumps(list(features))))
            
        conn.commit()
        conn.close()
        self.cargar_desde_db() # Refrescar RAM

    def borrar_usuario(self, uid):
        """Elimina a un usuario y sus mediciones de la base de datos."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
        c.execute("DELETE FROM caracteristicas WHERE usuario_id = ?", (uid,))
        conn.commit()
        conn.close()
        self.cargar_desde_db() # Refrescar RAM

    def identificar_usuario(self, features_desconocidas):
        if not self.modelo_entrenado:
            return False, "Sistema no configurado.", 0.0

        features = np.array(features_desconocidas)
        mejor_id = None
        mejor_similitud = 0.0
        
        for uid in self.usuarios_registrados:
            indices = [i for i, label in enumerate(self.dataset_labels) if label == uid]
            user_sweeps = np.array([self.dataset_features[i] for i in indices])
            
            if user_sweeps.shape[1] != features.shape[0]:
                continue
                
            media = np.mean(user_sweeps, axis=0)
            rango = np.max(user_sweeps, axis=0) - np.min(user_sweeps, axis=0)
            
            margen = np.maximum(rango, np.abs(media) * 0.05)
            margen = np.where(margen == 0, 1e-6, margen)
            
            desviaciones = np.abs(features - media) / margen
            error_medio = np.mean(desviaciones)
            
            similitud = np.exp(-0.16 * error_medio)
            
            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_id = uid

        if mejor_id is None:
            return False, "Error dimensional", 0.0

        if mejor_similitud >= UMBRAL_CONFIANZA:
            return True, f"Bienvenido, {self.usuarios_registrados[mejor_id]}", mejor_similitud
        else:
            candidato = self.usuarios_registrados[mejor_id] if mejor_id is not None else "N/A"
            return False, f"Acceso denegado (Similar a: {candidato})", mejor_similitud

# --- INTERFAZ GRÁFICA PRINCIPAL ---
class SerialPlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("Ploteador Serial AD5940 - Base de Datos SQLite")

        # Inicialización de subsistemas (Archivos y DB)
        initialize_password()
        init_db()

        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_event = threading.Event()
        
        self.sistema = SistemaBiometrico()
        self.auto_save_csv = tk.BooleanVar(value=False)

        self.frequencies = []
        self.magnitudes = []
        self.phases = []
        self.last_raw_sweeps = [] 

        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        self.status_var = tk.StringVar(value="Listo")
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.pack(side=tk.TOP, fill="x")

        # Serial Frame
        serial_frame = ttk.LabelFrame(control_frame, text="Conexión Serial", padding="10")
        serial_frame.pack(side=tk.LEFT, fill="y", padx=(0, 5))

        ttk.Label(serial_frame, text="Puerto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.port_combobox = ttk.Combobox(serial_frame, width=20)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.refresh_ports()
        ttk.Button(serial_frame, text="↻ Actualizar", command=self.refresh_ports, width=12).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(serial_frame, text="Tasa de Baudios:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.baud_rate_entry = ttk.Entry(serial_frame, width=20)
        self.baud_rate_entry.insert(0, "115200")
        self.baud_rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.connect_button = ttk.Button(serial_frame, text="Conectar", command=self.connect_serial)
        self.connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(serial_frame, text="Desconectar", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Command Frame
        command_frame = ttk.LabelFrame(control_frame, text="Adquisición y Datos", padding="10")
        command_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0))
        command_frame.columnconfigure(0, weight=1)
        command_frame.columnconfigure(1, weight=1)
        command_frame.columnconfigure(2, weight=1)

        self.send_button = ttk.Button(command_frame, text="▶ Iniciar Adquisición", command=self.start_acquisition, state=tk.DISABLED)
        self.send_button.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(command_frame, text="✖ Limpiar Gráfica", command=self.clear_data)
        self.clear_button.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")

        self.save_button = ttk.Button(command_frame, text="💾 Guardar CSV Actual", command=self.save_data)
        self.save_button.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")

        # Biometrics Frame
        bio_frame = ttk.LabelFrame(control_frame, text="Biometría", padding="10")
        bio_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0))
        bio_frame.columnconfigure(0, weight=1)
        bio_frame.columnconfigure(1, weight=1)

        self.identify_btn = ttk.Button(bio_frame, text="👤 Identificar Usuario", command=self.start_identification, state=tk.DISABLED)
        self.identify_btn.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        self.admin_btn = ttk.Button(bio_frame, text="⚙️ Panel Admin", command=self.open_admin_panel)
        self.admin_btn.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        model_subframe = ttk.Frame(bio_frame)
        model_subframe.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(model_subframe, text="Modelo:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar(value="Regresión Lineal")
        self.model_combo = ttk.Combobox(model_subframe, textvariable=self.model_var, 
                                        values=["Regresión Lineal", "Cole-Cole (Ideal)"], 
                                        state="readonly", width=18)
        self.model_combo.pack(side=tk.LEFT)

        self.bio_result_var = tk.StringVar(value="Esperando...")
        self.bio_result_lbl = ttk.Label(bio_frame, textvariable=self.bio_result_var, font=("Helvetica", 10, "bold"))
        self.bio_result_lbl.grid(row=2, column=0, columnspan=2, pady=5)

        # Plot Frame
        self.plot_frame = ttk.Frame(self.master, padding="10")
        self.plot_frame.pack(side=tk.TOP, fill="both", expand=True)
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, msg):
        self.master.after(0, lambda: self.status_var.set(msg))

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combobox['values'] = port_list
        if port_list:
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
            self.set_status(f"Conectado a {port} a {baud_rate} bps")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.is_connected = False

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.stop_event.set()
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=2)
            self.serial_port.close()
            self.is_connected = False
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            self.identify_btn.config(state=tk.DISABLED)
            self.set_status("Desconectado.")

    def setup_plot(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.suptitle("Datos BIA AD5940", fontsize=14, fontweight='bold')
        self.fig.tight_layout(pad=3.0)

        self.line_mag, = self.ax1.plot([], [], 'r-o', linewidth=2, markersize=4)
        self.ax1.set_ylabel('Magnitud (Ohm)', fontweight='bold')
        self.ax1.set_xscale('log'); self.ax1.grid(True, which="both", ls="--", alpha=0.5)

        self.line_phase, = self.ax2.plot([], [], 'b-o', linewidth=2, markersize=4)
        self.ax2.set_xlabel('Frecuencia (Hz)', fontweight='bold')
        self.ax2.set_ylabel('Fase (grados)', fontweight='bold')
        self.ax2.set_xscale('log'); self.ax2.grid(True, which="both", ls="--", alpha=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.canvas.draw()

    def update_plot(self):
        self.line_mag.set_data(self.frequencies, self.magnitudes)
        self.line_phase.set_data(self.frequencies, self.phases)
        if self.frequencies:
            self.ax1.relim(); self.ax1.autoscale_view()
            self.ax2.relim(); self.ax2.autoscale_view()
            self.ax1.set_xlim(min(self.frequencies)*0.9, max(self.frequencies)*1.1)
            self.ax2.set_xlim(min(self.frequencies)*0.9, max(self.frequencies)*1.1)
        self.canvas.draw_idle()

    # --- FUNCIONES DE ARCHIVOS CSV ---
    def read_csv_file(self, filepath):
        sweeps = []
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader, None) 
                freqs, mags, phases = [], [], []
                for row in reader:
                    if len(row) >= 3:
                        try:
                            freqs.append(float(row[0]))
                            mags.append(float(row[1]))
                            phases.append(float(row[2]))
                        except ValueError: pass
                
                chunk_size = 48
                if len(freqs) >= chunk_size:
                    for i in range(0, len(freqs), chunk_size):
                        chunk_f = freqs[i:i+chunk_size]
                        chunk_m = mags[i:i+chunk_size]
                        chunk_p = phases[i:i+chunk_size]
                        if len(chunk_f) == chunk_size:
                            sweeps.append((chunk_f, chunk_m, chunk_p))
                elif len(freqs) > 0:
                    sweeps.append((freqs, mags, phases))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo CSV:\n{e}")
        return sweeps

    def save_raw_sweeps_to_csv(self):
        if not self.last_raw_sweeps: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar los 5 barridos")
        if filepath:
            try:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Frecuencia (Hz)", "Magnitud (Ohm)", "Fase (grados)"])
                    for sweep in self.last_raw_sweeps:
                        for row in sweep: writer.writerow(row)
                self.set_status(f"Guardado en {filepath}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_data(self):
        if not self.frequencies:
            messagebox.showwarning("Sin Datos", "No hay datos para guardar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filepath:
            try:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Frecuencia (Hz)", "Magnitud (Ohm)", "Fase (grados)"])
                    for freq, mag, phase in zip(self.frequencies, self.magnitudes, self.phases):
                        writer.writerow([freq, mag, phase])
                self.set_status("Datos guardados exitosamente")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_data(self):
        self.frequencies, self.magnitudes, self.phases = [], [], []
        self.update_plot()

    # --- LECTURA SERIAL Y FLUJOS ---
    def read_serial_data(self, mode="single", user_name="", metodo_extraccion="Regresión Lineal"):
        num_points = 48
        num_sweeps = 5 if mode == "register" else 1
        sweeps_features = []
        self.last_raw_sweeps = []

        try:
            self.master.after(0, self.disable_buttons)
            for sweep in range(num_sweeps):
                if self.stop_event.is_set(): break
                self.set_status(f"Adquiriendo barrido {sweep+1}/{num_sweeps}..." if mode=="register" else "Adquiriendo datos...")

                self.frequencies, self.magnitudes, self.phases, current_raw_sweep = [], [], [], []
                self.master.after(0, self.update_plot)
                self.serial_port.flushInput()
                self.serial_port.write(b"send\n")

                received_points = 0
                for _ in range(num_points):
                    if self.stop_event.is_set(): break
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            data = [float(x) for x in line.split(',')]
                            if len(data) >= 3:
                                self.frequencies.append(data[0])
                                self.magnitudes.append(data[1])
                                wrapped_phase = ((data[2] + 180) % 360) - 180
                                self.phases.append(wrapped_phase)
                                current_raw_sweep.append([data[0], data[1], wrapped_phase])
                                received_points += 1
                                if received_points % 4 == 0: self.master.after(0, self.update_plot)
                        except ValueError: pass
                
                self.master.after(0, self.update_plot)
                
                if received_points > 0 and not self.stop_event.is_set():
                    feat = calcular_caracteristicas(self.frequencies, self.magnitudes, self.phases, metodo_extraccion)
                    sweeps_features.append(feat)
                    self.last_raw_sweeps.append(current_raw_sweep)
                if sweep < num_sweeps - 1 and not self.stop_event.is_set(): time.sleep(0.5)

            if not self.stop_event.is_set():
                if mode == "identify" and sweeps_features:
                    self.master.after(0, lambda: self.process_identification(sweeps_features[0]))
                elif mode == "register":
                    if len(sweeps_features) == num_sweeps:
                        self.master.after(0, lambda: self.process_registration(user_name, sweeps_features))
                        if self.auto_save_csv.get(): self.master.after(500, self.save_raw_sweeps_to_csv)
                    else: self.set_status("Registro incompleto.")
                else: self.set_status("Adquisición completada.")
            else: self.set_status("Detenida.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.master.after(0, self.disconnect_serial)
        finally:
            self.master.after(0, self.enable_buttons)

    def start_acquisition(self): self.start_acquisition_task("single")
    def start_identification(self): self.start_acquisition_task("identify")
    def start_registration(self, user_name): self.start_acquisition_task("register", user_name)

    def start_acquisition_task(self, mode="single", user_name=""):
        if not self.is_connected:
            messagebox.showwarning("Atención", "Conéctese al puerto serial primero.")
            return
        self.stop_event.clear()
        threading.Thread(target=self.read_serial_data, args=(mode, user_name, self.model_var.get()), daemon=True).start()

    def disable_buttons(self):
        self.send_button.config(state=tk.DISABLED)
        self.identify_btn.config(state=tk.DISABLED)
        self.admin_btn.config(state=tk.DISABLED)
        self.model_combo.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.admin_btn.config(state=tk.NORMAL)
        self.model_combo.config(state="readonly")
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
        messagebox.showinfo("Éxito", f"Usuario '{user_name}' guardado en la Base de Datos SQLite.")

    # --- PANEL ADMINISTRADOR (INTEGRACIÓN SQLITE Y CSV) ---
    def open_admin_panel(self):
        pwd = simpledialog.askstring("Admin", "Ingrese contraseña:", show='*')
        if not pwd or not verify_password(get_stored_hash(), pwd):
            if pwd is not None: messagebox.showerror("Error", "Contraseña incorrecta")
            return
            
        admin_win = tk.Toplevel(self.master)
        admin_win.title("Panel de Administrador DB")
        admin_win.geometry("450x650") 
        
        ttk.Label(admin_win, text="BASE DE DATOS DE USUARIOS (SQLite)", font=("Helvetica", 10, "bold")).pack(pady=(15, 5))
        
        # Frame para la lista y el botón de borrar
        list_frame = ttk.Frame(admin_win)
        list_frame.pack(fill=tk.BOTH, padx=20, pady=5)
        
        lbl_count = ttk.Label(list_frame, text="")
        lbl_count.pack(anchor="w")
        
        listbox = tk.Listbox(list_frame, height=6)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        
        # Función para refrescar la lista desde la RAM (que ya está sincronizada con SQLite)
        def actualizar_lista():
            listbox.delete(0, tk.END)
            for uid, unombre in self.sistema.usuarios_registrados.items():
                listbox.insert(tk.END, f"ID {uid} - {unombre}")
            lbl_count.config(text=f"Registrados: {len(self.sistema.usuarios_registrados)} / {MAX_USUARIOS}")

        actualizar_lista()
        
        # --- BOTÓN ELIMINAR USUARIO ---
        def on_delete_user():
            seleccion = listbox.curselection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccione un usuario de la lista.")
                return
            item_text = listbox.get(seleccion[0])
            uid = int(item_text.split(" ")[1]) # Extrae el ID (ej: "ID 3 - Juan" -> 3)
            
            if messagebox.askyesno("Confirmar", f"¿Borrar permanentemente al usuario '{self.sistema.usuarios_registrados[uid]}' de la base de datos?"):
                self.sistema.borrar_usuario(uid)
                actualizar_lista()
                messagebox.showinfo("Borrado", "Usuario eliminado de SQLite.")

        ttk.Button(admin_win, text="🗑️ Borrar Seleccionado", command=on_delete_user).pack(pady=5)
        
        ttk.Separator(admin_win, orient='horizontal').pack(fill='x', pady=10, padx=20)
        
        # --- AGREGAR USUARIOS ---
        ttk.Label(admin_win, text="Nombre del nuevo usuario:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(admin_win, textvariable=name_var).pack(padx=20, fill=tk.X)
        
        def on_register():
            name = name_var.get().strip()
            if not name: return messagebox.showwarning("Error", "Nombre vacío.")
            if len(self.sistema.usuarios_registrados) >= MAX_USUARIOS: return messagebox.showerror("Error", "Límite alcanzado.")
            
            admin_win.destroy()
            messagebox.showinfo("Registro", "Mantenga el brazo quieto (5 barridos).")
            self.start_registration(name)
            
        def on_register_csv():
            name = name_var.get().strip()
            if not name: return messagebox.showwarning("Error", "Nombre vacío.")
            if len(self.sistema.usuarios_registrados) >= MAX_USUARIOS: return messagebox.showerror("Error", "Límite alcanzado.")
            
            filepath = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
            if not filepath: return
            
            sweeps_data = self.read_csv_file(filepath)
            if not sweeps_data: return
            while len(sweeps_data) < 5: sweeps_data.append(sweeps_data[0])
                
            metodo = self.model_var.get()
            sweeps_features = [calcular_caracteristicas(f, m, p, metodo) for f, m, p in sweeps_data[:5]]
            admin_win.destroy()
            self.process_registration(name, sweeps_features)
            
        def on_identify_csv():
            if len(self.sistema.usuarios_registrados) == 0: return messagebox.showwarning("Error", "Base de datos vacía.")
            filepath = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
            if not filepath: return
            sweeps_data = self.read_csv_file(filepath)
            if not sweeps_data: return
            feat = calcular_caracteristicas(sweeps_data[0][0], sweeps_data[0][1], sweeps_data[0][2], self.model_var.get())
            admin_win.destroy()
            self.process_identification(feat)

        ttk.Button(admin_win, text="▶ Iniciar Registro (Vivo)", command=on_register).pack(pady=(10, 5), padx=20, fill=tk.X)
        ttk.Button(admin_win, text="📁 Importar Registro desde CSV", command=on_register_csv).pack(pady=5, padx=20, fill=tk.X)
        ttk.Button(admin_win, text="🔍 Simular Identificación CSV", command=on_identify_csv).pack(pady=5, padx=20, fill=tk.X)

        # --- CONFIGURACIONES ---
        ttk.Separator(admin_win, orient='horizontal').pack(fill='x', pady=10, padx=20)
        ttk.Checkbutton(admin_win, text="Auto-guardar CSV al registrar en vivo", variable=self.auto_save_csv).pack(pady=5)
        
        def on_change_password():
            new_pwd = simpledialog.askstring("Password", "NUEVA contraseña:", show='*')
            if new_pwd:
                conf_pwd = simpledialog.askstring("Password", "Confirmar:", show='*')
                if new_pwd == conf_pwd:
                    update_stored_hash(new_pwd)
                    messagebox.showinfo("Éxito", "Contraseña actualizada.")
                else: messagebox.showerror("Error", "No coinciden.")
                    
        ttk.Button(admin_win, text="Cambiar Contraseña Maestra", command=on_change_password).pack(pady=10)

    def on_closing(self):
        if self.is_connected: self.disconnect_serial()
        self.master.destroy()
        plt.close(self.fig)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()