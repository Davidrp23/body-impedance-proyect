import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from sklearn.naive_bayes import GaussianNB
import threading
import time
import csv

# --- CONFIGURACIONES GLOBALES ---
PASSWORD_ADMIN = "nordic123"
MAX_USUARIOS = 5
UMBRAL_CONFIANZA = 0.85

# --- CLASE DEL SISTEMA BIOMÉTRICO ---
class SistemaBiometrico:
    def __init__(self):
        self.modelo_nb = GaussianNB()
        self.usuarios_registrados = {} 
        self.dataset_features = []
        self.dataset_labels = []
        self.modelo_entrenado = False

    def calcular_caracteristicas(self, frecuencias, magnitudes, fases):
        if not frecuencias:
            return None
            
        frecuencias = np.array(frecuencias)
        magnitudes = np.array(magnitudes)
        fases = np.array(fases)
        
        # Cálculo de Resistencia (R) y Reactancia (X)
        R = magnitudes * np.cos(np.radians(fases))
        X = magnitudes * np.sin(np.radians(fases))
        
        max_mag = np.max(magnitudes)
        
        # Espacio log-log (evitamos log(0) con un pequeño offset si es necesario)
        log_freq = np.log10(frecuencias)
        log_mag = np.log10(magnitudes)
        log_R = np.log10(np.abs(R) + 1e-9)
        log_X = np.log10(np.abs(X) + 1e-9)
        
        # Ajuste lineal (regresión)
        slope_mag, int_mag = np.polyfit(log_freq, log_mag, 1)
        slope_R, int_R = np.polyfit(log_freq, log_R, 1)
        slope_X, int_X = np.polyfit(log_freq, log_X, 1)
        
        return [max_mag, slope_mag, int_mag, slope_R, int_R, slope_X, int_X]

    def entrenar_modelo(self):
        if len(self.usuarios_registrados) > 0:
            self.modelo_nb.fit(self.dataset_features, self.dataset_labels)
            self.modelo_entrenado = True
            return True
        return False

    def agregar_usuario(self, nombre, lista_features):
        if len(self.usuarios_registrados) >= MAX_USUARIOS:
            return False, f"Límite máximo de {MAX_USUARIOS} usuarios alcanzado."

        nuevo_id = len(self.usuarios_registrados)
        self.usuarios_registrados[nuevo_id] = nombre
        
        for features in lista_features:
            self.dataset_features.append(features)
            self.dataset_labels.append(nuevo_id)
            
        self.entrenar_modelo()
        return True, f"Usuario '{nombre}' agregado exitosamente."

    def identificar_usuario(self, features_desconocidas):
        if not self.modelo_entrenado:
            return False, "Sistema no configurado. Registre al menos un usuario."

        probabilidades = self.modelo_nb.predict_proba([features_desconocidas])[0]
        max_prob = np.max(probabilidades)
        id_estimado = np.argmax(probabilidades)

        if max_prob >= UMBRAL_CONFIANZA:
            nombre_usuario = self.usuarios_registrados[id_estimado]
            return True, f"ACCESO AUTORIZADO: ¡Bienvenido, {nombre_usuario}! (Confianza: {max_prob*100:.1f}%)"
        else:
            return False, f"ACCESO DENEGADO: Usuario desconocido. (Confianza: {max_prob*100:.1f}%)"

