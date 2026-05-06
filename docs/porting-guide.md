# Cómo portar la librería AD5940 a una plataforma nueva (Zephyr + nRF5340)

## Arquitectura del código del AD5940

Analog Devices estructura el código del AD5940 en capas:

```
┌─────────────────────────────────────┐
│  AD5940Main.c                       │  ← Tu aplicación (configurar, lanzar, procesar)
│  BodyImpedance.c                    │  ← Lógica BIA del fabricante (secuencias, calibración)
├─────────────────────────────────────┤
│  ad5940.c / ad5940.h                │  ← Librería core del fabricante (registros, secuenciador)
├─────────────────────────────────────┤
│  ZephyrPort.c                       │  ← LO ÚNICO QUE PORTAS
└─────────────────────────────────────┘
         │
         ▼
   Hardware SPI + GPIOs
```

**Regla fundamental:** solo se toca la capa inferior. `ad5940.c` y `BodyImpedance.c` no deberían modificarse (salvo bugs). Todo el port consiste en implementar las funciones de plataforma en un archivo nuevo.

## Qué es el Port.c

El AD5940 necesita **7+2 funciones** que tú implementas. La librería (`ad5940.c`) las llama pero no sabe nada de tu hardware. Es un patrón de abstracción HAL (Hardware Abstraction Layer):

```c
// Comunicación SPI
void AD5940_ReadWriteNBytes(unsigned char *pSend, unsigned char *pRecv, unsigned long len);
void AD5940_CsClr(void);    // assert CS (chip select bajo)
void AD5940_CsSet(void);    // de-assert CS (chip select alto)

// Reset
void AD5940_RstClr(void);   // assert reset (pin bajo)
void AD5940_RstSet(void);   // de-assert reset (pin alto)

// Timing
void AD5940_Delay10us(uint32_t time);  // delay en múltiplos de 10µs

// Interrupciones
uint32_t AD5940_GetMCUIntFlag(void);   // ¿hay interrupción pendiente?
uint32_t AD5940_ClrMCUIntFlag(void);   // limpiar flag

// + Init de recursos
uint32_t AD5940_MCUResourceInit(void); // configurar SPI, GPIOs, interrupción
```

Eso es todo. Si implementas esas funciones correctamente, el resto del código del fabricante funciona sin tocarlo.

## Cómo se implementa cada función en Zephyr

### SPI

En Zephyr, SPI se maneja con la API `drivers/spi.h`. Se obtiene el device del devicetree y se usa `spi_transceive()`:

```c
static const struct device *spi_dev = DEVICE_DT_GET(DT_NODELABEL(spi2));

static const struct spi_config spi_cfg = {
    .frequency  = 1000000,
    .operation  = SPI_WORD_SET(8) | SPI_TRANSFER_MSB,
};

void AD5940_ReadWriteNBytes(unsigned char *pSend, unsigned char *pRecv, unsigned long len)
{
    // Zephyr necesita buffers no-NULL, usar dummies si es necesario
    struct spi_buf tx_buf = { .buf = pSend ? pSend : dummy_tx, .len = len };
    struct spi_buf rx_buf = { .buf = pRecv ? pRecv : dummy_rx, .len = len };
    // ... spi_transceive(spi_dev, &spi_cfg, &tx_set, &rx_set);
}
```

**Detalle importante:** La librería del AD5940 a veces llama con `pSend=NULL` o `pRecv=NULL`. El driver SPI de Zephyr necesita buffers válidos siempre, por eso usamos buffers dummy.

### CS manual (por qué no usar el CS automático de Zephyr)

La mayoría de sensores SPI hacen una transferencia por ciclo CS. Zephyr puede manejar esto automáticamente con `cs-gpios` en el devicetree:

```dts
/* Ejemplo NORMAL de SPI con CS automático (NO aplica al AD5940) */
&spi2 {
    cs-gpios = <&gpio1 12 GPIO_ACTIVE_LOW>;
    mi_sensor: mi_sensor@0 {
        reg = <0>;
        spi-max-frequency = <1000000>;
    };
};
```

Con el AD5940 **no se puede hacer esto**. La librería `ad5940.c` hace múltiples transferencias SPI dentro de un mismo ciclo CS. Por ejemplo, para leer un registro:

```
CS LOW                          ← CsClr()
  SPI: enviar SPICMD_SETADDR    ← Write8B
  SPI: enviar dirección          ← Write16B
CS HIGH                         ← CsSet()

CS LOW                          ← CsClr()
  SPI: enviar SPICMD_READREG    ← Write8B
  SPI: leer dato                 ← Read16B o Read32B
CS HIGH                         ← CsSet()
```

Son **4 llamadas SPI** agrupadas en **2 ciclos CS**. Si Zephyr manejara CS automáticamente, haría CS LOW/HIGH en **cada** `spi_transceive()` (4 ciclos CS en vez de 2). El AD5940 no entendería el protocolo.

Por eso:
- Quitamos `cs-gpios` del devicetree (`/delete-property/ cs-gpios`)
- Definimos CS como GPIO manual aparte
- La librería lo controla con `CsClr()`/`CsSet()` que nosotros implementamos en el Port.c

### GPIOs

En Zephyr, los GPIOs se definen en el overlay del devicetree y se acceden con `gpio_dt_spec`:

```c
static const struct gpio_dt_spec cs_gpio = GPIO_DT_SPEC_GET(DT_NODELABEL(cs_pin), gpios);

void AD5940_CsClr(void) {
    k_busy_wait(50);
    gpio_pin_set_dt(&cs_gpio, 1);   // logical 1 = pin LOW (ACTIVE_LOW)
    k_busy_wait(100);               // delay para wake de hibernate
}
```

**Cuidado con ACTIVE_LOW:** En el overlay definimos los GPIOs como `GPIO_ACTIVE_LOW`. Eso significa que `gpio_pin_set_dt(&pin, 1)` pone el pin a LOW físicamente. Es contraintuitivo pero es la convención de Zephyr: trabajas con lógica (1=activo, 0=inactivo) y el flag `ACTIVE_LOW` invierte la polaridad.

### Interrupción

El AD5940 genera una interrupción en su pin GP0 cuando hay datos listos (FIFO threshold). En el MCU, conectamos ese pin a una GPIO con interrupción:

```c
static volatile uint8_t ucInterrupted;

static void gp0int_isr(const struct device *dev, struct gpio_callback *cb, uint32_t pins) {
    ucInterrupted = 1;  // solo poner flag, no procesar en ISR
}

// En MCUResourceInit:
gpio_pin_configure_dt(&int_gpio, GPIO_INPUT);
gpio_pin_interrupt_configure_dt(&int_gpio, GPIO_INT_EDGE_TO_ACTIVE);
gpio_init_callback(&int_cb_data, gp0int_isr, BIT(int_gpio.pin));
gpio_add_callback(int_gpio.port, &int_cb_data);
```

El patrón es: la ISR pone un flag, el main loop lo lee y procesa. Nunca hacer SPI dentro de una ISR.

## El overlay del devicetree

Es donde definimos qué periférico SPI usar y qué pines para CS, RST e INT:

```dts
&spi2 {
    compatible = "nordic,nrf-spim";
    status = "okay";
    pinctrl-0 = <&spi2_default>;     // SCK=P1.15, MOSI=P1.13, MISO=P1.14
    /delete-property/ cs-gpios;       // CS manual, no automático
};

/ {
    ad5940_gpios {
        compatible = "gpio-leds";     // truco: reusa el binding de LEDs
        cs_pin: cs_pin {
            gpios = <&gpio1 12 GPIO_ACTIVE_LOW>;
        };
        rst_pin: rst_pin {
            gpios = <&gpio0 7 GPIO_ACTIVE_LOW>;
        };
        int_pin: int_pin {
            gpios = <&gpio1 4 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>;
        };
    };
};
```

