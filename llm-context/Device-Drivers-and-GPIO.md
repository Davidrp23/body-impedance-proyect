# Device driver model

## Overview

A device driver is a combination of statically allocated structures maintained in the kernel that contain information about the device instance. Some of the device information that is worth mentioning is config, data, state, and an API to access the device-specific implementation of all the features supported for this specific device.

In this lesson, we will cover the device driver model, API, instances and implementation. Then we will take a look at the sensor driver API available in nRF Connect SDK, and how to add a custom sensor to it.

In the exercise section, we will use the BME280 sensor with the SPI interface that was used in Lesson 5. We will practice creating a custom driver for this sensor using the sensor driver API.

---

## Device driver model

The Zephyr RTOS that the nRF Connect SDK is based on provides a **device driver model**. This driver implementation is highly decoupled from its API, which allows developers to switch out the low-lever driver implementation without modifying the application on top, because we can use the same generic API.

This decoupling has many benefits, including a high level of portability, as it makes it possible to use the same code on different boards without manually modifying the underlying driver implementation.

> **Recall**: The Zephyr device driver model was also covered in Lesson 2 – Device driver model of the nRF Connect SDK Fundamentals course

The Zephyr device driver model is the architecture that defines the association between the generic APIs and the device driver implementations. We can split the model into three different sections, as shown in the image description below.

*(Diagram description: Application -> Device Driver API -> Device Driver Instances -> Device Driver Implementation -> Hardware)*

The three sub-categories for the device driver model are:

1.  **Device driver APIs:** High-level, hardware-agnostic functions (e.g., `gpio_pin_set()`, `spi_transceive()`, `sensor_sample_fetch()`). Defined in header files like `<zephyr/drivers/gpio.h>`.
2.  **Device driver instances:** Runtime representation of a specific hardware device (e.g., `&gpio0`, `&spi1`). Obtained via devicetree macros (`DEVICE_DT_GET()`, `GPIO_DT_SPEC_GET()`, etc.). Represented by `const struct device *`.
3.  **Device driver implementation:** Low-level, hardware-specific code that implements the functionality defined by the APIs for a particular peripheral. Linked to instances via the devicetree `compatible` property and driver registration macros.

The application interacts with the generic API. The API uses the device driver instance (device pointer) obtained from the devicetree to call the correct functions within the device driver implementation layer.

### Device driver implementation

When implementing a device driver, one needs to consider several key components, mostly centered around the driver's data structures.

#### Zephyr devices (`struct device`)

Zephyr devices are represented by `struct device`, defined in `<zephyr/device.h>`. This structure holds references to resources and information defined by the driver implementation.

Simplified `struct device`:
```c
struct device {
      const char *name;      // Device name (unique), from DT label property
      const void *config;    // Pointer to read-only config struct (from DT properties)
      void * const data;     // Pointer to runtime data struct (state, counters, etc.)
      const void *api;       // Pointer to the driver's API function struct
      // ... other internal kernel fields ...
};
```

#### Device definition

Devices are typically defined statically at compile time using macros:

*   `DEVICE_DEFINE()`: For non-devicetree devices (less common).
*   `DEVICE_DT_DEFINE()`: For devicetree-based devices, using node ID.
*   `DEVICE_DT_INST_DEFINE()`: For devicetree-based devices, using an instance number based on a `compatible`. **Most common for drivers supporting multiple instances.**

Devices defined this way are automatically initialized by the kernel during boot, before `main()` is called, based on init levels and priorities.

**Using `DEVICE_DT_INST_DEFINE()`:**

Instance-based macros rely on `DT_DRV_COMPAT` being defined *before* the macro call. Set `DT_DRV_COMPAT` to the lowercase-and-underscores version of the `compatible` string your driver supports.

Example: If your driver supports `compatible = "vendor,mysensor"`, define this at the top of your driver `.c` file:
```c
#define DT_DRV_COMPAT vendor_mysensor
```

A typical driver definition using instance macros looks like this:

```c
#include <zephyr/device.h>
#include <zephyr/drivers/spi.h> // Example dependency
// ... other includes ...

// Define compatible for this driver
#define DT_DRV_COMPAT vendor_mysensor

// Forward declarations for driver structs and functions
struct mysensor_config {
    struct spi_dt_spec spi; // Example: Store SPI config from DT
    // Other config...
};

struct mysensor_data {
    // Runtime data like sensor readings, state flags, etc.
    int reading;
};

static int mysensor_init(const struct device *dev);
// ... other driver API function implementations ...

// Define the driver's API function structure
static const struct sensor_driver_api mysensor_api_funcs = { // Using sensor API example
    // .sample_fetch = mysensor_sample_fetch,
    // .channel_get = mysensor_channel_get,
    // ... other API functions ...
};

// Macro to define one instance of the driver
#define MYSENSOR_DEFINE(inst)                                           \
    /* Define instance-specific data */                                 \
    static struct mysensor_data data_##inst;                            \
    /* Define instance-specific config, populated from Devicetree */    \
    static const struct mysensor_config config_##inst = {               \
        .spi = SPI_DT_SPEC_INST_GET(inst, SPI_OP_MODE_MASTER, 0),       \
        /* Get other DT properties: .some_prop = DT_INST_PROP(inst, some_prop), */ \
    };                                                                  \
                                                                        \
    /* Define the device instance */                                    \
    DEVICE_DT_INST_DEFINE(inst,                                         \
                          mysensor_init,        /* Init function */     \
                          NULL,                 /* PM handle (optional)*/ \
                          &data_##inst,         /* Data struct ptr */   \
                          &config_##inst,       /* Config struct ptr */ \
                          POST_KERNEL,          /* Init level */        \
                          CONFIG_SENSOR_INIT_PRIORITY, /* Init priority */ \
                          &mysensor_api_funcs); /* API struct ptr */

// Instantiate the driver for each enabled devicetree node with matching compatible
DT_INST_FOREACH_STATUS_OKAY(MYSENSOR_DEFINE)
```