# --- CLASE PRINCIPAL DE LA APLICACIÓN GUI ---
class AppBioimpedancia:
    def __init__(self, master):
        self.master = master
        self.master.title("AD5940 - Plotter & Biometría")
        self.master.geometry("900x700")

        # Variables de estado
        self.puerto_serial = None
        self.conectado = False
        self.hilo_lectura = None
        self.evento_detener = threading.Event()
        self.sistema_biometrico = SistemaBiometrico()
        self.ocupado = False

        # Datos para graficar
        self.frecuencias_plot = []
        self.magnitudes_plot = []
        self.fases_plot = []

        self.crear_interfaz()

    def crear_interfaz(self):
        estilo = ttk.Style()
        if 'clam' in estilo.theme_names():
            estilo.theme_use('clam')

        self.var_estado = tk.StringVar(value="Listo")

        # --- Panel Superior (Conexión) ---
        marco_conexion = ttk.LabelFrame(self.master, text="Conexión Serial", padding="10")
        marco_conexion.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        ttk.Label(marco_conexion, text="Puerto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_puertos = ttk.Combobox(marco_conexion, width=20)
        self.combo_puertos.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(marco_conexion, text="↻ Actualizar", command=self.actualizar_puertos).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(marco_conexion, text="Baud Rate:").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.entrada_baud = ttk.Entry(marco_conexion, width=15)
        self.entrada_baud.insert(0, "115200")
        self.entrada_baud.grid(row=0, column=4, padx=5, pady=5)

        self.btn_conectar = ttk.Button(marco_conexion, text="Conectar", command=self.conectar_serial)
        self.btn_conectar.grid(row=0, column=5, padx=10, pady=5)

        self.btn_desconectar = ttk.Button(marco_conexion, text="Desconectar", command=self.desconectar_serial, state=tk.DISABLED)
        self.btn_desconectar.grid(row=0, column=6, padx=5, pady=5)
        
        self.actualizar_puertos()

        # --- Sistema de Pestañas ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(side=tk.TOP, fill="both", expand=True, padx=10, pady=5)

        # Pestaña 1: Plotter BIA
        self.pestaña_plotter = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_plotter, text="Gráficos (Plotter)")
        self.configurar_pestaña_plotter()

        # Pestaña 2: Biometría
        self.pestaña_biometria = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_biometria, text="Sistema Biométrico")
        self.configurar_pestaña_biometria()

        # --- Barra de Estado ---
        barra_estado = ttk.Label(self.master, textvariable=self.var_estado, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        barra_estado.pack(side=tk.BOTTOM, fill=tk.X)

    def configurar_pestaña_plotter(self):
        marco_controles = ttk.Frame(self.pestaña_plotter, padding="5")
        marco_controles.pack(side=tk.TOP, fill="x")

        self.btn_iniciar_plot = ttk.Button(marco_controles, text="▶ Iniciar Adquisición", command=self.iniciar_adquisicion_plot, state=tk.DISABLED)
        self.btn_iniciar_plot.pack(side=tk.LEFT, padx=5)

        self.btn_limpiar_plot = ttk.Button(marco_controles, text="✖ Limpiar Gráfico", command=self.limpiar_grafico)
        self.btn_limpiar_plot.pack(side=tk.LEFT, padx=5)

        self.btn_guardar_csv = ttk.Button(marco_controles, text="💾 Guardar CSV", command=self.guardar_csv)
        self.btn_guardar_csv.pack(side=tk.LEFT, padx=5)

        # Gráficos
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 5))
        self.fig.suptitle("Datos BIA AD5940", fontsize=14, fontweight='bold')
        self.fig.tight_layout(pad=3.0)

        self.linea_mag, = self.ax1.plot([], [], 'r-o', label='Magnitud (Ohm)', linewidth=2, markersize=4)
        self.ax1.set_ylabel('Magnitud (Ohm)', fontweight='bold')
        self.ax1.set_xscale('log')
        self.ax1.grid(True, which="both", ls="--", alpha=0.5)
        self.ax1.legend()

        self.linea_fase, = self.ax2.plot([], [], 'b-o', label='Fase (Grados)', linewidth=2, markersize=4)
        self.ax2.set_xlabel('Frecuencia (Hz)', fontweight='bold')
        self.ax2.set_ylabel('Fase (Grados)', fontweight='bold')
        self.ax2.set_xscale('log')
        self.ax2.grid(True, which="both", ls="--", alpha=0.5)
        self.ax2.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.pestaña_plotter)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.pestaña_plotter)
        self.toolbar.update()

    def configurar_pestaña_biometria(self):
        # Marco Principal
        marco_izq = ttk.Frame(self.pestaña_biometria, padding="10")
        marco_izq.pack(side=tk.LEFT, fill="y")
        
        marco_der = ttk.Frame(self.pestaña_biometria, padding="10")
        marco_der.pack(side=tk.LEFT, fill="both", expand=True)

        # Controles Uso Diario
        marco_diario = ttk.LabelFrame(marco_izq, text="Uso Diario", padding="10")
        marco_diario.pack(side=tk.TOP, fill="x", pady=5)
        
        self.btn_identificar = ttk.Button(marco_diario, text="🔍 Identificar Usuario", command=self.iniciar_identificacion, state=tk.DISABLED)
        self.btn_identificar.pack(fill="x", pady=10)

        # Panel Administrador
        marco_admin = ttk.LabelFrame(marco_izq, text="Panel de Administrador", padding="10")
        marco_admin.pack(side=tk.TOP, fill="x", pady=10)

        self.btn_registrar = ttk.Button(marco_admin, text="➕ Registrar Nuevo Usuario", command=self.iniciar_registro, state=tk.DISABLED)
        self.btn_registrar.pack(fill="x", pady=5)
        
        self.lbl_usuarios = ttk.Label(marco_admin, text=f"Usuarios: 0/{MAX_USUARIOS}")
        self.lbl_usuarios.pack(pady=5)

        # Consola de Salida
        ttk.Label(marco_der, text="Consola de Sistema:").pack(anchor=tk.W)
        self.consola = scrolledtext.ScrolledText(marco_der, wrap=tk.WORD, width=50, height=20, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.consola.pack(fill="both", expand=True)
        self.log_consola("Sistema Biométrico Inicializado.\nEsperando conexión serial...")

    # --- FUNCIONES DE INTERFAZ ---
    def set_estado(self, msg):
        self.master.after(0, lambda: self.var_estado.set(msg))

    def log_consola(self, msg):
        self.master.after(0, self._escribir_consola, msg)
        
    def _escribir_consola(self, msg):
        self.consola.insert(tk.END, msg + "\n")
        self.consola.see(tk.END)

    def actualizar_puertos(self):
        puertos = serial.tools.list_ports.comports()
        lista_puertos = [p.device for p in puertos]
        self.combo_puertos['values'] = lista_puertos
        if lista_puertos:
            pto_sugerido = next((p for p in lista_puertos if "ACM" in p or "USB" in p or "COM" in p), lista_puertos[0])
            self.combo_puertos.set(pto_sugerido)
        else:
            self.combo_puertos.set("")

    # --- COMUNICACIÓN SERIAL ---
    def conectar_serial(self):
        pto = self.combo_puertos.get()
        baud = self.entrada_baud.get()
        try:
            self.puerto_serial = serial.Serial(pto, int(baud), timeout=1)
            time.sleep(1.5) # Esperar a que la placa se asiente tras DTR toggle
            self.puerto_serial.reset_input_buffer()
            self.conectado = True
            
            # Actualizar botones
            self.btn_conectar.config(state=tk.DISABLED)
            self.btn_desconectar.config(state=tk.NORMAL)
            self.btn_iniciar_plot.config(state=tk.NORMAL)
            self.btn_identificar.config(state=tk.NORMAL)
            self.btn_registrar.config(state=tk.NORMAL)
            
            self.set_estado(f"Conectado a {pto} a {baud} bps")
            self.log_consola(f"Conexión exitosa a {pto}.")
        except Exception as e:
            messagebox.showerror("Error de Conexión", str(e))
            self.set_estado("Error al conectar.")

    def desconectar_serial(self):
        if self.puerto_serial and self.puerto_serial.is_open:
            self.evento_detener.set()
            if self.hilo_lectura and self.hilo_lectura.is_alive():
                self.hilo_lectura.join(timeout=2)
            self.puerto_serial.close()
            
        self.conectado = False
        self.btn_conectar.config(state=tk.NORMAL)
        self.btn_desconectar.config(state=tk.DISABLED)
        self.btn_iniciar_plot.config(state=tk.DISABLED)
        self.btn_identificar.config(state=tk.DISABLED)
        self.btn_registrar.config(state=tk.DISABLED)
        self.set_estado("Desconectado.")
        self.log_consola("Desconectado del puerto serial.")

    # --- LÓGICA DE ADQUISICIÓN UNIFICADA ---
    def realizar_barrido(self):
        """Envía el comando, lee los datos y devuelve las listas de barrido."""
        self.puerto_serial.reset_input_buffer()
        self.puerto_serial.write(b"send\n")
        self.puerto_serial.flush()
        
        frecuencias, magnitudes, fases = [], [], []
        puntos_leidos = 0
        MAX_PUNTOS = 48 # Límite de seguridad
        
        while not self.evento_detener.is_set():
            linea = self.puerto_serial.readline().decode('utf-8', errors='ignore').strip()
            
            if linea == "END_SWEEP" or puntos_leidos >= MAX_PUNTOS:
                if len(frecuencias) > 0:
                    break
                else:
                    if linea == "END_SWEEP": break
                    continue
            if not linea:
                continue
                
            try:
                datos = [float(x) for x in linea.split(',')]
                if len(datos) >= 3:
                    frecuencias.append(datos[0])
                    magnitudes.append(datos[1])
                    # Normalizar fase entre -180 y 180
                    fase_norm = ((datos[2] + 180) % 360) - 180
                    fases.append(fase_norm)
                    puntos_leidos += 1
            except ValueError:
                pass # Ignorar líneas malformadas
                
        return frecuencias, magnitudes, fases

    def hilo_operacion_serial(self, modo, repeticiones=1, nombre=""):
        try:
            self.ocupado = True
            self.master.after(0, lambda: self.set_botones_estado(tk.DISABLED))
            
            lista_barridos_features = []

            for i in range(repeticiones):
                if self.evento_detener.is_set(): break
                
                if modo == "registro":
                    self.log_consola(f"  -> Capturando barrido {i+1}/{repeticiones}...")
                else:
                    self.set_estado("Adquiriendo datos...")

                f, m, p = self.realizar_barrido()

                if modo == "plot":
                    self.frecuencias_plot, self.magnitudes_plot, self.fases_plot = f, m, p
                    self.master.after(0, self.actualizar_grafico)
                    self.set_estado("Adquisición completada.")
                    
                elif modo == "identificacion":
                    self.log_consola("Barrido completado. Analizando...")
                    features = self.sistema_biometrico.calcular_caracteristicas(f, m, p)
                    if features:
                        exito, msg = self.sistema_biometrico.identificar_usuario(features)
                        self.log_consola(msg)
                    else:
                        self.log_consola("[-] Error: No se pudieron extraer características.")
                        
                elif modo == "registro":
                    features = self.sistema_biometrico.calcular_caracteristicas(f, m, p)
                    if features:
                        lista_barridos_features.append(features)
                    time.sleep(0.5)

            # Post-procesamiento para registro
            if modo == "registro" and len(lista_barridos_features) == repeticiones:
                exito, msg = self.sistema_biometrico.agregar_usuario(nombre, lista_barridos_features)
                self.log_consola(msg)
                self.master.after(0, self.actualizar_label_usuarios)

        except Exception as e:
            self.log_consola(f"Error en comunicación: {str(e)}")
        finally:
            self.ocupado = False
            self.master.after(0, lambda: self.set_botones_estado(tk.NORMAL))

    def set_botones_estado(self, estado):
        if not self.conectado: return
        self.btn_iniciar_plot.config(state=estado)
        self.btn_identificar.config(state=estado)
        self.btn_registrar.config(state=estado)

    # --- LÓGICA DE PLOTTER ---
    def iniciar_adquisicion_plot(self):
        if self.ocupado: return
        self.evento_detener.clear()
        self.hilo_lectura = threading.Thread(target=self.hilo_operacion_serial, args=("plot",))
        self.hilo_lectura.daemon = True
        self.hilo_lectura.start()

    def actualizar_grafico(self):
        self.linea_mag.set_data(self.frecuencias_plot, self.magnitudes_plot)
        self.linea_fase.set_data(self.frecuencias_plot, self.fases_plot)

        if self.frecuencias_plot:
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            lim_min, lim_max = min(self.frecuencias_plot) * 0.9, max(self.frecuencias_plot) * 1.1
            self.ax1.set_xlim(lim_min, lim_max)
            self.ax2.set_xlim(lim_min, lim_max)

        self.canvas.draw_idle()

    def limpiar_grafico(self):
        self.frecuencias_plot, self.magnitudes_plot, self.fases_plot = [], [], []
        self.actualizar_grafico()
        self.set_estado("Gráfico limpiado.")

    def guardar_csv(self):
        if not self.frecuencias_plot:
            messagebox.showwarning("Sin Datos", "No hay datos para guardar.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar Datos BIA")
        if ruta:
            try:
                with open(ruta, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Frecuencia (Hz)", "Magnitud (Ohm)", "Fase (Grados)"])
                    for fr, mg, ph in zip(self.frecuencias_plot, self.magnitudes_plot, self.fases_plot):
                        writer.writerow([fr, mg, ph])
                self.set_estado(f"Guardado en {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al guardar: {e}")

    # --- LÓGICA DE BIOMETRÍA ---
    def iniciar_identificacion(self):
        if self.ocupado: return
        if not self.sistema_biometrico.modelo_entrenado:
            messagebox.showwarning("Atención", "El sistema no tiene usuarios registrados.")
            return
            
        self.log_consola("\n--- IDENTIFICACIÓN ---")
        self.log_consola("Mantenga el brazo quieto. Adquiriendo datos...")
        self.evento_detener.clear()
        self.hilo_lectura = threading.Thread(target=self.hilo_operacion_serial, args=("identificacion",))
        self.hilo_lectura.daemon = True
        self.hilo_lectura.start()

    def iniciar_registro(self):
        if self.ocupado: return
        
        # Validación de Administrador
        psw = simpledialog.askstring("Panel Admin", "Ingrese la contraseña de administrador:", show='*')
        if psw != PASSWORD_ADMIN:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta.")
            return

        if len(self.sistema_biometrico.usuarios_registrados) >= MAX_USUARIOS:
            messagebox.showinfo("Límite Alcanzado", f"Se ha alcanzado el límite de {MAX_USUARIOS} usuarios.")
            return

        nombre = simpledialog.askstring("Nuevo Usuario", "Ingrese el nombre del usuario:")
        if not nombre: return # Cancelado o vacío

        messagebox.showinfo("Instrucciones", "Se tomarán 5 mediciones. Por favor, póngase la pulsera y no se mueva hasta que termine el proceso.")
        
        self.log_consola(f"\n--- REGISTRANDO: {nombre} ---")
        self.evento_detener.clear()
        self.hilo_lectura = threading.Thread(target=self.hilo_operacion_serial, args=("registro", 5, nombre))
        self.hilo_lectura.daemon = True
        self.hilo_lectura.start()

    def actualizar_label_usuarios(self):
        num_usuarios = len(self.sistema_biometrico.usuarios_registrados)
        self.lbl_usuarios.config(text=f"Usuarios: {num_usuarios}/{MAX_USUARIOS}")

    def al_cerrar(self):
        self.desconectar_serial()
        self.master.destroy()
        plt.close(self.fig)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppBioimpedancia(root)
    root.protocol("WM_DELETE_WINDOW", app.al_cerrar)
    root.mainloop()