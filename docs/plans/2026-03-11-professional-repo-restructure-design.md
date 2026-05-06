# Professional Embedded Project Structure — Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reorganizar el repo ad5940_zephyr como ejemplo profesional para alumnos, y crear un repo template que puedan clonar para sus proyectos.

**Architecture:** Dos entregables: (1) este repo reorganizado con documentación real del proyecto AD5940 BIA, y (2) una carpeta `project-template/` con plantillas vacías y guías de workflow. Ambos usan terminología Zephyr/Nordic real.

**Tech Stack:** Zephyr RTOS, nRF Connect SDK, GitHub, Markdown

---

## Task 1: Actualizar .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1:** Añadir entradas estándar para Zephyr/embedded:

```gitignore
# editors
*.swp
*~
.vscode/
*.code-workspace

# OS
.DS_Store
Thumbs.db

# build
/build*/

# Python
__pycache__/
*.pyc
```

**Step 2: Commit**
```bash
git add .gitignore
git commit -m "Update .gitignore with standard entries for Zephyr projects"
```

---

## Task 2: Reorganizar código fuente — mover ad5940/ dentro de src/

**Files:**
- Move: `ad5940/*` → `src/ad5940/`
- Modify: `CMakeLists.txt` (actualizar rutas)

**Step 1:** Mover archivos:
```bash
mv ad5940/ src/ad5940/
```

**Step 2:** Actualizar CMakeLists.txt — cambiar rutas de `ad5940/` a `src/ad5940/`:
```cmake
cmake_minimum_required(VERSION 3.20.0)
set(DTC_OVERLAY_FILE "${CMAKE_CURRENT_SOURCE_DIR}/boards/nrf5340dk_nrf5340_cpuapp_ns.overlay")
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(ad5940_bia)

target_sources(app PRIVATE
    src/main.c
    src/ad5940/ad5940.c
    src/ad5940/BodyImpedance.c
    src/ad5940/AD5940Main.c
    src/ad5940/ZephyrPort.c
)

target_include_directories(app PRIVATE src/ad5940)
```

**Step 3: Commit**
```bash
git add -A
git commit -m "Reorganize source: move ad5940/ into src/ad5940/"
```

---

## Task 3: Mover docs de referencia del curso a llm-context/

**Files:**
- Move: `docs/*.md` (excepto porting-guide.md) → `llm-context/`
- Create: `llm-context/README.md`

**Step 1:** Mover los 7 archivos grandes del curso de Nordic:
```bash
mkdir -p llm-context
mv docs/Bluetooth-LE-Complete-Guide.md llm-context/
mv docs/Bootloaders-and-Firmware-Updates.md llm-context/
mv docs/Debugging-and-Development-Tools.md llm-context/
mv docs/Device-Drivers-and-GPIO.md llm-context/
mv docs/Hardware-Peripherals-and-Communication.md llm-context/
mv docs/Multithreading-and-RTOS.md llm-context/
mv docs/nRF-Connect-SDK-Fundamentals.md llm-context/
```

**Step 2:** Crear `llm-context/README.md`:
```markdown
# LLM Context Files

These files are reference material from the Nordic DevAcademy course.
They are NOT project documentation — they exist so that AI assistants
(Claude, Copilot, etc.) have context about Zephyr RTOS and nRF Connect SDK
when helping with development.

These files should not be modified as part of normal project work.
```

**Step 3: Commit**
```bash
git add -A
git commit -m "Move Nordic course reference docs to llm-context/"
```

---

## Task 4: Escribir README.md del proyecto ejemplo

**Files:**
- Create: `README.md`

**Step 1:** Escribir README profesional con:
- Título y descripción breve del proyecto
- Diagrama de bloques HW (ASCII)
- Requisitos (nRF Connect SDK version, board)
- Instrucciones de build y flash
- Estructura del repositorio explicada
- Link a docs/

El contenido completo se escribe en el paso de implementación.