*   `MYSENSOR_DEFINE(inst)`: A helper macro defining static data/config structs and calling `DEVICE_DT_INST_DEFINE` for a given instance `inst`.
*   `DEVICE_DT_INST_DEFINE()`: Registers the device instance with the kernel, linking the instance number (`inst`), init function, data, config, API struct, and init level/priority.
*   `DT_INST_FOREACH_STATUS_OKAY(MYSENSOR_DEFINE)`: This crucial macro expands the `MYSENSOR_DEFINE` macro for every devicetree node instance (`inst` = 0, 1, 2...) that has `compatible = "vendor,mysensor"` and `status = "okay"`.

#### Key components of a device driver

1.  **Configuration (`config` struct):** Holds read-only configuration data, often populated from devicetree properties during initialization. Pointed to by `dev->config`.
2.  **Runtime Data (`data` struct):** Holds variables that change during runtime (state, counters, buffers, etc.). Pointed to by `dev->data`.
3.  **Initialization Function (`init`):** Runs during kernel boot (before `main`). Sets up hardware, allocates resources, configures pins, registers interrupts. Defined via `DEVICE_DT..._DEFINE`. Uses `SYS_INIT()` internally.
4.  **Interrupt Handlers (ISRs):** Code executed when the hardware generates an interrupt. Registered during init. Should be fast; often defers work to threads (e.g., using workqueues).
5.  **Power Management (Optional):** Implements `struct pm_device_ops` and registers with `DEVICE_DT..._DEFINE` to participate in Zephyr's power management system (suspend/resume device state).
6.  **API Structure (`api` struct):** A struct containing function pointers that implement the standard driver API (e.g., `struct sensor_driver_api`, `struct gpio_driver_api`). Allows application code to call driver functions via the generic API headers. Pointed to by `dev->api`.

---

## Setting up a west workspace

### Application types

Based on location relative to the Zephyr west workspace and SDK repositories:

1.  **Repository Application:** Located *inside* the SDK source tree (e.g., `nrf/samples/`, `zephyr/samples/`).
    *(Diagram description: File structure showing app inside nrf/ or zephyr/)*
2.  **Freestanding Application:** Located *outside* the SDK workspace directory. Needs `$ZEPHYR_BASE` environment variable set or passed to CMake. (Examples: Nordic Developer Academy course exercises).
    *(Diagram description: File structure showing SDK and app in separate top-level folders)*
3.  **Workspace Application:** Located *inside* the west workspace directory, but *outside* the main SDK/Zephyr repositories (often in a sibling directory). Managed as part of the workspace.
    *(Diagram description: File structure showing app folder alongside nrf/, zephyr/)*

### Setting up a workspace application

Use `west` commands to manage workspaces.

*   **`west init`:** Creates a new workspace.
    *   From remote manifest: Clones the manifest repository (which lists projects like nrf, zephyr, modules, and potentially your application repo) and sets up the workspace structure.
        ```bash
        # Example: Initialize workspace using ncs-example-application manifest
        west init -m https://github.com/nrfconnect/ncs-example-application --mr main my-workspace
        cd my-workspace
        west update # Clones/updates projects listed in the manifest (nrf, zephyr, etc.)
        ```
    *   From local manifest: Creates a workspace around an existing local directory containing a `west.yml` manifest file.
        ```bash
        # Assume ncs-example-application is already cloned locally
        west init -l ncs-example-application
        # cd into the new workspace directory if needed
        # west update might still be needed depending on the state
        ```
*   **`west update`:** Clones or updates projects listed in the workspace's manifest file (`west.yml`) to their specified revisions.# Reading buttons and controlling LEDs

## Overview
In this lesson, we will examine how hardware is described in nRF Connect SDK, whether it is a development kit (DK), a System on Chip (SoC), a System in a Package (SiP) or a module. Interaction between applications and hardware is done through pieces of software called device drivers, and we will explain the device driver model used in nRF Connect SDK. We will use the General-Purpose Input/Output (GPIO) hardware peripheral and driver as a case study. We will do a line-by-line walkthrough of the blinky sample that we flashed on the board in the previous lesson.

In the exercise section of this lesson, we will learn how to use the GPIO peripheral to control LEDs and read the status of buttons using both polling and interrupts methods.

## Devicetree

*(Instructions corresponding to nRF Connect SDK v2.9.0)*

In Embedded Systems firmware development, hardware is traditionally described inside header files (`.h` or `.hh`). nRF Connect SDK uses a more structured and modular method to describe hardware borrowed from the Zephyr RTOS, which is through a construct called a **devicetree**.

A **devicetree** is a hierarchical data structure that describes hardware. The hardware described could be a development kit, SoC, SiP, module, defining everything ranging from the GPIO configurations of the LEDs on a development kit to the memory-mapped locations of peripherals. The devicetree uses a specific format consisting of nodes connected together, where each node contains a set of properties.

*The following section is derived from Zephyr's Devicetree documentation.*

### Devicetree basics

As the name indicates, a devicetree is a tree-like structure. The human-readable text format for this tree is called **DTS** (for devicetree source).

Here is an example DTS file:
```devicetree
/dts-v1/;
/ {
        a-node {
                subnode_label: a-sub-node {
                        foo = <3>;
                };
        };
};
```
The tree above has three nodes:
*   A root node: `/`
*   A node named `a-node`, which is a child of the root node
*   A node named `a-sub-node`, which is a child of `a-node`

Nodes can be given **labels**, which are unique shorthands that can be used to refer to the labeled node elsewhere in the devicetree. Above, `a-sub-node` has the label `subnode_label`. A node can have no, one, or multiple node labels.

Devicetree nodes can also have **properties**. Properties are name/value pairs. Property values can be an array of strings, bytes, numbers, or any mixture of types.

The node `a-sub-node` has a property named `foo`, whose value is a cell with value `3`. The size and type of `foo`‘s value are implied by the enclosing angle brackets (`<` and `>`) in the DTS. Properties might have an empty value if conveying true-false information. In this case, the presence or absence of the property is sufficiently descriptive.

