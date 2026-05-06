# [Nombre del Proyecto]

[Descripción breve del proyecto en 2-3 oraciones. Qué hace, qué hardware usa, qué problema resuelve.]

## Equipo

| Nombre          | Rol                  | GitHub          |
|-----------------|----------------------|-----------------|
| [Nombre]        | [Rol]                | @usuario        |
| [Nombre]        | [Rol]                | @usuario        |
| [Nombre]        | [Rol]                | @usuario        |
| [Nombre]        | [Rol]                | @usuario        |

## Requisitos previos

- **nRF Connect SDK** v2.x instalado ([guía de instalación](https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/installation.html))
- **VS Code** con la extensión **nRF Connect for VS Code**
- **nRF5340 DK** (placa de desarrollo)
- Cable USB para conexión y alimentación de la placa

## Compilar y flashear

1. Abrir el proyecto en VS Code con la extensión nRF Connect.

2. Compilar desde la terminal:
   ```bash
   west build -b nrf5340dk/nrf5340/cpuapp
   ```

3. Flashear al dispositivo:
   ```bash
   west flash
   ```

4. Ver logs del serial:
   ```bash
   # Opción 1: nRF Connect Serial Terminal en VS Code
   # Opción 2: desde la terminal
   minicom -D /dev/ttyACM0 -b 115200
   ```

## Estructura del repositorio

```
├── src/              ← Código fuente
├── boards/           ← Devicetree overlays (.overlay)
├── docs/
│   ├── PRD.md        ← Requisitos del proyecto
│   ├── architecture.md ← Diseño del sistema
│   ├── designs/      ← Design docs por bloque
│   ├── verification/ ← Evidencia de pruebas
│   └── WORKFLOW.md   ← Flujo de trabajo del equipo
├── llm-context/      ← Documentación de referencia para IA
├── scripts/          ← Scripts de utilidad
├── prj.conf          ← Configuración Kconfig
├── CMakeLists.txt    ← Build system
└── .github/          ← Templates de PR e issues
```

## Documentación

- [PRD - Requisitos del proyecto](docs/PRD.md)
- [Arquitectura del sistema](docs/architecture.md)
- [Flujo de trabajo](docs/WORKFLOW.md)

## Flujo de trabajo

Este proyecto sigue el flujo de trabajo descrito en [docs/WORKFLOW.md](docs/WORKFLOW.md).
Cada bloque de funcionalidad pasa por: **Design Doc** -> **Implementación** -> **Verificación** -> **Pull Request**.
