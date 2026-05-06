# Arquitectura del Sistema

## Diagrama de bloques hardware

<!--
Dibujar un diagrama ASCII que muestre:
- La placa principal (nRF5340 DK)
- Sensores y periféricos externos
- Conexiones físicas (SPI, I2C, GPIO, UART)
- Alimentación si es relevante

Ejemplo:
-->

```
┌─────────────────┐          SPI           ┌──────────────┐
│                 │  MOSI (P1.13) -------> │              │
│   nRF5340 DK    │  MISO (P1.14) <------- │   [Sensor]   │
│   (cpuapp)      │  SCLK (P1.15) -------> │              │
│                 │  CS   (P1.12) -------> │              │
│                 │                         └──────────────┘
│                 │
│                 │  ~~~~ BLE ~~~~  📱 Móvil / PC
└─────────────────┘
```

<!-- Actualizar el diagrama con los pines y periféricos reales de tu proyecto -->

## Diagrama de bloques software

El software se organiza en 5 capas, desarrolladas de abajo hacia arriba:

### Capa 1: Hardware Setup

**Devicetree overlay** (`.overlay`) + **Kconfig** (`prj.conf`)

<!-- ¿Qué periféricos necesitas habilitar? ¿SPI, I2C, GPIO, ADC? -->
<!-- ¿Qué pines vas a usar? ¿Necesitas reasignar pines por defecto? -->
<!-- ¿Qué CONFIG_ necesitas activar en prj.conf? -->

- Archivos: `boards/nrf5340dk_nrf5340_cpuapp.overlay`, `prj.conf`
- Verificación: el proyecto compila, `device_is_ready()` retorna `true`

### Capa 2: Driver / Port Layer

**Zephyr APIs**: `spi_transceive()`, `gpio_pin_configure()`, `i2c_write()`, `adc_read()`, etc.

<!-- ¿Tu sensor tiene una librería propia del fabricante? -->
<!-- Si sí: ¿qué funciones de bajo nivel necesita que tú implementes (port layer)? -->
<!-- Si no: ¿qué registros necesitas leer/escribir directamente? -->

- Archivos: `src/sensor_port.c` (o equivalente)
- Verificación: puedo leer el chip ID o un registro conocido del sensor

### Capa 3: Application Logic

Configuración del sensor, lanzamiento de mediciones, procesamiento de datos.

<!-- ¿Qué secuencia de configuración necesita tu sensor? -->
<!-- ¿Qué datos produce y cómo los procesas? -->
<!-- ¿Necesitas calibración, filtrado, conversión de unidades? -->

- Archivos: `src/sensor_app.c` (o equivalente)
- Verificación: los datos leídos tienen sentido físico (rango esperado)

### Capa 4: Communication

BLE GATT Service, UART, USB, u otro protocolo de comunicación.

<!-- ¿Qué datos necesitas transmitir? ¿Con qué frecuencia? -->
<!-- ¿BLE? ¿Qué servicios y características GATT necesitas? -->
<!-- ¿UART para debug o como interfaz principal? -->

- Archivos: `src/ble_service.c` (o equivalente)
- Verificación: puedo enviar datos a otro dispositivo y recibirlos

### Capa 5: System Integration

Todo junto en `main.c`: inicialización, threads si se necesitan, manejo de errores.

<!-- ¿Necesitas threads separados? ¿Para qué? -->
<!-- ¿Cómo manejas errores? ¿Qué pasa si el sensor no responde? -->
<!-- ¿Necesitas timers periódicos? ¿Workqueue? -->

- Archivos: `src/main.c`
- Verificación: el sistema funciona de forma continua y estable

## Decisiones de diseño

<!--
Documentar aquí las decisiones técnicas importantes y su justificación.
Formato sugerido:

### DD-001: [Título de la decisión]
- **Contexto:** [situación que motivó la decisión]
- **Decisión:** [qué se decidió]
- **Alternativas consideradas:** [qué más se evaluó]
- **Justificación:** [por qué se eligió esta opción]
-->

### DD-001: [Título]
- **Contexto:**
- **Decisión:**
- **Alternativas consideradas:**
- **Justificación:**

## Mapeo de archivos a capas

| Archivo                        | Capa                | Descripción                          |
|--------------------------------|---------------------|--------------------------------------|
| `prj.conf`                     | Hardware Setup      | Configuración Kconfig                |
| `boards/*.overlay`             | Hardware Setup      | Devicetree overlay                   |
| `src/main.c`                   | System Integration  | Punto de entrada, inicialización     |
| `src/[driver].c`               | Driver / Port Layer | [Descripción]                        |
| `src/[app_logic].c`            | Application Logic   | [Descripción]                        |
| `src/[communication].c`        | Communication       | [Descripción]                        |
