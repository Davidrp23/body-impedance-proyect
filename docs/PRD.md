# PRD: Medicion de Bioimpedancia con AD5940 sobre nRF5340 DK

**Proyecto:** `ad5940_bia`
**Plataforma:** nRF5340 DK (cpuapp) + AD5940 Eval Board
**SDK:** nRF Connect SDK con Zephyr RTOS
**Fecha:** 2026-03-11

---

## 1. Objetivo del proyecto

Desarrollar una aplicacion embebida sobre Zephyr RTOS que realice mediciones de bioimpedancia (BIA) utilizando el chip AD5940 de Analog Devices conectado por SPI al nRF5340 DK. El sistema ejecuta un barrido de frecuencia logaritmico de 4 kHz a 198 kHz, midiendo magnitud y fase de la impedancia en cada punto. Los resultados se transmiten por consola UART para su visualizacion y analisis.

---

## 2. Requisitos Funcionales

| ID     | Requisito | Detalle |
|--------|-----------|---------|
| RF-001 | Comunicacion SPI con AD5940 usando Zephyr SPI API | Utilizar `spi_transceive()` sobre SPIM2 (`&spi2` en devicetree) a 1 MHz. Configuracion: `SPI_WORD_SET(8) \| SPI_TRANSFER_MSB`. |
| RF-002 | Control manual de CS, RST e INT via Zephyr GPIO API | CS en `P1.12` (ACTIVE_LOW), RST en `P0.07` (ACTIVE_LOW), INT en `P1.04` (ACTIVE_LOW, PULL_UP). Pines definidos en el devicetree overlay como nodos `cs_pin`, `rst_pin`, `int_pin` bajo `ad5940_gpios`. CS incluye delay post-asercion de 100 us para wake de hibernate. |
| RF-003 | Barrido de frecuencia configurable | Rango por defecto: 4 kHz a 198 kHz. Numero de puntos configurable (por defecto 48). Escala logaritmica (`SweepLog = bTRUE`). Parametros modificables via variables `cfgSweepStart`, `cfgSweepStop`, `cfgSweepPoints`. |
| RF-004 | Medicion de impedancia (magnitud y fase) | Para cada punto de frecuencia, el AD5940 ejecuta una DFT de 8192 puntos sobre la senal muestreada. Se miden dos canales: corriente (RCAL) y voltaje (Rz). El firmware calcula magnitud (Ohm) y fase (radianes, convertida a grados para salida). |
| RF-005 | Salida de resultados por UART console | Cada punto se imprime con formato: `"%.2f Hz %.2f Ohm %.2f deg"`. Se usa `printk()` a traves de la macro `DEBUG_PRINT`. La consola UART esta habilitada con `CONFIG_UART_CONSOLE=y`. |
| RF-006 | Ciclo autonomo de medicion | Secuencia: WUPT trigger -> wake AD5940 -> ejecutar secuencia de medicion (SEQID_0) -> escribir resultado DFT al FIFO -> entrar a hibernate (`AD5940_EnterSleepS()`). El MCU detecta datos via interrupcion GPIO (GP0, flanco activo) y lee el FIFO. |
| RF-007 | Calibracion RTIA por frecuencia | Antes de iniciar mediciones, el sistema calibra la RTIA del HSTIA para cada punto de frecuencia del barrido. Los valores calibrados (magnitud y fase) se almacenan en `RtiaCalTable[48][2]` y se aplican al calcular la impedancia. |
| RF-008 | Inicializacion de hardware AD5940 | Secuencia de inicio: hardware reset -> configuracion de clocks (HFOSC 16 MHz, LFOSC 32 kHz) -> FIFO (4 KB, fuente DFT, threshold 4) -> interrupciones (INTC0: FIFO threshold, INTC1: all) -> GPIOs del AD5940 (GP0 como INT). |
| RF-009 | Almacenamiento temporal de resultados | Los puntos medidos se almacenan en un buffer global `g_measurement_buffer[48]` de tipo `MeasurementPoint` (frecuencia, magnitud, fase) para procesamiento posterior. |
| RF-010 | Shutdown del AD5940 al finalizar | Al completar el barrido, el firmware detiene el WUPT (`AD5940_WUPTCtrl(bFALSE)`) y ejecuta `AD5940_ShutDownS()` para poner el chip en modo hibernate. |

---

## 3. Requisitos No Funcionales