Devicetree nodes have **paths** identifying their locations in the tree. Like Unix file system paths, devicetree paths are strings separated by slashes (`/`), and the root node’s path is a single slash: `/`. Otherwise, each node’s path is formed by concatenating the node’s ancestors’ names with the node’s own name, separated by slashes. For example, the full path to `a-sub-node` is `/a-node/a-sub-node`.

### Devicetree bindings (YAML files)

Devicetree **bindings** define the `compatible` property. It declares requirements on the contents of devicetree nodes, and provides semantic information about the contents of valid nodes. Zephyr’s devicetree bindings are defined as YAML files. Every devicetree node must have a `compatible` property. A devicetree node is matched using the `compatible` property with its definition in the devicetree binding.

Below is an example of a devicetree binding file (`.yaml`) that defines the `compatible` property named `nordic,nrf-sample` with one required property named `num-sample` of type integer.
```yaml
compatible: "nordic,nrf-sample"
properties:
  num-sample:
    type: int
    required: true
```
Below is a sample DTS file (`.dts`) with the node `node0` that is set to the `compatible` `nordic,nrf-sample`. This means the `node0` node must have the required property `num-sample` and that property must be assigned an integer value. Otherwise, the build will fail.
```devicetree
node0 {
     compatible = "nordic,nrf-sample";
     num-sample = <3>;
};
```
The devicetree bindings are shipped with the SDK in `<install_path>\zephyr\dts\bindings` (see [devicetree bindings for Nordic Semiconductor devices](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/dts/bindings/nordic/index.html)). In some situations, you define your own YAML files, such as when creating your custom driver. This is something covered in the nRF Connect SDK Intermediate course.

### Aliases

It is common to add aliases to the devicetree. The `/aliases` node contains properties that are aliases, where the name of the property is the name of that alias and the value of the property is a reference to a node in the device tree, see below.
```devicetree
/ {
        aliases {
                subnode_alias = &subnode_label;
        };
};
```
The code snippet above assigns the node `a-sub-node`, referenced by its label `subnode_label` to the alias `subnode_alias`. The purpose here is that your C/C++ application code (Ex: `main.c`) will use the alias. The definition of fixed aliases (Ex: `led0` for the first LED on a board) in boards’ dts files can make the application code more portable, as it can avoid hard-coding varying device node names and make the application code more flexible to changes in the board used.

### Accessing the devicetree

To get information about a particular devicetree node in your source code, you need a **node identifier** for it. This is just a C macro that refers to the node. There are many ways to get a node identifier.

The two common ones are by the node label through the macro `DT_NODELABEL()` and by an alias through the macro `DT_ALIAS()`.

For example, to get the node identifier of `a-sub-node`:
```c
DT_NODELABEL(subnode_label)
```
To get the value assigned to a certain devicetree property, we can use the macro `DT_PROP()`. For example, to get the value assigned to the `foo` property:
```c
DT_PROP(DT_NODELABEL(subnode_label), foo)
```

### Devicetree example

Let’s take an actual example to understand these concepts better. The **nRF52833 DK** has four user-configurable LEDs (with the PCB labeling LED1 – LED4) connected to GPIO pins `P0.13` – `P0.16` as shown in the screenshots below obtained from the schematics (available in Downloads -> Hardware Files on a development kit page) of the nRF52833 DK.

*(Description of external images: nRF52833 DK LED location and pin mapping)*

> **Information**
> The PCB labeling (“Silkscreen on PCB”) for the LEDs and buttons on the nRF54 Series DKs (f.ex nRF54L15 DK) now aligns with their definitions in the devicetree.
> For example, the PCB label “LED0” corresponds to the “led0” in devicetree. This is a change from our previous development kits, where “LED1” PCB labeling was used to refer to “led0” devicetree node.

#### DK devicetree file

These hardware details are all described in the devicetree file for the nRF52833 DK. Let’s examine this file, available in `<install_path>\zephyr\boards\nordic\nrf52833dk\nrf52833dk_nrf52833.dts`

The devicetree file for the DK includes the devicetree for the specific SoC variant used in the development kit. In the case of the nRF52833 DK, it is the file `nrf52833_qiaa.dtsi` available in the directory `<install_path>\zephyr\dts\arm\nordic`. This file is used because it corresponds to the package variant and function variant of the SoC used on the nRF52833 DK. The `I` in `DTSI` stands for Include. `dtsi` files generally contain SoC-level definitions. It also includes the pin mapping, defined in `nrf52833dk_nrf52833-pinctrl.dtsi`.

*   The LED1 (read the information note above) on the nRF52833 DK has the node name `led_0` and the node label `led0`. The node label is commonly used to refer to the node, like this `&led0`.
*   The `led_0` has two properties: `gpios` and `label`.
*   You can see that the property `gpios` is referencing the node `gpio0` through the `&` symbol. `gpio0` is defined in the SoC devicetree, as we will see in the following paragraph. The GPIO pin where LED1 on the kit is connected to the nRF52833 SoC is defined with `GPIO 0` as pin `13` (`P0.13`) and active low.

> **Important**
> A node usually has a node label, but it can also have a property with the name `label`. For instance, the node `led_0` has the node label `led0` and a property `label` with the value `"Green LED 0"`. In this context, the `label` property adds a Human readable string describing the LED. Using the `label` property (f.ex `"Green LED 0"`) to get a node identifier is deprecated and should not be used. Instead, to get a node identifier, the node label (`led0`) is recommended to be used.

The alias node is also defined in the DK devicetree file, see the image description below.

*(Description of original image: nRF52833 DK devicetree /aliases node)*

We can see from the `/aliases` node in the DK devicetree, that node `led_0`, referenced by its node label as `&led0`, is given the alias `led0`. This might sound redundant; however, it is here to make sure that all boards with LEDs nodes will have a constant alias for their LEDs (f.ex `led0` for the first LED) so that the application code (f.ex `main.c`) will compile on different boards, without the need for you to manually inspect the DTS files and figure out the node label used for the LEDs on different boards.

