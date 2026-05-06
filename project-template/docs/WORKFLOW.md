# Flujo de Trabajo

## 1. Visión general

Este documento describe el flujo de trabajo profesional para desarrollo de firmware embebido con Zephyr RTOS en el nRF5340 DK. Está basado en prácticas de la industria: Agile adaptado a sistemas embebidos, GitHub Flow para control de versiones, y Docs-as-Code para documentación técnica.

El objetivo es que el equipo trabaje de forma organizada, trazable y verificable -- igual que un equipo de ingeniería profesional.

## 2. Desarrollo por capas (no por sprints)

En firmware embebido, el software se desarrolla **de abajo hacia arriba**, capa por capa. Cada capa depende de que la anterior funcione correctamente. No tiene sentido intentar enviar datos por BLE si el driver del sensor no lee bien.

Las 5 capas son:

```
Capa 5: System Integration         ← Todo junto, threads, manejo de errores
         ▲
Capa 4: Communication              ← BLE, UART, USB
         ▲
Capa 3: Application Logic          ← Configurar sensor, procesar datos
         ▲
Capa 2: Driver / Port Layer        ← Zephyr APIs: SPI, I2C, GPIO, ADC
         ▲
Capa 1: Hardware Setup             ← Devicetree overlay + Kconfig (prj.conf)
```

### Capa 1: Hardware Setup

- **Qué se hace:** Configurar el Devicetree overlay (`.overlay`) y Kconfig (`prj.conf`) para que Zephyr reconozca el hardware conectado.
- **Pregunta clave:** "¿Mi placa reconoce el periférico? ¿SPI/I2C/GPIO están habilitados?"
- **Verificación:** El proyecto compila sin errores y `device_is_ready()` retorna `true` para cada periférico.

### Capa 2: Driver / Port Layer

- **Qué se hace:** Usar las APIs de Zephyr (`spi_transceive()`, `gpio_pin_configure()`, `i2c_write()`, etc.) para comunicarse con el hardware. Si el sensor trae una librería propia del fabricante, implementar un **port layer** que adapte las funciones de bajo nivel a las APIs de Zephyr.
- **Pregunta clave:** "¿Puedo leer el chip ID o un registro conocido del sensor?"
- **Verificación:** Se lee correctamente un valor conocido del sensor (ej: chip ID, registro WHO_AM_I).

### Capa 3: Application Logic

- **Qué se hace:** Configurar el sensor para el modo de operación deseado, lanzar mediciones y procesar los datos obtenidos.
- **Pregunta clave:** "¿Los datos leídos tienen sentido físico?"
- **Verificación:** Los valores medidos están dentro del rango esperado y son coherentes.

### Capa 4: Communication

- **Qué se hace:** Implementar BLE GATT service, UART, USB u otro protocolo para transmitir datos a otro dispositivo.
- **Pregunta clave:** "¿Puedo enviar datos y recibirlos en el otro extremo?"
- **Verificación:** Los datos transmitidos se reciben correctamente en el dispositivo receptor (móvil, PC, etc.).

### Capa 5: System Integration

- **Qué se hace:** Integrar todo en `main.c`, crear threads si se necesitan, implementar manejo de errores y asegurar estabilidad.
- **Pregunta clave:** "¿El sistema funciona de forma continua y estable?"
- **Verificación:** El sistema opera durante un periodo prolongado sin errores, crashes o memory leaks.

## 3. Ciclo de trabajo por bloque

Cada bloque de funcionalidad (dentro de una capa) sigue un ciclo de 4 pasos:

### a) Design Doc -- antes de escribir código

1. Crear `docs/designs/NNN-nombre.md` usando la plantilla (`docs/designs/000-template.md`).
2. Describir: qué hace el bloque, interfaz pública, dependencias del Devicetree y Kconfig, criterios de verificación.
3. Entregar el design doc como PR y revisarlo **antes** de empezar a codificar.

El design doc no tiene que ser largo. Media página está bien. Lo importante es pensar *antes* de codificar.

### b) Implementación