**Step 2: Commit**
```bash
git add README.md
git commit -m "Add professional README with build instructions and project overview"
```

---

## Task 5: Escribir docs/PRD.md del proyecto ejemplo

**Files:**
- Create: `docs/PRD.md`

**Step 1:** Escribir un PRD real para el proyecto AD5940 BIA con:
- Objetivo del proyecto
- Requisitos funcionales (RF-001...) usando terminología Zephyr
- Requisitos no funcionales (RNF-001...)
- Restricciones
- Criterios de aceptación
- Fuera de alcance

Este documento sirve como ejemplo real de lo que los alumnos deben producir.

**Step 2: Commit**
```bash
git add docs/PRD.md
git commit -m "Add PRD document for AD5940 BIA project"
```

---

## Task 6: Escribir docs/architecture.md del proyecto ejemplo

**Files:**
- Create: `docs/architecture.md`

**Step 1:** Escribir documento de arquitectura real con:
- Diagrama de bloques HW (nRF5340 ↔ AD5940 ↔ Debug Console)
- Diagrama de bloques SW (5 capas con terminología Zephyr)
- Hardware Setup: overlay y prj.conf explicados
- Driver / Port Layer: ZephyrPort.c y por qué CS manual
- Application Logic: AD5940Main.c y BodyImpedance.c
- Decisiones de diseño (ADRs): por qué SPIM2, por qué 1MHz, etc.
- Mapeo de archivos a capas

**Step 2: Commit**
```bash
git add docs/architecture.md
git commit -m "Add architecture document with Zephyr layer diagrams"
```

---

## Task 7: Mover y mejorar porting-guide.md

**Files:**
- Move: `docs/porting-guide.md` (ya está en docs/, solo verificar)

El porting-guide.md ya existe y está bien escrito. Solo asegurar que está en `docs/` (ya lo está).

**Step 1: No requiere cambios.** Ya está en la ubicación correcta.

---

## Task 8: Crear project-template/ con toda la estructura para alumnos

**Files:**
- Create: `project-template/` (directorio completo)

### Estructura:
```
project-template/
├── CMakeLists.txt
├── prj.conf
├── README.md
├── .gitignore
├── boards/
│   └── nrf5340dk_nrf5340_cpuapp.overlay
├── src/
│   └── main.c
├── docs/
│   ├── PRD.md                    (plantilla)
│   ├── architecture.md           (plantilla)
│   ├── designs/
│   │   └── 000-template.md       (plantilla de design doc)
│   ├── verification/
│   │   └── .gitkeep
│   └── images/
│       └── .gitkeep
├── llm-context/
│   └── README.md
├── scripts/
│   └── .gitkeep
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── feature.md
        └── bug.md
```

Cada archivo se detalla en sub-steps en la implementación.

**Step 2: Commit**
```bash
git add project-template/
git commit -m "Add project template with all student templates and guides"
```

---

## Task 9: Escribir WORKFLOW.md en el template

**Files:**
- Create: `project-template/docs/WORKFLOW.md`

**Step 1:** Escribir la guía completa de flujo de trabajo con:
1. Desarrollo por capas (no sprints), con terminología Zephyr
2. Ciclo por bloque: Design Doc → Implementación → Verificación → PR
3. Reglas de Git (GitHub Flow, branch naming, commits, PRs)
4. Gestión de tareas con GitHub Issues + Project Board
5. Hitos de entrega sugeridos
6. Convenciones y ejemplos concretos

**Step 2: Commit**
```bash
git add project-template/docs/WORKFLOW.md
git commit -m "Add workflow guide for embedded development process"
```

---

## Task 10: Limpieza final

**Step 1:** Eliminar `.DS_Store` del tracking:
```bash
git rm --cached .DS_Store
```

**Step 2:** Verificar que todo compila (si hay entorno Zephyr disponible):
```bash
west build -b nrf5340dk/nrf5340/cpuapp/ns
```

**Step 3: Commit final**
```bash
git add -A
git commit -m "Clean up tracked files and verify build"
```