**Por qué SPIM2 y no SPIM4:** En el nRF5340, SPIM4 tiene un DMA avanzado (EasyDMA con listas) que daba problemas con las transferencias pequeñas (1-4 bytes) que hace la librería constantemente. SPIM2 es más simple y funciona bien a 1MHz.

## Qué archivos se tocan y cuáles no

| Archivo | ¿Se toca? | Qué se hace |
|---------|-----------|-------------|
| `ZephyrPort.c` | **Sí — es el port** | Implementar las 7+2 funciones |
| `ad5940.c` | **No** (salvo bugs) | Librería del fabricante, no tocar |
| `ad5940.h` | **Mínimo** | Añadir declaración de `AD5940_ReadGP0Pin` |
| `BodyImpedance.c` | **Mínimo** | Solo si hay bugs (INTC restore, EnterSleepS) |
| `AD5940Main.c` | **Sí** | Tu aplicación: configurar parámetros, procesar datos |
| `boards/*.overlay` | **Sí** | Definir pines SPI y GPIOs para tu placa |
| `prj.conf` | **Sí** | Habilitar SPI, GPIO, FPU, serial, etc. |

## El ciclo de medición (hay que entenderlo para no romperlo)

```
   WUPT despierta chip
         │
         ▼
   Secuenciador ejecuta medición
         │
         ▼
   Resultado va a FIFO
         │
         ▼
   FIFO alcanza threshold → GP0 interrupt
         │
         ▼
   EnterSleepS → chip hiberna  ← el secuenciador hace esto
         │
         ▼
   WUPT cuenta sleep timer (SOLO en hibernate)
         │
         ▼
   Vuelve al inicio
```

En paralelo, el MCU:
1. Detecta interrupción (flag)
2. Despierta chip con `WakeUp()` (CS LOW lo saca de hibernate)
3. `SLPKEY_LOCK` — evitar que hiberne mientras leemos
4. Lee FIFO
5. `SLPKEY_UNLOCK` + `EnterSleepS` — devolver chip a hibernate
6. Procesa datos

**Lo crítico:** si no devuelves el chip a hibernate (paso 5), el WUPT no avanza y la siguiente medición no se dispara.

## Cambios necesarios respecto al código original del fabricante

### 1. Delay post-CS de 100µs en `CsClr()` (ZephyrPort.c)

```c
void AD5940_CsClr(void)
{
    k_busy_wait(50);   // inter-CS delay
    gpio_pin_set_dt(&cs_gpio, 1);  // assert CS
    k_busy_wait(100);  // post-assertion delay
}
```

**Por qué:** El AD5940 hiberna entre mediciones para ahorrar energía. Cuando CS baja, el chip se despierta, pero necesita 14-40µs antes de poder procesar SPI. El port original (ADuCM3029) no necesita este delay porque su SPI corre a 13MHz+ y el overhead del loop de `WakeUp()` ya da suficiente tiempo. Con Zephyr a 1MHz, sin el delay el primer byte SPI se cloquea antes de que el chip esté listo.

### 2. `EnterSleepS()` en el ISR tras leer FIFO (BodyImpedance.c)

```c
// Después de leer FIFO:
AD5940_SleepKeyCtrlS(SLPKEY_UNLOCK);
AD5940_EnterSleepS();
```

**Por qué:** El timer de sleep del WUPT **solo cuenta cuando el chip está en hibernate**. Si después de leer FIFO no ponemos el chip a dormir, el WUPT no avanza y la siguiente medición no se dispara.

### 3. Restaurar INTC tras calibración (BodyImpedance.c)

