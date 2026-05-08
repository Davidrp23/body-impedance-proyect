import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import threading
import time
import csv

class SerialPlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("AD5940 Serial Plotter")

        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_event = threading.Event()

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
        command_frame.rowconfigure(0, weight=1)

        self.send_button = ttk.Button(command_frame, text="▶ Start Acquisition", command=self.start_acquisition, state=tk.DISABLED)
        self.send_button.grid(row=0, column=0, padx=10, pady=15, sticky="nsew")

        self.clear_button = ttk.Button(command_frame, text="✖ Clear Plot", command=self.clear_data)
        self.clear_button.grid(row=0, column=1, padx=10, pady=15, sticky="nsew")

        self.save_button = ttk.Button(command_frame, text="💾 Save CSV", command=self.save_data)
        self.save_button.grid(row=0, column=2, padx=10, pady=15, sticky="nsew")

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

    def read_serial_data(self):
        num_points = 48 # Assuming 48 points as per AD5940Main.c DEFAULT_SWEEP_POINTS

        try:
            self.set_status("Acquiring data...")
            self.master.after(1, lambda: self.send_button.config(state=tk.DISABLED)) # Disable button temporarily
            self.serial_port.flushInput() # Clear any pending input before sending command
            self.serial_port.write(b"send\n")

            received_points = 0
            for i in range(num_points):
                if self.stop_event.is_set():
                    break
                line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    try:
                        # Expected format: freq,mag,phase,real,imag
                        data = [float(x) for x in line.split(',')]
                        if len(data) >= 3:
                            self.frequencies.append(data[0])
                            self.magnitudes.append(data[1])
                            # Normalizar la fase para que siempre esté entre -180 y +180
                            wrapped_phase = ((data[2] + 180) % 360) - 180
                            self.phases.append(wrapped_phase)
                            received_points += 1
                    except ValueError:
                        print(f"Skipping malformed line: {line}")
                else:
                    print("Received empty line or timeout during acquisition.")
            
            if not self.stop_event.is_set():
                self.master.after(1, self.update_plot) # Update plot once all data is received
                self.set_status(f"Acquisition complete. {received_points} points received.")
            else:
                self.set_status("Acquisition stopped.")
            
        except serial.SerialException as e:
            messagebox.showerror("Serial Read Error", str(e))
            self.set_status("Serial Read Error.")
            self.master.after(1, self.disconnect_serial) # Disconnect on error
        except Exception as e:
            messagebox.showerror("Error during acquisition", str(e))
            self.set_status("Error during acquisition.")
        finally:
            self.master.after(1, lambda: self.send_button.config(state=tk.NORMAL)) # Re-enable button

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
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a serial port first.")
            return

        self.stop_event.clear() # Clear stop event for new acquisition
        self.read_thread = threading.Thread(target=self.read_serial_data)
        self.read_thread.daemon = True # Allow the main program to exit even if thread is running
        self.read_thread.start()

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