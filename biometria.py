import serial
import numpy as np
from sklearn.naive_bayes import GaussianNB
import getpass
import time

# --- CONFIGURACIONES GLOBALES ---
PUERTO_SERIAL = '/dev/ttyACM1'  # Cambiar por el puerto correcto (ej. /dev/ttyACM0 en Mac/Linux)
BAUD_RATE = 115200      # Debe coincidir con la placa Nordic
PASSWORD_ADMIN = "nordic123"
MAX_USUARIOS = 5        # Límite máximo para mantener alta precisión
UMBRAL_CONFIANZA = 0.85 # 85% de seguridad mínima para autorizar el acceso

# --- FUNCIONES DE LECTURA Y EXTRACCIÓN DE CARACTERÍSTICAS ---
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
    
    # Ajuste lineal (regresión) para obtener las pendientes (slope) y las intersecciones (intercept)
    slope_mag, int_mag = np.polyfit(log_freq, log_mag, 1)
    slope_R, int_R = np.polyfit(log_freq, log_R, 1)
    slope_X, int_X = np.polyfit(log_freq, log_X, 1)
    
    return [max_mag, slope_mag, int_mag, slope_R, int_R, slope_X, int_X]

def iniciar_y_leer_barrido(ser):
    """
    Envía el comando de inicio ('S') a la placa y luego lee los datos.
    """
    # 1. SINCRONIZACIÓN: Envía la letra 'S' a la placa Nordic para que inicie la medición
    ser.write(b'send\n')
    ser.flush()
    
    frecuencias, magnitudes, fases = [], [], []
    
    # 2. LECTURA: Espera los datos hasta recibir 'END_SWEEP'
    while True:
        # errors='ignore' evita cierres inesperados si la placa envía basura por el cable
        linea = ser.readline().decode('utf-8', errors='ignore').strip()
        
        if linea == "END_SWEEP":
            if len(frecuencias) > 0:
                break
            else:
                continue
                
        try:
            f, m, p = linea.split(',')
            frecuencias.append(float(f))
            magnitudes.append(float(m))
            fases.append(float(p))
        except ValueError:
            pass # Ignora las líneas que no estén en el formato "freq,mag,fase"
            
    return frecuencias, magnitudes, fases

# --- CLASE DEL SISTEMA BIOMÉTRICO ---
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
            print("\n[+] ¡Modelo actualizado con éxito!")
        else:
            print("\n[-] Ningún usuario en la base de datos.")

    def agregar_usuario(self, nombre, features_list):
        if len(self.usuarios_registrados) >= MAX_USUARIOS:
            print(f"\n[-] ERROR: Límite máximo de {MAX_USUARIOS} usuarios alcanzado.")
            return

        nuevo_id = len(self.usuarios_registrados)
        self.usuarios_registrados[nuevo_id] = nombre
        
        for features in features_list:
            self.dataset_features.append(features)
            self.dataset_labels.append(nuevo_id)
            
        print(f"\n[+] Usuario '{nombre}' agregado a la base de datos.")
        self.entrenar_modelo()

    def identificar_usuario(self, features_desconocidas):
        if not self.modelo_entrenado:
            print("\n[-] Sistema no configurado. Registre al menos un usuario.")
            return

        # Obtenemos las probabilidades para ver qué tan seguro está el modelo
        probabilidad = self.modelo_nb.predict_proba([features_desconocidas])[0]
        max_prob = np.max(probabilidad)
        id_estimado = np.argmax(probabilidad)

        print(f"\nAnálisis completado. Confianza máxima: {max_prob*100:.1f}%")

        # Lógica Anti-Intruso: si la confianza es muy baja, la persona no está registrada
        if max_prob >= UMBRAL_CONFIANZA:
            nombre_usuario = self.usuarios_registrados[id_estimado]
            print(f"[!] ACCESO AUTORIZADO: ¡Bienvenido, {nombre_usuario}!")
        else:
            print("[!] ACCESO DENEGADO: Usuario desconocido o intento fallido.")

# --- INTERFAZ DE USUARIO ---
def main():
    print("Conectando a la placa Nordic...")
    try:
        ser = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2) # Espera a que la placa se reinicie al abrir el puerto
        ser.reset_input_buffer() # Limpia datos viejos
        print("¡Conectado!\n")
    except serial.SerialException:
        print(f"ERROR: No se pudo abrir el puerto {PUERTO_SERIAL}. Verifica la conexión.")
        return

    sistema = SistemaBiometrico()
    
    while True:
        print("\n" + "="*30)
        print(" SISTEMA DE BIOIMPEDANCIA AD5940")
        print("="*30)
        print("1. Identificar Usuario (Uso Diario)")
        print("2. Panel de Administrador (Agregar Usuarios)")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            print("\nIniciando medición. Por favor, mantenga el brazo quieto...")
            frecuencias, magnitudes, fases = iniciar_y_leer_barrido(ser)
            features_desconocidas = calcular_caracteristicas(frecuencias, magnitudes, fases)
            sistema.identificar_usuario(features_desconocidas)

        elif opcion == '2':
            psw = getpass.getpass("Ingrese la contraseña de administrador: ")
            if psw == PASSWORD_ADMIN:
                print("\n--- PANEL DE ADMIN ---")
                print(f"Usuarios actuales: {len(sistema.usuarios_registrados)}/{MAX_USUARIOS}")
                print("1. Registrar nuevo usuario")
                print("2. Ver usuarios registrados")
                sub_opcion = input("Opción: ")

                if sub_opcion == '1':
                    if len(sistema.usuarios_registrados) >= MAX_USUARIOS:
                        print(f"\n[-] Límite de {MAX_USUARIOS} usuarios ya alcanzado.")
                    else:
                        nombre = input("Ingrese el nombre de la persona: ")
                        print("Recopilando 5 mediciones. Póngase la pulsera y no se mueva.")
                        sweep_list = []
                        for i in range(5):
                            print(f"  Enviando señal de inicio para barrido {i+1}/5...")
                            frecuencias, magnitudes, fases = iniciar_y_leer_barrido(ser)
                            features = calcular_caracteristicas(frecuencias, magnitudes, fases)
                            sweep_list.append(features)
                            time.sleep(0.5) # Pausa de medio segundo entre barridos
                        
                        sistema.agregar_usuario(nombre, sweep_list)
                        
                elif sub_opcion == '2':
                    print("\nUsuarios autorizados:")
                    for uid, unombre in sistema.usuarios_registrados.items():
                        print(f" - ID {uid}: {unombre}")
            else:
                print("\n[-] ¡Contraseña incorrecta!")

        elif opcion == '3':
            print("\nApagando el sistema...")
            ser.close()
            break
        else:
            print("\n[-] Opción no válida.")

if __name__ == "__main__":
    main()