If we take a look at some of the other peripheral nodes, you will notice various `pinctrl` properties (defined in `<install_path>\zephyr\dts\bindings\pinctrl\pinctrl-device.yaml`). For example, `&uart0`, the node describing the UART0 peripheral has the properties `pinctrl-0`, `pinctrl-1` and `pinctrl-names`.

*(Description of original image: nRF52833 DK devicetree &uart0 node)*

This is based on Zephyr’s pin control and assigns specific pin configurations to the devicetree nodes through the `&pinctrl` node that is defined in the pin control devicetree file.

#### Pin control devicetree file

The devicetree file relies on the pin control devicetree file for the pin mappings of the various nodes (except for LEDs and buttons). As seen in the image description above, the `&uart0` node has references to the nodes `&uart0_default` and `&uart0_sleep`, which are defined in this file. The pin control devicetree file is found in `<install_path>\zephyr\boards\arm\nrf52833dk_nrf52833\nrf52833dk_nrf52833-pinctrl.dtsi`.

*   The `&pinctrl` node (defined in `<install_path>\zephyr\dts\bindings\pinctrl\nordic,nrf-pinctrl.yaml`) includes all device pin configurations in its sub-nodes.
*   The node `uart0_default` encodes the pin configurations for the default state of the UART0 peripheral. The pin control API lets you assign different pins to the peripherals based on states; the two standard states are `default` and `sleep`.
*   Pin configurations are organized in groups within each sub-node, where each group specifies a list of pin function selections in the `psels` property. The `group1` node is one of these groups, specifying the pin configurations for `UART_TX` and `UART_RTS`.
*   A group can also specify shared pin properties common to all specified pins. The `group2` node is specifying the pin configurations for `UART_RX` and `UART_CTS`, and setting the `bias-pull-up` property for both of them.

#### SoC variant devicetree file

Now, examine the SoC variant devicetree `nrf52833_qiaa.dtsi` available in the directory `<install_path>\zephyr\dts\arm\nordic`.

*(Description of original image: nRF52833 QIAA SoC variant devicetree)*

*   The SoC variant devicetree includes the base SoC devicetree `nrf52833.dtsi`, which is available in the same directory.
*   It contains information related to the SoC variant (version) such as the RAM and flash base addresses and sizes.

#### Base SoC devicetree file

The SoC devicetree contains SoC-level hardware descriptions for all the peripherals and system blocks. Examine the base SoC devicetree `nrf52833.dtsi` available in the directory `<install_path>\zephyr\dts\arm\nordic`.

*(Description of original image: nRF52833 SoC devicetree)*

*   The `gpio0` node is defined here.
*   The node specifies which hardware it represents via the `compatible` property. This is used by the driver to select which nodes it supports.
*   It also defines the address space for the node.