1. Crear una feature branch desde `main`: `feature/spi-driver`, `feature/ble-service`, etc.
2. Escribir commits descriptivos en inglés: `"Add SPI initialization for AD5940"`, `"Fix chip ID read returning zero"`.
3. El código debe compilar en cada commit. No hacer commits de código roto.

### c) Verificación

1. Ejecutar los criterios definidos en el design doc.
2. Capturar evidencia: copiar logs del serial terminal, fotos del setup, capturas de osciloscopio.
3. Guardar la evidencia en `docs/verification/NNN-nombre/` (ej: `docs/verification/001-spi-driver/`).

### d) Pull Request

1. Abrir PR usando el template (se carga automáticamente).
2. Referenciar el issue: `"Closes #12"`.
3. Incluir la evidencia de verificación en el PR o referenciar los archivos en `docs/verification/`.
4. Mínimo 1 review de un compañero del equipo.
5. Merge a `main` solo cuando el código compila y la verificación pasa.

### Ejemplo concreto

```
Bloque: SPI Driver
├── docs/designs/001-spi-driver.md        ← "Voy a hacer esto"
├── feature/spi-driver (branch)           ← Implementación
├── docs/verification/001-spi-driver/
│   └── spi-read-chip-id.log             ← "Funciona, mira"
└── PR #3: "Add SPI driver"              ← Review + merge a main
```

Secuencia temporal:

1. Abrir issue #2: "Implementar SPI driver para sensor X"
2. Crear `docs/designs/001-spi-driver.md`, abrir PR de design doc, revisarlo
3. Crear branch `feature/spi-driver`, implementar
4. Verificar: copiar logs a `docs/verification/001-spi-driver/`
5. Abrir PR #3 con evidencia, review de un compañero, merge

## 4. Reglas de Git

### Branching: GitHub Flow

- **`main` siempre compila.** Nadie hace push directo a `main`.
- Feature branches para cada bloque de trabajo:
  - `feature/spi-driver` -- funcionalidad nueva
  - `fix/spi-timeout` -- corrección de bug
  - `docs/prd-update` -- cambios en documentación

### Commits

- **En inglés**, descriptivos, en imperativo:
  - `"Add SPI initialization for AD5940"`
  - `"Fix chip ID read returning zero on first attempt"`
  - `"Update overlay with correct pin assignments"`
- **NO:**
  - `"fix stuff"`
  - `"wip"`
  - `"asdf"`
  - `"changes"`

### Pull Requests

- Todo cambio entra a `main` por Pull Request.
- Mínimo 1 review de un compañero.
- Usar el template de PR (se carga automáticamente desde `.github/PULL_REQUEST_TEMPLATE.md`).
- Incluir evidencia de verificación en hardware real.

### Branch Protection (configurar en GitHub)

Configurar en: **Settings -> Branches -> Add rule** para la branch `main`:

- [x] Require a pull request before merging
- [x] Require approvals: 1
- [ ] (Opcional) Require status checks to pass

## 5. Gestión de tareas con GitHub Issues

### Crear issues

- Crear **un issue por cada bloque de trabajo** (no por cada archivo o función).
- Usar los templates de issue (feature o bug) que están en `.github/ISSUE_TEMPLATE/`.
- Cada issue debe indicar la **capa del sistema** a la que pertenece.

### Labels recomendados

Crear estos labels en el repositorio (Settings -> Labels):

| Label            | Color   | Descripción                          |
|------------------|---------|--------------------------------------|
| `hardware-setup` | #0E8A16 | Capa 1: Devicetree, Kconfig         |
| `driver`         | #1D76DB | Capa 2: Driver / Port Layer         |
| `app-logic`      | #5319E7 | Capa 3: Application Logic           |
| `communication`  | #FBCA04 | Capa 4: BLE, UART, USB              |
| `integration`    | #D93F0B | Capa 5: System Integration          |
| `docs`           | #0075CA | Documentación                        |
| `bug`            | #D73A4A | Algo no funciona                     |
| `enhancement`    | #A2EEEF | Mejora                               |

