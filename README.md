# AD5940 Body Impedance Analysis (BIA) on nRF5340 DK

This project demonstrates how to interface the Analog Devices AD5940 high-precision impedance analyzer with a Nordic nRF5340 DK using Zephyr RTOS over SPI. It performs Body Impedance Analysis (BIA) measurements and outputs results over UART.

Built as a reference example for university embedded-systems courses.

## Hardware Setup

```
    nRF5340 DK (Arduino Header)              AD5940 Eval Board
   ┌──────────────────────────┐             ┌─────────────────┐
   │                          │             │                 │
   │  D13 (P1.15) SCK  ──────┼─────────────┼── SCK           │
   │  D11 (P1.13) MOSI ──────┼─────────────┼── MOSI          │
   │  D12 (P1.14) MISO ──────┼─────────────┼── MISO          │
   │  D10 (P1.12) CS   ──────┼─────────────┼── CS            │
   │  D2  (P1.04) INT  ──────┼─────────────┼── GP0 (INT)     │
   │       P0.07  RST  ──────┼─────────────┼── RESET         │
   │                          │             │                 │
   │  GND ────────────────────┼─────────────┼── GND           │
   │  VDD (3.3V) ────────────┼─────────────┼── VDD           │
   │                          │             │                 │
   └──────────────────────────┘             └─────────────────┘
```

### Pin Connections

| Function | nRF5340 Pin | Arduino Header | AD5940 Pin | Notes               |
|----------|-------------|----------------|------------|----------------------|
| SCK      | P1.15       | D13            | SCK        | SPI clock            |
| MOSI     | P1.13       | D11            | MOSI       | SPI data out         |
| MISO     | P1.14       | D12            | MISO       | SPI data in          |
| CS       | P1.12       | D10            | CS         | Manual GPIO, active low |
| INT      | P1.04       | D2             | GP0        | Interrupt, active low, pull-up |
| RST      | P0.07       | --             | RESET      | Active low           |
| GND      | GND         | GND            | GND        | Common ground        |
| VDD      | 3.3 V       | 3V3            | VDD        | Power supply         |

SPI uses the SPIM2 peripheral (not SPIM4). Chip select is driven manually via GPIO rather than through the SPI controller.

## Prerequisites

- **nRF Connect SDK** (v2.5.0 or later) with Zephyr RTOS
- **west** meta-tool (installed as part of the nRF Connect SDK)
- **nRF5340 DK** development board
- **AD5940** or **ADuCM355** evaluation board
- A USB cable for programming and UART console output

## Build and Flash

1. Set up the nRF Connect SDK environment (see [Nordic's installation guide](https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/installation.html)).

2. Build the project:

   ```bash
   west build -b nrf5340dk/nrf5340/cpuapp
   ```

3. Flash the firmware:

   ```bash
   west flash
   ```

4. Open a serial terminal (115200 baud) to see measurement output:

   ```bash
   # Example using minicom
   minicom -D /dev/ttyACM0 -b 115200
   ```

To build for the non-secure target (with TF-M), use the `nrf5340dk/nrf5340/cpuapp/ns` board target instead. The corresponding device tree overlay is selected automatically via `CMakeLists.txt`.

## Repository Structure

```
├── CMakeLists.txt              Build configuration
├── prj.conf                    Kconfig options (SPI, GPIO, logging, FPU)
├── boards/                     Device tree overlays for nRF5340 DK
├── src/
│   ├── main.c                  Entry point: initializes AD5940 and runs BIA loop
│   └── ad5940/
│       ├── ZephyrPort.c        Platform port: SPI, GPIO, delay, interrupt
│       ├── AD5940Main.c        Application-level init and measurement sequencing
│       ├── BodyImpedance.c     BIA algorithm configuration and result processing
│       ├── ad5940.c / ad5940.h Vendor library (Analog Devices)
│       └── ...                 Additional vendor headers
├── docs/                       Project documentation
│   ├── PRD.md                  Product requirements document
│   ├── architecture.md         System architecture and data flow
│   └── porting-guide.md        Guide for porting AD5940 to new platforms
├── project-template/           Starter template for student assignments
└── llm-context/                Nordic course material (reference for AI tools)
```

For detailed design documentation, see:

- [docs/porting-guide.md](docs/porting-guide.md) -- How to port the AD5940 library to a new Zephyr-based platform.
- [docs/PRD.md](docs/PRD.md) -- Product requirements and project scope.
- [docs/architecture.md](docs/architecture.md) -- System architecture, component interactions, and data flow.

## Student Template

The `project-template/` directory contains a stripped-down version of this project intended as a starting point for course assignments. It includes the build scaffolding and vendor library but leaves the port layer and application logic for students to implement.

## License

See individual source files for license information. The AD5940 library files are provided by Analog Devices.