This should give you a basic overview of how hardware is described and presented using the devicetree. To get more information about the devicetree, you can download the devicetree specification [here](https://www.devicetree.org/specifications/).

---

## Device driver model

*(Instrucciones correspondientes a nRF Connect SDK v2.7.0 - v2.9.0)*

In order to interact with a hardware peripheral or a system block, we need to use a **device driver** (or driver for short), which is software that deals with the low-level details of configuring the hardware the way we want. In the nRF Connect SDK, the driver implementation is highly decoupled from its API. This basically means that we are able to switch out the low-level driver implementation without modifying the application because we can use the same generic API.

This decoupling has many benefits, including a high level of portability, as it makes it possible to use the same code on different boards without needing to manually modify the underlying driver implementation.

The application interacts with the hardware through the generic API by obtaining a **device pointer** for the hardware in question, using the macro `DEVICE_DT_GET()` or related macros.

> **Note**
> It is also possible to get the device pointer through `device_get_binding()`, though this is no longer recommended.
> As opposed to the previous practice of using `device_get_binding()` to retrieve the device pointer, using `DEVICE_DT_GET()` has the benefit of failing at build time if the device was not allocated by the driver, for instance, if it does not exist in the devicetree or has the status `disabled`.
> In addition, unlike `device_get_binding()`, it does not perform a run-time string comparison, which could impact performance in some situations.

The Zephyr device model is responsible for the association between generic APIs and device driver implementations.

*(Description of original image: Zephyr device model diagram)*

The macro `DEVICE_DT_GET()` has the signature shown below:

To get the device pointer, you need to pass the devicetree node identifier. As mentioned in the Devicetree section, there are many ways to get the node identifier. Two common ways are by the node label through the macro `DT_NODELABEL()` and by an alias through the macro `DT_ALIAS()`.

Before using the device pointer, it should be checked using `device_is_ready()`, which has the following signature:

`device_is_ready()` will check if the device is ready for use, for instance, if it is properly initialized.

The following code snippet will take the devicetree node identifier returned by `DT_NODELABEL()` and return a pointer to the device object. Then `device_is_ready()` verifies that the device is ready for use, i.e. in a state so that it can be used with its standard API.
```c
const struct device *dev;
dev = DEVICE_DT_GET(DT_NODELABEL(uart0));

if (!device_is_ready(dev)) {
    // Handle error: device not ready
    return;
}
```
To use a device driver generic API, you must have a pointer of type `const struct device` to point to its implementation. You need to do this per peripheral instance. For example, if you have two UART peripherals (`&uart0` and `&uart1`) and you want to use them both, you must have two separate pointers of type `const struct device`.

In other words, you need to have two different calls to `DEVICE_DT_GET()`.

> **Important**
> Most peripheral APIs will have an equivalent to `DEVICE_DT_GET()` and `device_is_ready()` that are specific to the peripheral. For example for the GPIO peripheral, there is `GPIO_DT_SPEC_GET()` and `gpio_is_ready_dt()`.
> These are the recommended ways to use the peripheral as they collect more information about the peripheral from the devicetree structure and reduce the need to add peripheral configurations in the application code.

---

## GPIO Generic API

*(Instrucciones correspondientes a nRF Connect SDK v2.7.0 - v2.9.0)*

To interact with the General-Purpose Input/Output (GPIO) peripheral, we can use the generic API `<zephyr/drivers/gpio.h>`, which provides user-friendly functions to interact with GPIO peripherals. The GPIO peripheral can be used to interact with a variety of external components such as switches, buttons, and LEDs.

When using any driver in Zephyr, the first step is to initialize it by retrieving the device pointer. For a GPIO pin, the first necessary step after that is to configure the pin to be either an input or an output pin. Then you can write to an output pin or read from an input pin. In the following paragraphs, these four steps will be covered in detail.

### Initializing the API

Some of the generic APIs in Zephyr have API-specific structs that contain the previously mentioned device pointer, as well as some other information about the device. In the GPIO API, this is the structure `gpio_dt_spec`. This structure encompasses the device pointer `const struct device * port`, as well as the pin number on the device, `gpio_pin_t pin`, and the device’s configuration flags, `gpio_dt_flags_t dt_flags`.

The `port` is the GPIO device controlling the pin. Pins are usually grouped and controlled by a single GPIO port. On most Nordic SoCs, there are either one or two GPIO controllers, named `GPIO0` or `GPIO1`.

You can check this in the SoCs product specification. For example, see the [nRF52833 Product Specification section GPIO — General purpose input/output](https://infocenter.nordicsemi.com/topic/ps_nrf52833/gpio.html).

To retrieve this structure, we need to use the API-specific function `GPIO_DT_SPEC_GET()`, which has the following signature:

Similar to `DEVICE_DT_GET()`, `GPIO_DT_SPEC_GET()` also takes the devicetree node identifier. It also takes the property name of the node. The function will return a variable of type `gpio_dt_spec`, containing the device pointer as well as the pin number and configuration flags.

The advantage of this API-specific structure is that it encapsulates all the information needed to use the device in a single variable, instead of having to extract it from the devicetree line by line.

Let’s take `led_0` as an example, which has the devicetree implementation shown below:

*(Description of original image showing led_0 node properties)*

From the image description above, we can see that the property containing all this information is called `gpios`, and is the property name to pass to `GPIO_DT_SPEC_GET()`:
```c
// Assuming led0 is an alias for the led_0 node
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
```
This function will return a struct of type `gpio_dt_spec` with the device pointer for the GPIO controller, `&gpio0`, the pin number `led.pin = 13` and the flag `led.dt_flags = GPIO_ACTIVE_LOW`.

Before using the device pointer contained in `gpio_dt_spec led`, we need to check if it’s ready using `gpio_is_ready_dt()`.
```c
if (!gpio_is_ready_dt(&led)) {
    // Handle error: GPIO device not ready
    return 0; // Example error return
}
```

### Configure a single pin

This is done by calling the function `gpio_pin_configure_dt()`, which has the following signature:

With this function, you can configure a pin to be an input (`GPIO_INPUT`) or an output (`GPIO_OUTPUT`) through the second parameter `flags` as shown in the examples below.

The following line configures the pin associated with `gpio_dt_spec led`, which can be denoted as `led.pin`, as an output pin:
```c
// Assuming 'led' is the gpio_dt_spec initialized earlier
int ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT);
if (ret < 0) {
    // Handle configuration error
}
```
You can also specify other hardware characteristics to a pin like the drive strength, pull up/pull down resistors, active high or active low. Different hardware characteristics can be combined through the `|` operator. Again, this is done using the parameter `flags`.

The following line configures the pin `led.pin` as an output that is active low.
```c
// Assuming 'led' is the gpio_dt_spec initialized earlier
int ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT | GPIO_ACTIVE_LOW);
if (ret < 0) {
    // Handle configuration error
}
```
All GPIO flags are documented [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/hardware/peripherals/gpio.html#gpio-flags).

### Write to an output pin

Writing to an output pin is straightforward by using the function `gpio_pin_set_dt()`, which has the following signature:

For example, the following line sets the pin associated with `gpio_dt_spec led`, which can be denoted as `led.pin`, to logic 1 “active state”:
```c
// Assuming 'led' is the gpio_dt_spec initialized and configured as output
int ret = gpio_pin_set_dt(&led, 1);
if (ret < 0) {
    // Handle set error
}
```
For instance, for the node `led_0` on the nRF52833DK, this would set pin 13 to logic 1 “active state”.

You can also use the `gpio_pin_toggle_dt()` function to toggle an output pin.

For example, the following line will toggle the pin `led.pin`, whenever this API is called.
```c
// Assuming 'led' is the gpio_dt_spec initialized and configured as output
int ret = gpio_pin_toggle_dt(&led);
if (ret < 0) {
    // Handle toggle error
}
```

### Read from an input pin

Reading a pin configured as an input is not as straightforward as writing to a pin configured as an output. There are two possible methods to read the status of an input pin:

1.  **Polling method**
    Polling means continuously reading the status of the pin to check if it has changed. To read the current status of a pin, all you need to do is to call the function `gpio_pin_get_dt()`, which has the following signature:

    For example, the following line reads the current status of `led.pin` saves it in a variable called `val`.
    ```c
    // Assuming 'led' is configured as input (change variable name for clarity if needed, e.g., 'button')
    int val = gpio_pin_get_dt(&led);
    if (val < 0) {
        // Handle read error
    } else {
        // val contains 0 or 1 (or potentially other values on error, hence check)
    }
    ```
    The drawback of the polling method is that you have to repeatedly call `gpio_pin_get_dt()` to keep track of the status of a pin. This is usually not optimal from performance and power perspectives as it requires the CPU’s constant attention. It’s a simple method, yet not power-efficient.
    We will use this method in Exercise 1 of this lesson for demonstration purposes.

2.  **Interrupt method**
    In this method, the hardware will notify the CPU once there is a change in the status of the pin. This is the **recommended way** to read an input pin as it frees the CPU from the burden of repeatedly polling the status of the pin. You can put the CPU to sleep and only wake it up when there is a change. We will use this method in Exercise 2 of this lesson.

    > **Note**
    > You can only configure an interrupt on a GPIO pin configured as an input.

    The following are the general steps needed to set up an interrupt on a GPIO pin.

    1.  **Configure the interrupt on a pin.**
        This is done by calling the function `gpio_pin_interrupt_configure_dt()`, which has the signature shown below:

        Through the second parameter `flags`, you can configure whether you want to trigger the interrupt on rising edge, falling edge, or both. Or change to logical level 1, logical level 0, or both.
        The following line will configure an interrupt on `button.pin` on the change to logical level 1 (active state).
        ```c
        // Assuming 'button' is the gpio_dt_spec for the button pin
        int ret = gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_TO_ACTIVE);
        if (ret < 0) {
            // Handle interrupt configuration error
        }
        ```
        All interrupt flag options are documented [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/hardware/peripherals/gpio.html#interrupt-configuration-flags), under GPIO interrupt configuration flags.

    2.  **Define the callback handler function `pin_isr()`**.
        > **Definition**
        > **Callback handler function**: Also known as an interrupt handler or an Interrupt Service Routine (ISR). It runs asynchronously in response to a hardware or software interrupt. In general, ISRs have higher priority than all threads (covered in Lesson 7). It preempts the execution of the current thread, allowing an action to take place immediately. Thread execution resumes only once all ISR work has been completed.

        The signature (prototype) of the callback handler function is shown below:
        ```c
        void pin_isr(const struct device *dev, struct gpio_callback *cb, gpio_port_pins_t pins);
        ```
        This signature is defined in `gpio_callback_handler_t`.
        What you put inside the body of an ISR is highly application-dependent. For instance, the following ISR toggles a LED every time the interrupt is triggered.
        ```c
        // Assuming 'led' is a globally accessible gpio_dt_spec for the LED
        void pin_isr(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
        {
            gpio_pin_toggle_dt(&led);
        }
        ```

    3.  **Define a variable of type `static struct gpio_callback`** as shown in the code line below.
        ```c
        static struct gpio_callback pin_cb_data;
        ```
        The `pin_cb_data` gpio callback variable will hold information such as the pin number and the function to be called when an interrupt occurs (callback function).

    4.  **Initialize the gpio callback variable `pin_cb_data` using `gpio_init_callback()`.**
        This `gpio_callback` struct variable stores the address of the callback function and the bitmask relevant to the pin. Use the function `gpio_init_callback()` to do this initialization.

        For example, the following line will initialize the `pin_cb_data` variable with the callback function `pin_isr` and the bit mask of pin `button.pin`. Note the use of the macro `BIT(n)`, which simply gets an unsigned integer with bit position n set.
        ```c
        // Assuming 'button' is the gpio_dt_spec for the button pin
        // Assuming 'pin_isr' is the callback function defined earlier
        gpio_init_callback(&pin_cb_data, pin_isr, BIT(button.pin));
        ```

    5.  **The final step is to add the callback function through the function `gpio_add_callback()`.**

        For example, the following line adds the callback function that we set up in the previous steps.
        ```c
        // Assuming 'button' is the gpio_dt_spec for the button pin
        int ret = gpio_add_callback(button.port, &pin_cb_data);
        if (ret < 0) {
            // Handle adding callback error
        }
        ```

The full API documentation for GPIO generic interface is available [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/hardware/peripherals/gpio.html).

---

## Dissecting the blinky sample

*(Instrucciones correspondientes a nRF Connect SDK v2.7.0 - v2.9.0)*

Now that we have examined the devicetree, device driver model, and the GPIO generic API, let’s dissect the blinky sample program to understand how it works.

In the following paragraphs, we will examine the blinky sample line by line to understand how this program is working. The blinky sample comes with the nRF Connect SDK and can be found at this location: `<install_path>\zephyr\samples\basic\blinky`.

*(Description of original image: Blinky sample code)*

1.  **Include modules**
    The blinky sample uses the following modules in the nRF Connect SDK:
    *   Kernel services `<zephyr/kernel.h>` for the sleep function `k_msleep()`. This header is called the Public kernel API header.
    *   The generic GPIO interface `<zephyr/drivers/gpio.h>` for the structure `gpio_dt_spec`, the macros `GPIO_DT_SPEC_GET()`, and the functions, `gpio_is_ready_dt()`, `gpio_pin_configure_dt()` and `gpio_pin_toggle_dt()`.
    ```c
    #include <zephyr/kernel.h>
    #include <zephyr/drivers/gpio.h>
    ```

2.  **Define the node identifier**
    The line below uses the devicetree macro `DT_ALIAS()` to get the node identifier symbol `LED0_NODE`, which will represent LED1 (node `led_0`). Remember from the Devicetree topic that `led_0` node is defined in the devicetree of the DK. `LED0_NODE` is now the source code symbol that represents the hardware for LED1.
    The `DT_ALIAS()` macro gets the node identifier from the node’s alias, which as we saw in the Devicetree section, is `led0`.
    ```c
    #define LED0_NODE DT_ALIAS(led0) // LED0_NODE = led0 defined in the .dts file
    ```
    > **Note**
    > There are many ways to retrieve the node identifier. The macros `DT_PATH()`, `DT_NODELABEL()`, `DT_ALIAS()`, and `DT_INST()` all return the node identifier, based on various parameters.

3.  **Retrieve the device pointer, pin number, and configuration flags.**
    The macro call `GPIO_DT_SPEC_GET()` returns the structure `gpio_dt_spec led`, which contains the device pointer for node `led_0` as well as the pin number and associated configuration flags. The node identifier `LED0_NODE`, defined in the previous step, has this information embedded inside its `gpios` property. Note the second parameter `gpios`, the name of the property containing all this information.
    ```c
    /* Get the node identifier for the LED specified by its alias. */
    #define LED0_NODE DT_ALIAS(led0)

    static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
    ```
    Now let’s examine `main()`.

4.  **Verify that the device is ready for use**
    As we mentioned before, we must pass the device pointer of the `gpio_dt_spec`, in this case `led`, to `gpio_is_ready_dt()`, to verify that the device is ready for use.
    ```c
    int main(void)
    {
        // ... other definitions ...

        if (!gpio_is_ready_dt(&led)) {
                return 0; // Or handle error appropriately
        }
        // ... rest of the code ...
    }
    ```

5.  **Configure the GPIO pin**
    The generic GPIO API function `gpio_pin_configure_dt()` is used to configure the GPIO pin associated with `led` as an output (active low) and initializes it to a logic 1, as explained in the GPIO Generic API section.
    ```c
        int ret;

        ret = gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);
        if (ret < 0) {
            return 0; // Or handle error appropriately
        }
    ```

6.  **Continuously toggle the GPIO pin**
    Finally, the blinky main function will enter an infinite loop where we continuously toggle the GPIO pin using `gpio_pin_toggle_dt()`. Note that in every iteration, we are also calling the kernel service function `k_msleep()`, which puts the main function to sleep for 1 second (assuming `SLEEP_TIME_MS` is 1000), resulting in the blinking behavior at 1-second intervals.
    ```c
        #define SLEEP_TIME_MS   1000

        while (1) {
            ret = gpio_pin_toggle_dt(&led);
            if (ret < 0) {
                return 0; // Or handle error appropriately
            }
            k_msleep(SLEEP_TIME_MS);
        }
        return 0; // Should not be reached in this example
    } // End of main
    ```

---

## Exercise 1: Controlling an LED through a button (polling based)

*(Instrucciones correspondientes a nRF Connect SDK v2.7.0 - v2.9.0)*

In this exercise, we will modify the blinky example so that LED1 is turned on only when button 1 is being pressed.

> **Note**
> On the nRF54L15 DK, the board’s LEDs and Buttons are labeled with PCB labels (PCB silkscreen) that start with 0 (LED0-LED3) and (BUTTON0-BUTTON3). In previous-generation development kits, the indexing starts with 1 (LED1-LED4). So, on the nRF54L15 DK, we will be working with LED0 and BUTTON0.

To do this, we will use the **polling method**, as discussed in GPIO Generic API. This is done by continuously polling the CPU to check if the button was pressed and then update the LED accordingly. In Exercise 2 that follows, we will learn how to use GPIO interrupts, which is more power-efficient than polling.

If we recall the schematic of the nRF52833 DK, there are four push-buttons connected to the same GPIO peripheral as the LEDs, `GPIO0` (node label: `gpio0`). This can be seen in the GPIO pin mapping, for instance, notice that button 1 is connected to `P0.11`. The `0` in `P0` symbolizes it is `&gpio0`.

*(Description of original images: nRF52833 DK button location and pin mapping)*

This is why the same driver is needed for both the LEDs and buttons. This is also evident from the DK’s devicetree file `nrf52833dk_nrf52833.dts`:
```devicetree
        buttons {
                compatible = "gpio-keys";
                button0: button_0 { /* Button 1 on PCB */
                        gpios = <&gpio0 11 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>;
                        label = "Push button switch 0";
                };
                button1: button_1 { /* Button 2 on PCB */
                        gpios = <&gpio0 12 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>;
                        label = "Push button switch 1";
                };
                /* ... other buttons ... */
        };

        /* ... */
        /* These aliases are provided for compatibility with samples */
        aliases {
                /* ... other aliases ... */
                sw0 = &button0; /* Alias for Button 1 */
                sw1 = &button1; /* Alias for Button 2 */
                sw2 = &button2; /* Alias for Button 3 */
                sw3 = &button3; /* Alias for Button 4 */
                /* ... other aliases ... */
        };
```
Button 1 on the nRF52833 DK is given the node name `button_0`, which has the alias (`sw0`) and node label (`button0`) and is connected to `&gpio0`, pin `11`. Remember, indexing in the devicetree files always starts from 0, which is why button 1 on the board is called `button0`.
```devicetree
gpios = <&gpio0 11 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>;
```

> **Note**
> If the buttons are connected to a different GPIO port (e.g. `gpio1`) than the LEDs, a new device pointer is required. As an example, the nRF54L15 DK, which has LEDs on both `gpio1` and `gpio2`, while buttons are connected to `gpio0` and `gpio1`.

### Exercise steps

1.  **Clone the nRF Connect SDK Fundamentals GitHub repository.** Use either the VS Code GUI (1.1) or the command line (1.2).

    1.1 **Using VS Code:** Go to `View` -> `Command Palette` -> type `Git Clone` and paste the repository link (`https://github.com/NordicDeveloperAcademy/ncs-fund.git`). Save the repo close to the root directory.
    1.2 **Using command line:** Create a folder near your root directory and run the following in the nRF Connect Terminal:
    ```bash
    git clone https://github.com/NordicDeveloperAcademy/ncs-fund.git
    ```
    > **Note**: Ensure no spaces or special characters in the path to the repository.

2.  **Open the exercise code base in VS Code.**
    2.1 From the Welcome View in the nRF Connect extension, click **Open an existing application**.
    2.2 Select the base code folder: `l2/l2_e1` (choose your SDK version subfolder if applicable) and click **Select Folder**.
    2.3 Open `main.c` from the Explorer view.

3.  **Initialize the button on the hardware.**
    3.1 Get the node identifier for button 1 using its alias `sw0`. Add the following line near the top of `main.c` (e.g., after the LED definition):
    ```c
    #define SW0_NODE DT_ALIAS(sw0)
    ```
    3.2 Get the device pointer, pin number, and flags using `GPIO_DT_SPEC_GET()`. Add the following line (e.g., below the LED spec):
    ```c
    static const struct gpio_dt_spec button = GPIO_DT_SPEC_GET(SW0_NODE, gpios);
    ```
    This populates the `button` variable with info from the `gpios` property of the node identified by the `sw0` alias.

4.  **Verify the button device is ready.** Add the following check inside `main()` after initializing the `button` spec:
    ```c
    if (!device_is_ready(button.port)) {
            printk("Error: button device %s is not ready\n", button.port->name);
            return -1; // Indicate error
    }
    ```

5.  **Configure the button pin as input.** Add the following inside `main()` after the readiness check:
    ```c
    ret = gpio_pin_configure_dt(&button, GPIO_INPUT);
    if (ret < 0) {
            printk("Error %d: failed to configure %s pin %d\n", ret, button.port->name, button.pin);
            return -1; // Indicate error
    }
    ```

6.  **Poll the button status and update the LED in the main loop.**
    6.1 Read the button status using `gpio_pin_get_dt()`. Add inside the `while (1)` loop:
    ```c
    bool val = gpio_pin_get_dt(&button);
    // Note: gpio_pin_get_dt returns 0 or 1 on success, <0 on error.
    // The simple assignment works because active-low button + pull-up means:
    // Pressed = low level = 0 = LED OFF (if configured GPIO_OUTPUT_ACTIVE)
    // Released = high level = 1 = LED ON (if configured GPIO_OUTPUT_ACTIVE)
    // If LED is configured GPIO_OUTPUT_INACTIVE, the logic is reversed.
    // Let's assume LED is configured GPIO_OUTPUT_ACTIVE as in blinky.
    // We want LED ON when pressed (val=0). Let's invert the logic for setting the LED.
    // Alternatively, configure the LED as GPIO_OUTPUT_INACTIVE.
    // For simplicity with GPIO_OUTPUT_ACTIVE, let's set LED to !val
    ```
    6.2 Update the LED based on the button status using `gpio_pin_set_dt()`. Add after reading `val`:
    ```c
    // Assuming 'led' is configured as GPIO_OUTPUT_ACTIVE (ON=1, OFF=0)
    // And button is active low (Pressed=0, Released=1)
    // Set LED ON (1) when button pressed (val=0). Set OFF (0) when released (val=1)
    gpio_pin_set_dt(&led, !val);
    ```

7.  Change the sleep time in the `while` loop from `1000` ms to `100` ms by modifying the `SLEEP_TIME_MS` macro or the value passed to `k_msleep`.
    ```c
    #define SLEEP_TIME_MS 100
    // ... inside while(1) loop ...
    k_msleep(SLEEP_TIME_MS);
    ```

8.  Add a build configuration for your board as done in Lesson 1, Exercise 2.

9.  Build the exercise and flash it to your board. Observe that when button 1 is pressed, LED1 turns ON (or LED0/Button 0 on nRF54L15 DK).

The solution for this exercise can be found in the GitHub repository, in `l2/l2_e1_sol` (select your version subfolder).

---

## Exercise 2: Controlling an LED through a button (interrupt based)

*(Instrucciones correspondientes a nRF Connect SDK v2.7.0 - v2.9.0)*

In this exercise, we will modify the application to use the more power-efficient **interrupt-based method**, as explained in GPIO Generic API. Configure the button to generate an interrupt every time it is pressed. Then, inside the interrupt handler (callback function) of the button, we will toggle the LED.

### Exercise steps

1.  In VS Code, select **Open an existing application**.
2.  Open the exercise code base found in the cloned repository: `l2/l2_e2` (select your version subfolder). Open `main.c`.
3.  **Configure the interrupt on the button's pin.** Add the following code inside `main()` after configuring the button pin as input (`GPIO_INPUT`):
    ```c
    ret = gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_TO_ACTIVE);
    if (ret < 0) {
        printk("Error %d: failed to configure interrupt on %s pin %d\n", ret, button.port->name, button.pin);
        return -1; // Indicate error
    }
    ```
4.  **Define the callback function `button_pressed()`.** Add this function definition *before* `main()`:
    ```c
    void button_pressed(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
    {
        gpio_pin_toggle_dt(&led);
    }
    ```
5.  **Define a variable of type `static struct gpio_callback`.** Add this definition *outside* `main()` (e.g., near the top with other static variables):
    ```c
    static struct gpio_callback button_cb_data;
    ```
6.  **Initialize the static struct `gpio_callback` variable.** Add the following line inside `main()` *after* configuring the interrupt:
    ```c
    gpio_init_callback(&button_cb_data, button_pressed, BIT(button.pin));
    ```
7.  **Add the callback function using `gpio_add_callback()`.** Add the following line inside `main()` *after* initializing the callback:
    ```c
    ret = gpio_add_callback(button.port, &button_cb_data);
    if (ret < 0) {
        printk("Error %d: failed to add callback\n", ret);
        return -1; // Indicate error
    }
    ```
8.  Remove the polling code (the call to `gpio_pin_get_dt()` and `gpio_pin_set_dt(&led, !val)`) from the `while (1)` loop in `main()`. The loop should now only contain the sleep call.
9.  Increase the sleep time in the `main` function's `while` loop significantly, for example, to 10 minutes. This demonstrates that the CPU isn't busy polling. Change the `SLEEP_TIME_MS` macro definition:
    ```c
    #define SLEEP_TIME_MS (10 * 60 * 1000) // 10 minutes
    ```
    The `while` loop in `main` will now look like:
    ```c
    while (1) {
        k_msleep(SLEEP_TIME_MS);
    }
    ```

    > **More on this**
    > In this example, since the main thread has nothing else to do, the idle thread will likely run, putting the CPU into a low-power sleep state. The CPU wakes up only when the button interrupt occurs, executes the ISR (`button_pressed`), toggles the LED, and then resumes the `main` thread, which immediately goes back to sleep via `k_msleep()`.
    > Since the main function essentially does nothing after setup, calling `k_yield()` in the loop instead of `k_msleep()` would also allow the scheduler to run other threads or the idle thread. `k_msleep` with a long duration achieves a similar power-saving effect in this simple case by allowing the idle thread to take over.
    > Lesson 7 will cover the different Zephyr system threads in more detail.

10. Build the exercise and flash it to the board. Observe that when button 1 is pressed, LED1 toggles (or Button 0 / LED 0 on nRF54 DKs). The toggling happens immediately upon pressing the button, independent of the long sleep time in the main loop.

The solution for this exercise can be found in the GitHub repository, in `l2/l2_e2_sol` (select your version subfolder).