| ID      | Requisito | Especificacion |
|---------|-----------|----------------|
| RNF-001 | Frecuencia SPI | 1 MHz. Se usa SPIM2 (periferico simple) en lugar de SPIM4 porque SPIM4 se deshabilita en el overlay. SPIM2 no soporta DMA de alta velocidad, limitando la frecuencia maxima practica. |
| RNF-002 | Precision de medicion | Error menor al 5% comparado con impedancia conocida (resistor de referencia). Rcal = 10 kOhm. |
| RNF-003 | Tamano de stack | Main thread: `CONFIG_MAIN_STACK_SIZE=8192` bytes. System workqueue: `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=4096` bytes. |
| RNF-004 | Consumo energetico | El AD5940 entra en modo hibernate entre cada ciclo de medicion. El secuenciador interno ejecuta `AD5940_EnterSleepS()` al final de cada secuencia de medicion. El MCU usa `k_usleep(100)` en el loop de polling. |
| RNF-005 | Resolucion DFT | 8192 puntos (`DFTNUM_8192`), fuente SINC3 (`DFTSRC_SINC3`), ventana de Hanning habilitada. |
| RNF-006 | Tasa de muestreo | ODR = 20 Hz (configurable). Limitada por la duracion de la secuencia de medicion. El firmware calcula `MaxODR` y ajusta automaticamente si el ODR solicitado excede el maximo. |
| RNF-007 | Soporte de punto flotante | `CONFIG_FPU=y` habilitado. Se usa Newlib con soporte de `float` en `printf` (`CONFIG_NEWLIB_LIBC_FLOAT_PRINTF=y`). |
| RNF-008 | Tiempo de inicio | Delay de 3 segundos al arranque (`k_msleep(3000)`) para permitir conexion del terminal serial antes de la primera salida. |

---

## 4. Restricciones

| # | Restriccion | Descripcion |
|---|-------------|-------------|
| 1 | Hardware | nRF5340 DK (PCA10095) conectado a AD5940 evaluation board via header Arduino. Pinout fijo: SCK=P1.15, MOSI=P1.13, MISO=P1.14, CS=P1.12, INT=P1.04, RST=P0.07. |
| 2 | SDK | nRF Connect SDK con Zephyr RTOS. Build system CMake con `find_package(Zephyr)`. Board target: `nrf5340dk/nrf5340/cpuapp`. |
| 3 | Vendor library | El archivo `ad5940.c` y `ad5940.h` son la libreria propietaria de Analog Devices y no se modifican. Solo se implementan las 7+2 funciones de plataforma en `ZephyrPort.c`. |
| 4 | Maximo de puntos de barrido | 100 puntos (`MAXSWEEP_POINTS`), limitado por el tamano de `RtiaCalTable` en SRAM. Valor por defecto: 48 puntos. |
| 5 | Memoria SRAM del AD5940 | 2 KB para secuenciador (`SEQMEMSIZE_2KB`), 4 KB para FIFO de datos (`FIFOSIZE_4KB`). Total 6 KB de SRAM interna del AD5940. |
| 6 | Modo de potencia | Modo low-power (`AFEPWR_LP`) del AFE. Ancho de banda limitado a 250 kHz (`AFEBW_250KHZ`). |

---

## 5. Criterios de aceptacion

| # | Criterio | Verificacion |
|---|----------|--------------|
| CA-001 | El sistema detecta el AD5940 al arranque | `AD5940_MCUResourceInit()` retorna 0 y se imprime `"SPI device ready"` en consola. |
| CA-002 | Se completa un barrido completo de 48 puntos | Se imprimen exactamente 48 lineas con formato `"%.2f Hz %.2f Ohm %.2f deg"`, cubriendo frecuencias desde ~4 kHz hasta ~198 kHz. |
| CA-003 | Los valores de magnitud son fisicamente razonables | Para una carga resistiva conocida de 1 kOhm, la magnitud medida esta entre 950 y 1050 Ohm (error < 5%) en todo el rango de frecuencia. |
| CA-004 | La fase es consistente con la carga | Para una carga puramente resistiva, la fase medida esta entre -5 y +5 grados en todas las frecuencias. |
| CA-005 | El AD5940 entra en hibernate al finalizar | Despues de completar el barrido, se imprime `"AD5940 shutdown - chip in hibernation"`. No se observan mas interrupciones GP0. |
| CA-006 | No hay errores de SPI durante la ejecucion | No se imprime ningun mensaje `"SPI err:"` durante todo el ciclo de medicion. |
| CA-007 | La calibracion RTIA se ejecuta correctamente | Se calibran los 48 puntos de frecuencia antes de iniciar el barrido de medicion, sin errores. |
| CA-008 | El firmware compila sin warnings | `west build` completa sin warnings en los archivos del proyecto (excluyendo vendor library `ad5940.c`). |

---

## 6. Fuera de alcance

Los siguientes elementos **no** forman parte de esta version del proyecto:

- **Bluetooth Low Energy (BLE):** No se transmiten datos por BLE. La salida es exclusivamente por UART.
- **Aplicacion movil:** No hay app companion para recibir o visualizar datos.
- **Almacenamiento persistente:** Los datos no se guardan en flash, SD card, ni ningun medio no volatil.
- **Soporte multi-sensor:** Solo se soporta un AD5940 conectado por SPI.
- **Interfaz de usuario:** No hay botones, LEDs indicadores, ni pantalla. La interaccion es unicamente por terminal serial.
- **Procesamiento avanzado de datos:** No se realiza calculo de composicion corporal (agua, grasa, musculo). Solo se reportan magnitud y fase crudos.
- **Over-the-air updates (DFU/OTA):** No se implementa actualizacion de firmware remota.
- **Configuracion en tiempo de ejecucion:** Los parametros del barrido se definen en tiempo de compilacion. No hay shell ni comandos para cambiarlos dinamicamente.
