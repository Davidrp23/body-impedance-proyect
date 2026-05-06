import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time

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
        # Serial Port Configuration Frame
        serial_frame = ttk.LabelFrame(self.master, text="Serial Port Configuration")
        serial_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(serial_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.port_combobox = ttk.Combobox(serial_frame, width=25)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.refresh_ports()
        ttk.Button(serial_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(serial_frame, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.baud_rate_entry = ttk.Entry(serial_frame, width=20)
        self.baud_rate_entry.insert(0, "115200") # Default baud rate
        self.baud_rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.connect_button = ttk.Button(serial_frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(serial_frame, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Command Frame
        command_frame = ttk.LabelFrame(self.master, text="Commands")
        command_frame.pack(padx=10, pady=5, fill="x")

        self.send_button = ttk.Button(command_frame, text="Send 'send' & Acquire Data", command=self.start_acquisition, state=tk.DISABLED)
        self.send_button.pack(padx=5, pady=5, fill="x")

        # Plot Frame
        self.plot_frame = ttk.LabelFrame(self.master, text="Real-time Plot")
        self.plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

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
            messagebox.showinfo("Serial Connection", f"Connected to {port} at {baud_rate} bps")
        except Exception as e:
            messagebox.showerror("Serial Connection Error", str(e))
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
            messagebox.showinfo("Serial Connection", "Disconnected from serial port")

    def setup_plot(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.suptitle("AD5940 BIA Data")

        self.line_mag, = self.ax1.plot([], [], 'r-o', label='Magnitude (Ohm)')
        self.ax1.set_ylabel('Magnitude (Ohm)')
        self.ax1.set_xscale('log')
        self.ax1.grid(True)
        self.ax1.legend()

        self.line_phase, = self.ax2.plot([], [], 'b-o', label='Phase (deg)')
        self.ax2.set_xlabel('Frequency (Hz)')
        self.ax2.set_ylabel('Phase (deg)')
        self.ax2.set_xscale('log')
        self.ax2.grid(True)
        self.ax2.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
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
        self.frequencies = []
        self.magnitudes = []
        self.phases = []
        num_points = 48 # Assuming 48 points as per AD5940Main.c DEFAULT_SWEEP_POINTS

        try:
            self.master.after(1, lambda: self.send_button.config(state=tk.DISABLED)) # Disable button temporarily
            self.serial_port.flushInput() # Clear any pending input before sending command
            self.serial_port.write(b"send\n")

            for i in range(num_points):
                if self.stop_event.is_set():
                    break
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    try:
                        # Expected format: freq,mag,phase,real,imag
                        data = [float(x) for x in line.split(',')]
                        if len(data) >= 3:
                            self.frequencies.append(data[0])
                            self.magnitudes.append(data[1])
                            self.phases.append(data[2])
                    except ValueError:
                        print(f"Skipping malformed line: {line}")
                else:
                    print("Received empty line or timeout during acquisition.")
            
            if not self.stop_event.is_set():
                self.master.after(1, self.update_plot) # Update plot once all data is received
            
        except serial.SerialException as e:
            messagebox.showerror("Serial Read Error", str(e))
            self.master.after(1, self.disconnect_serial) # Disconnect on error
        except Exception as e:
            messagebox.showerror("Error during acquisition", str(e))
        finally:
            self.master.after(1, lambda: self.send_button.config(state=tk.NORMAL)) # Re-enable button

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