```c
AppBIARtiaCal();
AppBIACfg.ReDoRtiaCal = bFALSE;
AD5940_INTCCfg(AFEINTC_1, AFEINTSRC_ALLINT, bTRUE);
AD5940_INTCCfg(AFEINTC_0, AFEINTSRC_DATAFIFOTHRESH, bTRUE);
```

**Por qué:** Medida defensiva. `HSRtiaCal` hace read-modify-write sobre los registros del controlador de interrupciones. Si alguna lectura SPI falla (glitch, ruido), corrompe la configuración y GP0 nunca dispara interrupción. Estas 2 escrituras SPI cuestan ~0 y previenen un bug difícil de diagnosticar.

### 4. Fix de buffer overflow en `Read16B` / `Read32B` (ad5940.c)

```c
// Original tenía RecvBuffer[2] pero llamaba con length=3
uint8_t RecvBuffer[3];
AD5940_ReadWriteNBytes(NULL, RecvBuffer, 3);
```

**Por qué:** Bug preexistente en la librería de Analog Devices. El buffer era más pequeño que el tamaño de la transferencia SPI. En el ADuCM3029 funcionaba por suerte (lo que había en el stack no se corrompía de forma visible). En nRF5340 con Zephyr, la corrupción de stack puede causar crashes.

## Debugging: caso real y lecciones aprendidas

### Qué pasó

Durante el desarrollo, el AD5940 mostraba síntomas erráticos: lecturas SPI devolvían 0xFFFF o 0x0000, la calibración se colgaba, el chip dejaba de responder tras iniciar mediciones. Se fueron acumulando workarounds (delays entre bytes SPI, retry loops, polling de GPIOs como backup) que "mejoraban algo" pero nunca resolvían el problema.

**La causa raíz era un jumper faltante en la evaluation board.** Sin alimentación correcta, ninguna solución software iba a funcionar. Una vez puesto el jumper, se quitaron todos los workarounds y el código funcionó limpio.

### Cómo hay que hacerlo

**1. Verificar lo físico primero (siempre)**
- ¿Hay alimentación? ¿Se enciende algún LED?
- ¿Los cables/jumpers están bien?
- ¿El voltaje es correcto? (medir con multímetro)
- Con el analizador lógico: ¿MISO responde o está flotando?

Si MISO está a 0xFF constante, el chip no está respondiendo. No es un problema de software.

**2. Validar la comunicación básica antes de complicar**
- Leer CHIPID (registro conocido, valor fijo: 0x5502)
- Si no lee bien, NO seguir adelante. El problema es de conexión/alimentación
- No añadir retries como solución — los retries esconden el problema

**3. Un cambio a la vez**
- Cambiar una sola cosa, probar, confirmar
- Si funciona: commit y siguiente
- Si no funciona: revertir y probar otra cosa
- Nunca acumular 5 cambios sin saber cuál fue el que arregló

**4. Distinguir workaround de fix**
- **Workaround:** "si reintento 100 veces funciona" → estás escondiendo el problema
- **Fix:** "el chip necesita 40µs para despertar de hibernate y no se los estoy dando" → estás resolviendo la causa

**5. Cuando nada tiene sentido, volver a lo físico**
- Si el software parece correcto pero nada funciona, el problema casi seguro es hardware
- Revisar alimentación, conexiones, jumpers, soldaduras
- Un osciloscopio o analizador lógico es imprescindible

## Resumen

1. **Solo se porta el Port.c** — implementar 7+2 funciones para tu plataforma
2. **CS es manual** — la librería lo controla, no Zephyr
3. **El chip hiberna entre mediciones** — CS LOW lo despierta, necesita ~40µs de delay
4. **ACTIVE_LOW en Zephyr** — logical 1 = pin LOW, cuidado con esto
5. **Verificar hardware primero** — alimentación, jumpers, señales con osciloscopio ANTES de tocar software
6. **No tocar ad5940.c** — si algo no funciona, el problema está en el port o en el hardware, no en la librería del fabricante