### Asignación

- Cada issue se asigna a una persona del equipo.
- Si un bloque es grande, dividirlo en sub-issues.

### GitHub Projects (Kanban)

Usar **GitHub Projects** para visualizar el progreso:

1. Ir a la pestaña **Projects** del repositorio.
2. Crear un nuevo proyecto con vista **Board** (Kanban).
3. Columnas: **To Do** -> **In Progress** -> **In Review** -> **Done**
4. Mover los issues según avanzan.

## 6. Hitos de entrega

| Hito | Entregable                             | Qué se evalúa                              |
|------|----------------------------------------|---------------------------------------------|
| H1   | PRD + Arquitectura + Issues creados    | Planificación y documentación               |
| H2   | Capas 1-2 funcionando                  | Comunicación con hardware + driver          |
| H3   | Capas 3-4 funcionando                  | Lógica de aplicación + comunicación         |
| H4   | Integración + demo final              | Sistema completo + presentación             |

Cada hito se entrega con:

- Código funcionando en `main` (merged via PRs).
- Design docs en `docs/designs/`.
- Evidencia de verificación en `docs/verification/`.
- Issues cerrados y PRs mergeados.

## 7. Estructura del repositorio

```
├── src/              ← Código fuente (.c, .h)
├── boards/           ← Devicetree overlays (.overlay)
├── docs/
│   ├── PRD.md        ← Requisitos del proyecto
│   ├── architecture.md ← Diseño del sistema por capas
│   ├── designs/      ← Design docs por bloque (antes de codificar)
│   ├── verification/ ← Evidencia de pruebas (logs, fotos)
│   ├── images/       ← Imágenes para documentación
│   └── WORKFLOW.md   ← Este documento
├── llm-context/      ← Documentación de referencia para asistentes IA
├── scripts/          ← Scripts de utilidad (build, flash, test)
├── prj.conf          ← Configuración Kconfig del proyecto
├── CMakeLists.txt    ← Configuración del build system
└── .github/          ← Templates de PR e issues
```

### Dónde va cada cosa

| Tipo de archivo              | Ubicación                         |
|------------------------------|-----------------------------------|
| Código fuente                | `src/`                            |
| Devicetree overlays          | `boards/`                         |
| Configuración Kconfig        | `prj.conf` (raíz)                |
| Requisitos del proyecto      | `docs/PRD.md`                     |
| Arquitectura                 | `docs/architecture.md`            |
| Design docs                  | `docs/designs/NNN-nombre.md`      |
| Evidencia de verificación    | `docs/verification/NNN-nombre/`   |
| Datasheets y docs para IA    | `llm-context/`                    |
| Scripts de utilidad          | `scripts/`                        |
| Templates de GitHub          | `.github/`                        |

## 8. Uso de IA

Se permite y se fomenta el uso de asistentes de IA (Claude, GitHub Copilot, ChatGPT, etc.) como herramienta de desarrollo.

### Cómo usarla efectivamente

- **Poner documentación de referencia en `llm-context/`**: datasheets del sensor, guías de Nordic DevAcademy, extractos de la documentación de Zephyr. Cuanta más referencia tenga la IA, mejores respuestas dará.
- **Dar contexto específico**: en vez de "ayúdame con SPI", decir "necesito configurar SPI en Zephyr para el nRF5340 DK, conectando al sensor AD5940 en los pines P1.12-P1.15".
- **Pedir explicaciones**: si la IA genera código, pedirle que explique qué hace cada parte.

### Reglas

- **La IA es un asistente, no un sustituto.** El alumno debe entender lo que el código hace. En la revisión de PR, un compañero puede preguntar "¿por qué usaste `k_msleep` aquí y no un timer?" y hay que saber responder.
- **Los commits son del alumno.** No se trata de hacer copy-paste sin entender. Si usas IA para generar código, revísalo, entiéndelo y adáptalo.
- **La verificación en hardware real no se puede delegar.** La IA puede sugerir código, pero solo tú puedes confirmar que funciona en la placa.
