## Elements of an nRF Connect SDK application

### Overview

In nRF Connect SDK, an application has a number of different elements that are used by the build system in some way to create the final runnable file. Understanding these elements, why they are needed, and how they interact with each other is crucial when creating your own application. In this lesson, we will explore each of these elements to understand how they all function in relation to each other. In the exercise portion, we will create a minimal working application from scratch and add our own custom files and configurations to customize the application.

Typical application structure:
```
app/
|-- CMakeLists.txt
|-- Kconfig
|-- prj.conf
|-- <board_name>.overlay
|-- src/
    |-- main.c
```

---

## Configuration files

*(Información relevante para nRF Connect SDK v2.7.0 – v2.9.0)*

### Application and board configurations

Each application in the nRF Connect SDK must have an **application configuration file**, usually called `prj.conf`, that describes the software modules and kernel services used and their settings. The application configuration file is text-based and contains configuration options (often called symbols) in the form of:

```kconfig
CONFIG_<symbol_name>=<value>
```

Each configuration option must start with the prefix `CONFIG_` followed by the name of the software module to configure, then the value to be set, with no spaces around the equals sign.

Let’s take a look at the application configuration file `prj.conf` from the blinky sample, which we covered in-depth in the previous lesson.

This file has only one line, seen below, that includes the GPIO driver.
```kconfig
CONFIG_GPIO=y
```
In other words, setting the `CONFIG_GPIO` symbol will enable the inclusion of the source code of the GPIO driver into the build process and hence our application will be able to use it.

In addition to the application configuration file, an application inherits the **board configuration file**, `<board_name>_defconfig`, of the board that the application is built for.

Let’s take an example, the nRF52833 DK has the board configuration file `nrf52833dk_nrf52833_defconfig` available in `<nRF Connect SDK Installation Path>\zephyr\boards\nordic\nrf52833dk`.

```kconfig
# SPDX-License-Identifier: Apache-2.0

CONFIG_SOC_SERIES_NRF52X=y
CONFIG_SOC_NRF52833_QIAA=y
CONFIG_BOARD_NRF52833DK_NRF52833=y

# Enable MPU
CONFIG_ARM_MPU=y

# Enable hardware stack protection
CONFIG_HW_STACK_PROTECTION=y

# Enable RTT
CONFIG_USE_SEGGER_RTT=y

# enable GPIO
CONFIG_GPIO=y

# enable uart driver
CONFIG_SERIAL=y

# enable console
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y

# additional board options
CONFIG_GPIO_AS_PINRESET=y
```
*Board configuration file for the nRF52833 DK: nrf52833dk_nrf52833_defconfig*

> **Note**
> Configuration options can be set both in the application configuration file and the board configuration file. In the example, `CONFIG_GPIO` symbol is set in both files. In this case, the value in the application configuration file always takes precedence.

The first three lines in the board configuration file includes software support specific to the nRF52833 DK and its nRF52833 SoC. The `CONFIG_ARM_MPU` is for the memory protection unit. This brings us to the question: How can we know the meaning of all these configuration options?

If you are using nRF Connect for VS Code, simply hovering the mouse over the configuration symbol will show a box that contains a description about the symbol.

Additionally, you can visit the [documentation webpage](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/kconfig/index.html) and find the documentation for the specific symbol, for instance, `CONFIG_GPIO`.

Further examining the board configuration file of the nRF52833 DK, we can see that the UART driver (`CONFIG_SERIAL`), the RTT drivers, the libraries (`CONFIG_USE_SEGGER_RTT`), and the console drivers (`CONFIG_CONSOLE`) are included. `CONFIG_UART_CONSOLE` will make UART the default console output. All of these software components are core to interacting with a console.

> **Note**
> You should **never** modify any board configuration files. Instead, rely on the application configuration file (`prj.conf`) to set new configurations and subsequently overwrite any default board configurations if needed. If you change the board configuration file directly, then these changes will apply for all projects using that board.

### Kernel Configuration (nRF Kconfig GUI)

In the nRF Connect SDK, symbols are grouped into menus and sub-menus to easily browse all available configurations.

An alternative way to modify the contents of the `prj.conf` (application configuration file) is by using the **nRF Kconfig GUI**. Kconfig refers to the software configurations and it groups all functionalities provided by the nRF Connect SDK and Zephyr into menus and submenus, which can be viewed in a graphical tree format.

The nRF Kconfig GUI view allows us to browse and implement the different functionalities available easily. Selecting/deselecting functionalities in the nRF Kconfig GUI corresponds to adding/removing lines in the `prj.conf` file.

nRF Kconfig GUI can be found under **Actions** in the nRF Connect extension in VS Code.

> **Important**
> Starting from nRF Connect SDK v2.8.0, Sysbuild is the default build system. nRF Kconfig GUI allows you to display the Kconfig configurations for Sysbuild itself and any of its images in the project. This is done by first selecting the image of interest from the **APPLICATIONS** view and then clicking on the **nRF Kconfig GUI** in the **ACTIONS** view.

There are other visual editors for Kconfig; you can access them through the submenu under nRF Kconfig GUI. You can also change the default Kconfig visual editor via `File -> Preferences -> Settings -> Extensions -> nRF Connect -> Kconfig Interface`.

Kconfig is organized into menus that group related configurations together, such as Modules, Device Drivers, C Library, and Boot Options. Menus can have submenus, and submenus can have submenus of their own. If we expand any of these menus, for instance, Device Drivers, all symbols related to this category will show up, some with menus of their own.

*(Description of image: Kconfig tree structure in nRF Connect for VS Code)*

A checked box indicates that this symbol is enabled, either in the application configuration file or in the board configuration file. For example, searching for “GPIO” shows that the GPIO drivers are enabled in the blinky sample configuration.

*(Description of image: GPIO driver enabled in Kconfig)*

After making changes in the Kconfig menu, there are 3 different ways to save those changes:
*(Description of image: Save options in Kconfig GUI)*

1.  **Apply:** Saves changes to a temporary configuration file (`build/zephyr/.config`). These changes are reverted on a pristine build.
2.  **Save to file:** Saves changes directly to `prj.conf`, preserving them across builds.
3.  **Save minimal:** Saves only the changes made into a separate file.

> **More on this**
> There are two interactive Kconfig interfaces (`nRF Kconfig GUI`, `menuconfig`) supported by nRF Connect for VS Code. They all allow you to explore related configuration options and know their values. One advantage of `menuconfig` is that it lists the dependencies and where the Symbol is set. However, the disadvantage of `menuconfig` is that configurations are only set temporarily and will be lost any time you do a clean (pristine) build. On the other hand, `nRF Kconfig GUI` is the only graphical interface that can allow you to save the configurations permanently in `prj.conf`.

---

## Devicetree overlays, CMake, and build systems

### Devicetree overlays

In lesson 2, we covered the devicetree, a hierarchical data structure that describes hardware through nodes with belonging properties. It is not recommended to modify the base devicetree files directly. Instead, we use **devicetree overlays** to modify the hardware description for a specific application. The overlay only needs to include the node and property it wants to modify.

```devicetree
/* Example overlay enabling SPI1 and configuring MOSI pin */
&spi1{
    status = "okay";
};

&pinctrl {
    spi1_default: spi1_default {
        group1 {
            psels = <NRF_PSEL(SPIM_MOSI, 0, 25)>;
        };
    };
    spi1_sleep: spi1_sleep {
        group1 {
            psels = <NRF_PSEL(SPIM_MOSI, 0, 25)>;
        };
    };
};
```
The overlay file shown above will set node `spi1` to have the status `okay`, essentially enabling this node. Then it is changing the pin configuration for the `SPIM_MOSI` line to pin `P0.25` by changing the appropriate sub-nodes and properties in the `&pinctrl` node. Note that you must change the pin configuration for both the `default` and `sleep` states if modifying pin control this way.

If an overlay file sets a node’s property to a value it already has, the node will just remain unchanged.

One easy way to create an overlay file is to create a file with the name of the board and the extension `.overlay` (e.g., `nrf52833dk_nrf52833.overlay`) and place it directly in the application root directory. The build system will automatically search for this file type and include it if it finds one.

However, there are several other ways to include overlay files. See [Set devicetree overlays](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/dts/howtos.html#set-devicetree-overlays) for a list of ways to include a devicetree overlay in your application.

> **Note**
> Overlays are also DTS files; the `.overlay` extension is just a convention that makes their purpose clear.

### CMake

In the nRF Connect SDK, all applications are **CMake** projects. This means that the application controls the configuration and build process of itself, Zephyr, and all sourced libraries. The file `CMakeLists.txt` is the main CMake project file and the source of this build process configuration.

We will take a closer look at some of the functions in the exercise.

### Sysbuild

**Sysbuild** is a high-level build system that simplifies the management of complex multi-image builds. It is an improved and extensible build system for multi-image builds, replacing the nRF Connect SDK-specific Multi-image builds system used in older nRF Connect SDK versions.

Sysbuild is mainly used for two use cases: **Multi-core applications** and **bootloaders**.

Sysbuild became available in nRF Connect SDK version 2.7.0 and is enabled by default for all nRF Connect SDK projects from version 2.8.0 onwards.

Sysbuild works by configuring and building at least a Zephyr application and, optionally, as many additional projects as you want. The additional projects can be either Zephyr applications or other types of builds.

To distinguish CMake variables and Kconfig options specific to the underlying build systems, sysbuild uses **namespacing**. For example, sysbuild-specific Kconfig options are preceded by `SB_` before `CONFIG` and application-specific CMake options are preceded by the application name.

Sysbuild is integrated with `west`. The sysbuild build configuration is generated using the sysbuild’s `CMakeLists.txt` file (which provides information about each underlying build system and CMake variables) and the sysbuild’s Kconfig options (which are usually gathered in the `sysbuild.conf` file).

> To learn more about Sysbuild, there is a dedicated lesson on it in the nRF Connect SDK Intermediate course – Lesson 8- Sysbuild

#### A note on Kconfig.sysbuild

For the nRF5340, we need to run an image on the network core if we want to use the Bluetooth LE radio. This is done automatically by the build system using the Sysbuild feature. Here is a brief explanation of how to add an image to the network core, specifically as done in the Bluetooth LE Fundamentals course, the Wi-Fi Fundamentals course, and the nRF Connect SDK samples.

Sysbuild uses Kconfig in a similar way to the `prj.conf`/`something.conf` we know. However, for Sysbuild, they are named `sysbuild.conf` / `Kconfig.sysbuild`.

To select an image for the network core, we set one of the configurations found under the docs for [Sysbuild: Enabling images](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/images.html). In most Bluetooth LE samples, **IPC Radio** is used, so we will also use IPC Radio.

Normally, this can be set in `sysbuild.conf` by adding:
```kconfig
# Enable IPC Radio for the network core
SB_CONFIG_NETCORE_IPC_RADIO=y
# Configure protocol for IPC Radio
SB_CONFIG_NETCORE_IPC_RADIO_BT_HCI_IPC=y
```
However, both in DevAcademy courses and the nRF Connect SDK Bluetooth LE samples set these instead in `Kconfig.sysbuild`, as shown below:
```kconfig
source "${ZEPHYR_BASE}/share/sysbuild/Kconfig"

config NRF_DEFAULT_IPC_RADIO
    default y

config NETCORE_IPC_RADIO_BT_HCI_IPC
    default y

```
This is because `SB_CONFIG_NETCORE_IPC_RADIO` only works for multi-core chips (Ex: nRF5340 SoC), so if this is set in `sysbuild.conf`, the samples would get a warning when building for single-core chips. However, when the configurations are set in `Kconfig.sysbuild`, the warning does not appear.

*(Explanation from original text about why Kconfig.sysbuild avoids the warning by overlaying default based on `SUPPORT_NETCORE_IPC_RADIO`)*

---

## Trusted Firmware-M (TF-M)

**Trusted Firmware-M (TF-M)** is a blueprint for constructing a Secure Processing Environment (SPE) tailored to Arm M-profile architectures. TF-M relies on the principle of security through separation to safeguard sensitive credentials and code. Additionally, TF-M extends its protective capabilities to applications by offering security services, including Protected Storage, Cryptography, and Attestation.

The Nordic Semiconductor Series, which implements the Armv8-M architecture (Arm Cortex-M33), incorporates **TrustZone** technology. This technology enforces hardware-based segregation between Secure and Non-secure Processing Environments, effectively creating separate Trusted and Non-Trusted build images.

This means that we have two options for boards based on the nRF54L/nRF53/nRF91 Series. Either:

*   **Option 1 – `<board_target>/ns`**
    Enforce security by separation by utilizing TF-M. Our application runs in the **Non-Secure Processing Environment (NSPE)** and TF-M runs in the **Secure Processing Environment (SPE)**.
*   **Option 2 – `<board_target>`**
    Do not enforce security by separation. Our application runs as a single image with full access privileges.

Let’s take a board with a board target `<board_target>` as an example. When building an application for the board, you could build for either `<board_target>` or `<board_target>/ns`.

*   `<board_target>`: The application is built as a single image without security by separation.
*   `<board_target>/ns`: The application will be built as a Non-Secure image. Hence, you will get security by separation as TF-M will automatically be built as the Secure image. The two images will be merged to form a combined image that will be used when programming or updating the device.

*(Diagram description from original text comparing Option 1 and Option 2)*

> **Note**
> In nRF Connect SDK v2.6.2 and below build targets were referenced as `nrf9160dk_nrf9160` and `nrf9160dk_nrf9160_ns`) (hardware model v1). Starting from nRF connect SDK v2.7.0, hardware model v2 is used with `/` used instead of `_`. Hardware support and custom boards are covered in-depth the nRF Connect SDK Intermediate course – Lesson 3.

---

## Child and parent images (deprecated)

When using the older multi-image build system, the build consisted of a parent image and one or more child images, where the child image is included by the parent image.

This build system was deprecated in nRF Connect SDK v2.8.0 and replaced by Sysbuild; child/parent images will be removed completely in a future release.

---

## Exercise 1: Creating an application

In this exercise, we will learn how to create a working “Hello World” application in the nRF Connect SDK from scratch. We are only doing this for educational purposes to expose you to all the elements of an nRF Connect SDK application.

Keep in mind that this is **not** the recommended way to create an application. As we explained in lesson 1, the recommended way is by using one of the samples that you can find in the SDK as a baseline.

### Exercise steps

1.  In the exercise folder for this lesson, create a folder and name it `l3_e1`.
2.  Open this folder and create the files needed for a minimum working application:
    *   `prj.conf` (leave empty for now)
    *   `CMakeLists.txt`
    *   Create a subdirectory `src`
    *   Inside `src`, create an empty file `main.c`
3.  Open `CMakeLists.txt` and add the minimum functions needed for the application to build:
    ```cmake
    cmake_minimum_required(VERSION 3.20.0)
    find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
    project(hello_world)
    target_sources(app PRIVATE src/main.c)
    ```
    *   `cmake_minimum_required`: ensures the build fails if the CMake version is too old.
    *   `find_package`: pulls in the Zephyr build systems, which creates a CMake target named `app`.
    *   `project`: sets the name of the project.
    *   `target_sources`: adds the source file to the project.

4.  In `src/main.c`, include the header file for Zephyr Kernel and the printk module:
    ```c
    #include <zephyr/kernel.h>
    #include <zephyr/sys/printk.h>
    ```
5.  In `src/main.c`, define the `main` function to continuously print the statement “Hello World!” and then sleep for a small amount of time (to avoid flooding the console).
    ```c
    int main(void)
    {
        while (1) {
            printk("Hello World!\n");
            k_msleep(1000); // Sleep for 1 second
        }
        return 0; // Should not be reached
    }
    ```
    > **Note**: `prj.conf` is left empty because the console drivers needed by `printk()` are enabled by default by the board configuration file. This is covered in-depth in Lesson 4.

6.  Add this as an existing application in nRF Connect for VS Code. Go to nRF Connect for VS Code and under the **Welcome View**, select **Open an existing application** and select the directory `l3_e1`. Observe the project showing up under the **Applications View**.
7.  Just like in Lesson 1, select **Add Build Configuration** by hovering your mouse over the project name in the Applications View and selecting the icon that appears. Choose the correct board, then select **Build Configuration**.
8.  Flash the application to your board.
9.  To view the output of the application, configure a terminal emulator. We will show how to use the built-in **nRF Terminal** in VS Code or the **Serial Terminal** application in nRF Connect for Desktop.

    Two important parameters for UART console:
    *   **Speed (baud rate):** Default for Nordic DKs is 115200 bps.
    *   **Serial line (COM port):** Varies by machine and board. Boards might have multiple Virtual COM (VCOM) ports (e.g., VCOM0, VCOM1).

    > **Note: Which Virtual COM (VCOM) port to choose?**
    > Nordic DKs have an interface MCU providing UART-to-USB and VCOM ports. Different VCOMs might be for specific uses (e.g., TF-M logs vs. application logs). If you don't see expected output on one VCOM port, try another and reset the board.

    #### Using nRF Terminal (VS Code)
    1. Go to the **Connected Devices** tab and expand your connected device.
    2. Click the **Connect To Serial Port In nRF Terminal** icon.
    3. Choose the serial port.
    4. Set the configuration:
        * Baud rate: 115200
        * 8 data bits, no parity, 1 stop bit (8N1)
        * No flow control (RTS/CTS off)
    5. Observe the output:
       ```
       *** Booting Zephyr OS build zephyr-v3.x.x ***
       Hello World!
       Hello World!
       ...
       ```

    #### Using Serial Terminal (nRF Connect for Desktop)
    1. Open the **Serial Terminal** app in nRF Connect for Desktop.
    2. Select the correct COM port for your board from the dropdown list.
    3. Set the baud rate to 115200.
    4. Ensure other settings match (8N1, no flow control).
    5. Click **Open**.
    6. You might need to press the **Reset** button on your DK to see the initial boot messages and output.
    7. Observe the output similar to the nRF Terminal example above.


The solution for this exercise can be found in the GitHub repository, `l3/l3_e1_sol` (select your version subfolder).

---

## Exercise 2: Customizing the application

During application development, it can be useful to customize aspects of the nRF Connect SDK for your specific application, without modifying the SDK files themselves. In this exercise, we will customize our application by adding custom files, configurations, and modifying the devicetree.

### Exercise steps

Use the previous exercise (`l3_e1`) as your starting point. Copy the completed exercise folder to a new directory and name it `l3_e2`. Open this new folder in VS Code.

#### Adding custom files

1.  Create a `.c` file and a `.h` file in the `src/` directory, alongside `main.c`. Call them `myfunction.c` and `myfunction.h`.
2.  Define a function `sum()` in `myfunction.c` and declare it in `myfunction.h`.
    *   `myfunction.c`:
        ```c
        #include "myfunction.h"

        int sum(int a, int b){
            return a+b;
        }
        ```
    *   `myfunction.h`:
        ```c
        #ifndef MY_FUNCTION_H
        #define MY_FUNCTION_H

        int sum(int a, int b);

        #endif // MY_FUNCTION_H
        ```
        > **Definition: Include guards**
        > A construct (usually preprocessor macros) used to prevent problems caused by including the same header file multiple times within a single translation unit.

3.  **Include the custom source file in the build.** Add the following line to `CMakeLists.txt`:
    ```cmake
    target_sources(app PRIVATE src/myfunction.c)
    ```
4.  **Include the header file in `main.c`**. Add this line at the top of `src/main.c`:
    ```c
    #include "myfunction.h"
    ```
5.  **Replace `main()` to run the custom function.** Modify the `main` function in `src/main.c`:
    ```c
    int main(void)
    {
        int a = 3, b = 4;
        while(1){
            printk("The sum of %d and %d is %d\n", a, b, sum(a,b));
            k_msleep(1000);
        }
        return 0; // Should not be reached
    }
    ```
6.  Build and flash the application to your board. Open a terminal output and you should see:
    ```
    *** Booting nRF Connect SDK ... ***
    *** Using Zephyr OS ... ***
    The sum of 3 and 4 is 7
    The sum of 3 and 4 is 7
    ...
    ```
    The issue with including source code directly via `target_sources()` is that the file is always included, even if the function isn't used. Next, we'll control this using Kconfig.

#### Adding custom configurations

6.  **Define a custom Kconfig symbol.** Create a file named `Kconfig` (no extension) in the application root directory (`l3_e2/`). Add the following content:
    ```kconfig
    # SPDX-License-Identifier: Apache-2.0

    source "Kconfig.zephyr"

    mainmenu "Application Configuration"

    config MYFUNCTION
        bool "Enable my function"
        default n
        help
          Enable the custom sum function defined in myfunction.c/h.
    ```
    *   `source "Kconfig.zephyr"`: Necessary to include base Zephyr configurations.
    *   `config MYFUNCTION`: Defines the symbol `CONFIG_MYFUNCTION`.
    *   `bool`: Specifies it's a boolean type.
    *   `"Enable my function"`: The prompt displayed in configuration interfaces.
    *   `default n`: Sets the default value to no (disabled).
    *   `help`: Provides descriptive text.

    (See Kconfig documentation for more on creating menus).

7.  **Make the addition of the custom source file conditional.** In `CMakeLists.txt`, comment out or remove the `target_sources` line from step 3 and add the following line instead, using `target_sources_ifdef()`:
    ```cmake
    # target_sources(app PRIVATE src/myfunction.c) # Commented out
    target_sources_ifdef(CONFIG_MYFUNCTION app PRIVATE src/myfunction.c)
    ```
    The build will now only include `myfunction.c` if `CONFIG_MYFUNCTION` is enabled (`=y`).

    > **Note**
    > This strategy is used extensively in nRF Connect SDK to only include the source code of libraries that you plan to use, limiting application size. Modules are included only when enabled via Kconfig.

8.  **Enable the custom Kconfig symbol.** Add the following line to `prj.conf`:
    ```kconfig
    CONFIG_MYFUNCTION=y
    ```
9.  **Update `main.c` to check the Kconfig symbol.**
    9.1 Conditionally include the header file:
    ```c
    #ifdef CONFIG_MYFUNCTION
    #include "myfunction.h"
    #endif
    ```
    9.2 Conditionally call the function within `main()`:
    ```c
    int main(void)
    {
        while (1) {
    #ifdef CONFIG_MYFUNCTION
            int a = 3, b = 4;
            printk("The sum of %d and %d is %d\n", a, b, sum(a, b));
    #else
            printk("MYFUNCTION not enabled\n");
            // Removed return 0 here to keep the loop running
            // You might want different behavior if disabled
    #endif
            k_msleep(1000);
        }
        return 0; // Should not be reached
    }
    ```
10. Build and flash the application. You should see the "The sum..." output again.
11. **Try disabling the Kconfig symbol.**
    11.1 In `prj.conf`, change the line to `CONFIG_MYFUNCTION=n`.
    11.2 **Perform a Pristine Build** (required for Kconfig changes affecting CMake to take effect reliably). In VS Code Actions view, click the "Pristine Build" icon next to the Build action, or use the Command Palette (`Ctrl+Shift+P`) and search for `Pristine Build`. Flash the application.
         > **Definition: Pristine build**
         > Creates a new build directory. All byproducts from previous builds have been removed.
    11.3 You should now see the output:
         ```
         *** Booting nRF Connect SDK ... ***
         *** Using Zephyr OS ... ***
         MYFUNCTION not enabled
         MYFUNCTION not enabled
         ...
         ```
    11.4 **Re-enable** the symbol in `prj.conf` (`CONFIG_MYFUNCTION=y`) for the next section. Remember to do another build (pristine might not be strictly necessary here, but safe) and flash.

#### Modifying the devicetree

In this section, we will modify the devicetree for this specific application using an overlay file to change the UART console baud rate.

12. **Create an overlay file.**
    *   In the application root directory (`l3_e2/`), create a subdirectory named `boards`.
    *   Inside the `boards` directory, create an overlay file named `<board_target>.overlay`. For the nRF52833 DK, this would be `nrf52833dk_nrf52833.overlay`.
        *   **Important**: Use the actual **board target** string used in the build configuration (e.g., `nrf54l15dk_nrf54l15_cpuapp_ns.overlay` for nRF54L15 DK with TF-M), not just the marketing name.
    *   Alternatively, use the VS Code nRF Connect extension GUI: Select the application context, expand `Config files -> Devicetree`, and click `+ Create overlay file`. This helps ensure the correct name.

13. **Change the baud rate for the UART node.** Add the following to your `.overlay` file to change the `current-speed` property of the default UART console peripheral (`uart0` for most DKs, check your board's DTS if unsure, e.g., `uart20` for nRF54L15).
    ```devicetree
    /* Overlay for changing UART0 baud rate */
    &uart0 {
        current-speed = <9600>; /* Change baud rate to 9600 */
    };
    ```
    *(Note: If using nRF54L15 DK, replace `&uart0` with `&uart20` or the correct UART instance)*.
    Common things changed via overlays include peripheral `status` (`okay`/`disabled`) and pin assignments (`pinctrl-*`). See [Set devicetree overlays](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/dts/howtos.html#set-devicetree-overlays) for more methods.

14. **Do a pristine build** (essential for devicetree changes) and flash the application.
    *   Use the Pristine Build icon in VS Code Actions or the Command Palette.
    *   To confirm the change, view the compiled devicetree output: Use the Command Palette (`Ctrl+Shift+P`) and run `nRF DeviceTree: Open Compiled Output`. Search for `uart0` (or your UART instance) and verify the `current-speed` property is `9600`. The compiled file is usually located at `<app_dir>/build/<build_dir_name>/zephyr/zephyr.dts`.
    *   You can also use the **DeviceTree Visual Editor** (accessible from Actions View or Command Palette) after a build. Navigate to the `uart` node and inspect its properties.
        > **Note**: Ensure the `nRF DeviceTree` extension (part of the nRF Connect Extension Pack) is installed to use the visual editor.

15. Observe that the serial terminal likely shows **garbled output or no output**. This is because the application is now transmitting at 9600 baud, while the terminal is likely still configured for 115200 baud.

16. **Change the baud rate in the serial terminal** to match the application (9600).
    *   **nRF Terminal (VS Code):**
        1. Close the existing terminal connection.
        2. Reconnect to the serial port.
        3. When prompted for settings (or click the cogwheel icon), select `[Other]` for baud rate and enter `9600`.
        4. Keep other settings (8N1, no flow control).
        5. Observe the correct "The sum..." log output.
    *   **Serial Terminal (nRF Connect for Desktop):**
        1. Close the connection if open.
        2. Change the baud rate setting in the app to `9600`.
        3. Open the connection.
        4. Reset the board if needed.
        5. Observe the correct log output.

17. **Devicetree Visual Editor (further reading).**
    Once you have an overlay and a compiled build, the DeviceTree Visual Editor provides a GUI to explore and modify the devicetree structure. You can view node properties and edit them directly, which automatically updates the corresponding `.overlay` file. It's a useful tool for learning Devicetree syntax as changes in the GUI reflect in the text file and vice-versa. Access it from the Actions view or Command Palette.

    *(Description of original image showing visual editor modifying UART properties)*

The solution for this exercise can be found in the GitHub repository, `l3/l3_e2_sol` (select your version subfolder).

---# nRF Connect SDK Introduction

## Overview
The nRF Connect SDK is a software development kit for building low-power wireless applications based on Nordic Semiconductor’s nRF54, nRF53, nRF52, nRF70, or nRF91 Series devices. We will take a look under the hood of the SDK to have a better understanding of its structure and content.

In the exercise section of this lesson, we will cover all the steps needed to download and install the nRF Connect SDK with the Visual Studio Code Integrated Development Environment (VS Code IDE). Then, we will test the installation by building and flashing the sample program blinky, which toggles an LED on your Nordic Semiconductor board. Finally, we will cover how to modify the blinky source code and rebuild the program to make the LED toggle at a different frequency.

The exercise is divided into two parts:

Exercise 1 – Installing nRF Connect SDK and VS Code.
Exercise 2 – Building your first nRF Connect SDK application.

## nRF Connect SDK structure and content

nRF Connect SDK is a scalable and unified software development kit for building low-power wireless applications based on the Nordic Semiconductor nRF54, nRF53, nRF52, nRF70, or nRF91 Series wireless devices. It offers an extensible framework for building size-optimized software for memory-constrained devices as well as powerful and complex software for more advanced devices and applications.

It integrates the Zephyr Real-Time Operating System (RTOS) and a wide range of complete applications, samples, and protocol stacks such as Bluetooth Low Energy, Bluetooth mesh, Wi-Fi, Matter, Thread/Zigbee and LTE-M/NB-IoT/GPS, TCP/IP. It also includes middleware such as CoAP, MQTT, LwM2M, various libraries, hardware drivers, Trusted Firmware-M for security, and a secure bootloader (MCUBoot).

*(Diagram described in original text: Architecture of the nRF Connect SDK)*

Zephyr RTOS and third-party components (e.g. MCUBoot, Trusted Firmware-M) are shown in dark blue in the above diagram description.

**Zephyr RTOS** is an open-source real-time operating system for connected and resource-constrained embedded devices. It includes a scheduler that ensures predictable/deterministic execution patterns and abstracts out the timing requirements. It also comes with a rich set of fundamental libraries and middleware that simplifies development and helps reduce a product’s time to market. Zephyr RTOS is highly configurable and enables scalable configurations from very small configurations for memory-constrained devices (minimum 8 kilobytes, for example, simple LED blinking application) to powerful, feature-rich, high-processing power devices (multiple MBs of memory) with large memory configurations.

The nRF Connect SDK offers a single code base for all of Nordic’s devices and software components. It simplifies porting modules, libraries, and drivers from one application to another, thus reducing development time. By enabling developers to pick and choose the essential software components for their application, high memory efficiency is guaranteed. The nRF Connect SDK is publicly hosted on GitHub.

Internally, the nRF Connect SDK code is organized into four main repositories:

*   `nrf` – Applications, samples, connectivity protocols (Nordic)
*   `nrfxlib` – Common libraries and stacks (Nordic)
*   `Zephyr` – RTOS & Board configurations (open source)
*   `MCUBoot` – Secure Bootloader (open source)

In addition to the four main repositories, there are also other repositories like the `TrustedFirmware-M` repository and the `Matter` repository.

The figure below (description from original text) visualizes the toolchain in the nRF Connect SDK, which is based on the Zephyr toolchain. You can see a set of different tools, each playing a role in the creation of an application, from configuring the system to building it.

*(Diagram described in original text: nRF Connect SDK tools and configuration methods)*

**Kconfig** (covered in Lesson 3) generates definitions that configure the whole system, for example, which wireless protocol or which libraries to include in your application. **Devicetree** (covered in Lesson 2) describes the hardware. **CMake** then uses the information from Kconfig and the devicetree to generate build files, which **Ninja** (comparable to make) will use to build the program. The **GCC** compiler system is used to create the executables.

This high decoupling of the source code (`*.c`) and the configuration system through Kconfig (`*.conf`) and the hardware description system through devicetree (`*.dts`) makes it easy to use the same application source code on different hardware and with different configurations with minimal changes. This has a huge impact on the ease of portability and maintainability.

*(Diagram described in original text: Build process for nRF Connect SDK)*

Now that we have an understanding of the content and structure of the nRF Connect SDK, let’s move to the hands-on part of this lesson where we install the nRF Connect SDK through some high-level tools that simplify the process of obtaining the repositories and setting up the needed toolchains.

---

## Exercise 1: Installing nRF Connect SDK and VS Code

*(The following instructions correspond to nRF Connect SDK v2.7.0 - v2.9.0 as presented in the original text.)*

Follow the steps below to install the nRF Connect SDK, its toolchain, and VS Code IDE. Starting September 2023, It is possible to download nRF Connect SDK and its toolchain directly from within VS Code, as explained in this guide.

In the first three steps (1-3), we will download the tools needed to flash firmware to the various Nordic Semiconductor development kits supported on DevAcademy (nRF Command Line Tools, Segger J-Link, and nrfutil and nrfutil device command).

1.  **Install nRF Command Line Tools.**
    Download the latest version that matches your operating system.
    Download link: [https://www.nordicsemi.com/Products/Development-tools/nRF-Command-Line-Tools/Download?lang=en#infotabs](https://www.nordicsemi.com/Products/Development-tools/nRF-Command-Line-Tools/Download?lang=en#infotabs).
    > **Note**
    > The nRF Command Line Tools is in the process of being archived. nRF Command Line Tools will remain available for download but will gradually be replaced by nRF Util. For courses on DevAcademy, you will need both nRF Command Line Tools and nRF Util during this transition period.

2.  **Install SEGGER J-Link v8.10f**
    Download the installer for your platform from [SEGGER J-Link Software](https://www.segger.com/downloads/jlink/). Run the installer; when you reach the ‘Choose Optional Components’ window during installation, be sure to select ‘Install Legacy USB Driver for J-Link’. This driver is necessary for some supported Development Kits.

3.  **Install nrfutil and the nrfutil device command**
    3.1 Download the binary compatible with your OS from the [nRF Util product page](https://www.nordicsemi.com/Products/Development-tools/nrf-util) and store it somewhere on your disk drive (For example `C:\nordic_tools\nrfutil.exe` for Windows).
    If you are running on macOS or Linux, you can store it in a folder that is already added in the system’s PATH (E.g. `/usr/bin/`), so that you can skip step 3.2.
    > **Note**
    > For Linux, keep in mind that nrfutil has some prerequisites that are listed in [Installing nRF Util prerequisites](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/gs_installing.html#nrfutil-prerequisites). Make sure you also download them, if you don’t have them on your machine already.
    3.2 (Windows) Update your system’s PATH to include the location where nrfutil is stored. Open `Edit environment variable for your account` and add the path where you stored the nrfutil binary.
    3.3 The `nrfutil` binary you just downloaded does not come with any pre-installed commands. In this step, we will upgrade the core `nrfutil` and download the `device` command.
    3.3.1 To make sure we have the latest nrfutil version, run the following command in a terminal (Command Prompt or PowerShell). It doesn’t matter which terminal since nrfutil is set globally in step 3.2.
    ```bash
    nrfutil self-upgrade
    ```
    3.3.2 Install the `nrfutil device` command. For this course, we will need the `device` command to flash binaries to development kits. In your active terminal, type:
    ```bash
    nrfutil install device
    ```
    You should see output similar to:
    ```
    [00:00:02] ###### 100% [Install packages] Install packages
    ```

4.  **Install VS Code.**
    Go to [https://code.visualstudio.com/download](https://code.visualstudio.com/download) and install the version that matches your operating system.

5.  **Install nRF Connect Extension Pack.**
    In the Activity Bar in VS Code, click the Extensions icon, then type `nRF Connect for VS Code Extension Pack` in the search field, and click on `Install`.

    **nRF Connect for VS Code extension pack** allows developers to use the popular Visual Studio Code Integrated Development Environment (VS Code IDE) to develop, build, debug, and deploy embedded applications based on Nordic’s nRF Connect SDK (Software Development Kit). It includes an interface to the compiler, linker, the whole build system, an RTOS-aware debugger, a seamless interface to the nRF Connect SDK, the Devicetree Visual Editor, and an integrated serial terminal, among other valuable development tools.

    nRF Connect for VS Code extension pack consists of the following components:
    *   **nRF Connect for VS Code:** The main extension contains an interface to the build system and nRF Connect SDK. It also provides an interface to manage nRF Connect SDK versions and toolchains.
    *   **nRF DeviceTree:** Provides Devicetree language support and the Devicetree Visual Editor.
    *   **nRF Kconfig:** Provides Kconfig language support.
    *   **nRF Terminal:** A serial and RTT terminal.
    *   **C/C++ from Microsoft:** Adds language support for C/C++, including features such as IntelliSense.
    *   **CMake:** CMake language support.
    *   **GNU Linker Map Files:** Linker map files support.

    We can download any nRF Connect SDK version of our preference and its toolchain through the extension. Complete documentation of the nRF Connect for VS Code is available [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/vscode/index.html).

    > **Note**
    > It’s crucial to install the `nRF Connect for VS Code Extension Pack`, not just `nRF Connect for VS Code`, in order to get all the available features.

6.  **Install Toolchain.**
    The toolchain is a set of tools that are used together to build nRF Connect SDK applications. It includes the assembler, compiler, linker, and CMake, among other tools.

    The first time you open nRF Connect for VS Code, it will prompt you to install a toolchain. This usually happens when the extension does not find any installed toolchain on your machine.

    Click on `Install Toolchain`. It will list the available versions of toolchains that can be downloaded and installed on your machine. Select the toolchain version that matches the nRF Connect SDK version you plan to use. We always recommend using the latest tagged version of the nRF Connect SDK.

    Installing the toolchain will take some time, depending on your development platform specifications and internet speed.

    > **Note**
    > By default, nRF Connect for VS Code displays only released tags (also known as stable versions) of toolchains. If you are evaluating new features and want to use a preview tag or a different type of tag (for example, customer sampling -cs), click on “Show All Toolchain Versions.” Note that for production code, only released tags should be used.

7.  **Install nRF Connect SDK.**
    In nRF Connect for VS Code, click on `Manage SDK`. Through the `Manage SDK` interface, we can install or uninstall nRF Connect SDK versions. Since this is our first time using the extension, we will see only two options. Click on `Install SDK`. It will list the available versions of the nRF Connect SDK that can be downloaded and installed on your machine. Choose the nRF Connect SDK version you wish to use for your project development.

    > **Note**
    > If you have opened the SDK folder in VS Code, the `Manage SDK` menu option will not be present, and you will instead see `Manage west workspace`. To fix this, open another window or folder in VS Code. If you don’t see either option, make sure you have the latest version of the nRF Connect for VS Code extension pack.

    We are showing how to install nRF Connect SDK version 2.4.2 (as an example from the original text). Depending on your internet and machine speed, this will take some time to finish.

    > **Important**
    > We recommend installing the latest released tag of nRF Connect SDK listed to get all the latest features and patches.

    With this, we have completed the installation of nRF Connect SDK and VS Code.

    > **Note**: It’s also worth noting that nRF Connect SDK is IDE agnostic, which means you can use it with the IDE of your choice or without an IDE. It is possible to download and install the nRF Connect using a command-line interface (CLI) through nRF Util (`nrfutil`). However, we highly recommend using VS Code with our nRF Connect for VS Code extension pack as it contains both a convenient graphical user interface (GUI) and an efficient command-line interface (CLI) in one place, in addition to many features that make firmware development much easier. Setting up another IDE to work with the nRF Connect SDK will require some extra manual steps that are out of the scope of this course.

---

## Exercise 2: Build and flash your first nRF Connect SDK application

*(The following instructions correspond to nRF Connect SDK v2.7.0 - v2.9.0 as presented in the original text.)*

In this exercise, we will program a simple application based on the `blinky` sample to toggle an LED on our board. Any supported Nordic Semiconductor development board will work (nRF54, nRF53, nRF52, nRF70, or nRF91 Series). The idea is to make sure that all the tools needed to build and flash a sample are set up correctly. The focus is to learn how to create an application from a template (“Copy a sample”), build the application, and flash it on a Nordic-powered board.

Basically, we will walk you through the three bullet points below:

*   Create a new application based on a template(sample).
*   Build an application.
*   Flash an application to a board.

### Exercise steps

1.  Create a folder close to your root directory that will hold all the exercises that we will be working on throughout this course.
    Example: `C:\myfw\ncsfund`. Avoid storing your applications in locations with long paths, as the build system might fail on some operating systems (Windows) if the application path is too long. Also, avoid using whitespaces and special characters in the path.

2.  In VS Code, click on the **nRF Connect Extension icon**. In the **WELCOME View**, click on **Create a new application**.

3.  In the **Create new application** dialog, select **Copy a sample**.
    You will be presented with three options:
    *   `Create a blank application`: Creates a blank application with an empty `main()` function.
    *   `Copy a sample`: Presents all the templates (“samples”) that come from the different modules in nRF Connect SDK and enables you to create an application based on a template. (Note: If you have multiple SDK versions installed, you will be prompted to select which SDK version to copy a sample from.)
    *   `Browse application index`: (Out of scope for this course) Copies a revision of an existing out-of-tree application compatible with the nRF Connect SDK from the online application index and sets up a west workspace repository around it.

    > **Note**
    > The SDK contains a rich set of templates. In the context of templates:
    > *   **Samples** are simple and showcase a single feature or library (e.g., SHA256 sample, UART sample, PWM sample, blinky sample, etc.).
    > *   **Applications** are complex and include a variety of libraries to implement a specific use case (e.g., Asset tracker application, Keyboard application, Mouse application).

    3.1 Type `blinky` in the search field and select the **Blinky Sample**. The Blinky sample blinks LED1 on your board indefinitely. We will base our first application on the Blinky sample. The Blinky sample comes from the Zephyr module in nRF Connect SDK, hence the sample path: `zephyr\samples\basic\blinky`.
    (Icons mentioned in original text allow access to the in-tree sample, online documentation, and GitHub repository respectively, and filtering options).

    3.2 Input the full path for where you want the application to be stored.
    1.  Select where you want to store your application (e.g., `C:\myfw\ncsfund\`).
    2.  Name your application `l1_e2`. This is the naming convention we will use for exercises throughout this course. This will create a folder for your application called `l1_e2`.
    Press Enter when you have input the full path.

    VS Code will ask if you want to open the application in the same VS Code instance or open a new VS Code instance. Select **Open** to open the application in the same VS Code instance.

    This will make a copy of the Blinky sample template, store it in the specified application directory, and add an unbuilt application to VS Code.

    > **Note**
    > nRF Connect for VS Code might show some error squiggles (e.g., header files not found) for an unbuilt application, often appearing in the PROBLEMS tab. Please ignore these error squiggles at this stage. These errors will automatically be resolved once you add and build a configuration (next step).

4.  **Add a build configuration.**
    This step specifies the hardware (development board or custom board) and software configuration (*.conf and possible devicetree overlays) for the build. What you set here controls the parameters passed to the underlying command-line tool, `west`.

    In the **APPLICATIONS view**, under the application name (`l1_e2`), click on **Add Build Configuration**. This opens the **Add Build Configuration** window.

    The GUI will inform you about the SDK/toolchain version being used. Ensure it matches the SDK/toolchain you intend to use and the SDK version from which you copied the sample. If not, click the arrow to select the correct version.

    4.1. Using the **Board target**, choose the board you want to flash your application to. See the table below for an overview of board targets for Nordic devices.

    | Device          | Board target                   |
    | :-------------- | :----------------------------- |
    | nRF54L15 DK*    | `nrf54l15dk/nrf54l15/cpuapp/ns`  |
    | nRF5340 DK      | `nrf5340dk/nrf5340/cpuapp/ns`  |
    | nRF52840 DK     | `nrf52840dk/nrf52840`          |
    | nRF52833 DK     | `nrf52833dk/nrf52833`          |
    | nRF52 DK        | `nrf52dk/nrf52832`             |
    | nRF9160 DK      | `nrf9160dk/nrf9160/ns`         |
    | nRF9161 DK*     | `nrf9161dk/nrf9161/ns`         |
    | nRF9151 DK*     | `nrf9151dk/nrf9151/ns`         |
    | Thingy:91 X     | `thingy91x/nrf9151/ns`         |
    | Thingy:91       | `thingy91/nrf9160/ns`          |
    | Thingy:53       | `thingy53/nrf5340/cpuapp/ns`   |
    | nRF7002 DK*     | `nrf7002dk/nrf5340/cpuapp/ns`  |

    *\*Board support added in specific SDK versions as noted in the original text.*

    > **Important**
    > The nRF54L15 PDK v0.8.1 is functionally equivalent to a DK. Use the board targets: `nrf54l15dk/nrf54l15/cpuapp/ns` (with TF-M) or `nrf54l15dk/nrf54l15/cpuapp` (without TF-M).

    (Example from original text: Choosing nRF52833 DK by specifying `nrf52833dk/nrf52833`).

    4.2. The **Board Revision** is usually on a sticker (format X.X.X). This field is optional and only needed if the board has multiple revisions (like nRF9160 DK). Leaving it blank uses the board definition's default.

    We will keep the default build configuration for the remaining options. However, understanding their roles is important:

    4.3. **Base configuration files:** Lists base application configuration files (e.g., `prj.conf`). Some templates might offer variants (e.g., `prj_minimal.conf`). Blinky has only `prj.conf`. Equivalent to `FILE_SUFFIX` (and `CONF_FILE`) in `west`.

    4.4. **Extra Kconfig fragments:** Lists additional Kconfig fragments (modifiers to the base configuration) found in the template or added to the application folder. Blinky has none. Equivalent to `EXTRA_CONF_FILE` in `west`.

    4.5. **Base Devicetree overlays:** Lists Devicetree overlays (hardware description modifiers) found in the template or added to the application folder. Blinky has none. Equivalent to `DTC_OVERLAY_FILE` in `west`.

    4.6. **Extra Devicetree overlays:** Provides additional custom devicetree overlay files to be mixed in. Equivalent to `EXTRA_DTC_OVERLAY_FILE` in `west`.

    4.7. **Snippets:** Bundles combining software (Kconfig) and hardware (Devicetree) configuration. Several exist in the SDK.

    4.8. **Extra CMake arguments:** Allows passing arguments to the build system. Leave blank for this demo.

    4.9. **Build directory name:** Option to manually name the build output directory. Default is usually `build` or `build_n`.

    4.10. **Optimization level:**
    *   `Use project default`: Uses settings from `prj.conf`.
    *   `Optimize for debugging (-Og)`: Important for debugging. Passes `CONFIG_DEBUG_THREAD_INFO="y"` and `CONFIG_DEBUG_OPTIMIZATIONS="y"`.
    *   `Optimize for speed(-O2)`: Passes `CONFIG_SPEED_OPTIMIZATIONS="y"`.
    *   `Optimize for size (-Os)`: Passes `CONFIG_SIZE_OPTIMIZATIONS="y"`.
    Leave as `Use project default` for this exercise. Remember to use `Optimize for debugging (-Og)` for debugging sessions.

    Leave the **Build after generating configuration** option enabled.

    4.11. **Sysbuild:** Enabled by default from nRF Connect SDK v2.8.0. Important for multi-image applications.

    4.12. Click the **Build Configuration** button.

    The build process will start. Open the **nRF Connect Terminal** (`View` -> `Terminal`) to see the progress. A successful build displays the application’s memory usage.

    > **More on this:**
    > A key component is `west`, a core command-line utility. It handles repository management, building, flashing, etc., and is invoked by the VS Code extension. You can use `west` commands manually in the terminal (use the `nRF Connect Terminal` where the toolchain is sourced). Type `west help` for details or check the `west` documentation.

    After building, a `build` sub-directory appears in your application folder, containing build outputs, including the binary file for flashing.

5.  Make sure your development kit is connected to your computer and switched on. It should be listed in the **Connected Devices View** in the nRF Connect for VS Code extension.

    > **Important**
    > If using a Thingy:53, Thingy:91 X, or Thingy:91 (no onboard debugger), the flash procedure differs, and the device won't appear in the Connected Devices View. Skip steps 5 and 6 and follow the specific flashing instructions for [Thingy:53](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/nrf_cloud/getting_started/thingy53_gs.html#programming-the-firmware) or [Thingy:91/Thingy:91 X](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/nrf_cloud/getting_started/thingy91_gs.html#programming-the-modem-and-application).

    If your board isn't listed, press the **Refresh Connected Devices** icon in the Connected Devices View.

6.  From the **Actions View**, click **Flash** to flash the application to the board. Monitor the progress in the Terminal Panel.

    > **Note**
    > `Flash` writes the application. `Erase And Flash To Board` erases the entire device first, including any saved application data (e.g., mesh network provisioning).

    LED1 on your board should now blink at one-second intervals.

    > **Note**
    > On the nRF54L15 DK, board LEDs are labeled starting from 0 (LED0-LED3). Previous DKs start from 1 (LED1-LED4). Running this sample on nRF54L15 DK will blink LED0.

7.  Let’s change the LED blink rate for demonstration.
    Locate `main.c` (in `Source Files->Applications` or via Explorer). On line 11 (or similar), change `SLEEP_TIME_MS` from `1000` to `100`.
    ```c
    #define SLEEP_TIME_MS   100
    ```

8.  Rebuild (click the build icon/button again for the existing configuration) and re-flash the application. Observe the LED blinking at a higher frequency.

---# Adding custom board support

## Overview

In the context of nRF Connect SDK/Zephyr, a **board definition** refers to configuration and initialization files that define the hardware characteristics and behavior of a specific development board or hardware platform.

nRF Connect SDK comes with support for a large number of boards (Development Kits, Prototyping Platforms, and Reference Designs), and it also offers the flexibility of adjusting the hardware specifications of existing board definitions through the use of devicetree overlay files and Kconfig fragments (Covered in the nRF Connect SDK Fundamentals course).

However, there are situations where we would like to create an entirely new board definition with its unique name and unique hardware specifications. This is usually the case when you have developed your schematics and own PCB for your Nordic-based product. We call this a **“custom board”** as the SDK itself does not provide it.

> **Important**: This lesson covers defining boards using Hardware Models V1 and V2.
> *   **Hardware Model V1 (HWMv1):** Used in nRF Connect SDK versions below v2.7.0.
> *   **Hardware Model V2 (HWMv2):** Default in nRF Connect SDK v2.7.0 and above, intended to replace HWMv1.
> Ensure you are viewing the content corresponding to your SDK version (use tabs if provided in the original source).

---

## Board definition

*(Information relevant for nRF Connect SDK v2.7.0 - v2.9.0 - HWMv2)*

When developing applications with nRF Connect SDK, the concept of a “board” is central. The SDK's high portability, based on Zephyr RTOS concepts, relies heavily on abstracting hardware differences.

A **Board** is simply the target hardware you want to build an application for. This abstraction makes moving applications between different hardware (e.g., nRF52840 DK to nRF54L15 DK, or DK to custom hardware) relatively straightforward. Hardware specifics are decoupled from application code via Devicetree and Kconfig.

Think of a “board” definition as a folder containing several key components:

*   **Devicetree files (`.dts`, `.dtsi`):** Describe the hardware – SoC(s) used, peripherals, pin configurations, memory layout, etc.
*   **Kconfig files (`Kconfig`, `_defconfig`):** Define software/RTOS configurations needed for the hardware (drivers, features).
*   **Metadata files (`board.yml`):** Describe high-level board information – name, vendor, SoC(s), revisions, variants.
*   **Optional C code (`.c`):** For special hardware initialization routines.
*   **Optional Documentation (`doc/`):** For board specifics.

A board definition includes information about:

*   **SoC configuration:** Exact SoC(s) (e.g., nRF54L15 QFAA), clock frequencies, memory details.
*   **Peripheral configuration:** Enabling and configuring available peripherals (UART, SPI, I2C, GPIO, Timers, etc.).
*   **Memory configuration:** RAM/Flash sizes, partitioning (application, bootloader, storage).
*   **Pin mapping:** Assigning SoC pins to specific functions (GPIO, UART TX/RX, etc.).
*   **Clock configuration:** Setting up system clocks.
*   **Interrupt configuration:** Assigning interrupt vectors and priorities.
*   **Driver configuration:** Default settings for drivers used by the board.
*   **Special Initialization Routines:** Custom C code for board-specific setup (muxes, PMICs, etc.).

Luckily, much of the lower-level configuration (Architecture, CPU, SoC Series/Family/Variant) is provided by the SDK. You primarily focus on the board-specific layer.

### Hardware support hierarchy (HWMv2)

nRF Connect SDK (v2.7.0+) uses Zephyr's Hardware Model V2 (HWMv2), organized in layers from specific to general:

1.  **Board:** Your specific hardware implementation (DK, custom board).
2.  **SoC:** Exact System-on-Chip used (e.g., nrf52833_qiaa). *(Provided by SDK)*
3.  **SoC Family:** Group of similar SoCs (e.g., nrf52). *(Provided by SDK)*
4.  **SoC Series:** Tightly related SoCs (e.g., nrf52x). *(Provided by SDK)*
5.  **CPU Core:** Specific CPU (e.g., cortex_m4). *(Provided by SDK)*
6.  **Architecture:** Instruction Set Architecture (e.g., arm). *(Provided by SDK)*

HWMv2 improves upon HWMv1, especially for multi-target boards (multi-core, multi-SoC, multi-architecture).

*   Boards are now located under `/boards/<vendor>/` instead of `/boards/<arch>/`.
*   Better integration with Sysbuild for managing multi-image builds (e.g., MCUboot, network cores).
*   Uses YAML (`.yml`) for describing boards, SoCs, revisions, variants, etc., providing flexibility.

**Example: nRF9160 DK**
*   **Board:** `nrf9160dk`
*   **SoCs:** `nrf9160`, `nrf52840`
*   **SoC Families:** `nrf91`, `nrf5`
*   **SoC Series:** `nrf91x`, `nrf52x`
*   **CPU Cores:** `cortex_m33`, `cortex_m4`
*   **Architecture:** `arm`

*(Table showing hierarchy for other Nordic DKs)*

### A note on drivers

Drivers for external components (sensors, displays, etc.) connected via peripherals (I2C, SPI) are *not* part of the board definition folder. They reside in dedicated driver locations within the SDK (`zephyr/drivers/`, `nrf/drivers/`). Drivers are matched to devicetree nodes via the `compatible` property. If a driver doesn't exist for your component, you may need to implement one.

> **More on this**: Creating custom drivers is covered in Lesson 7 of the Intermediate course.

---

## Creating board files

*(Information relevant for nRF Connect SDK v2.7.0 - v2.9.0 - HWMv2)*

This topic covers creating custom board files, naming conventions, file structure, and the role of each file in HWMv2.

> **Note**: The "Create a new board" GUI in VS Code uses the `west ncs-genboard` extension command, which can also be used via CLI.

### Naming your custom board

*   **Unique Name:** Must be unique across all boards known to `west`. Run `west boards` to see existing names.
*   **No SoC in Name:** HWMv2 doesn't require including the SoC in the board name; it's specified in `board.yml`.
*   **Board ID vs. Human Name:**
    *   The VS Code GUI asks for a **human-readable name** (can have spaces, caps, e.g., "My Custom Board").
    *   It automatically generates a **board ID** (used by build tools) from the human name (lowercase, spaces replaced by underscores, e.g., `my_custom_board`).

### HWMv2 – Board terminology

*(Diagram description: BL5340 DVK example showing terms)*

*   **Board Name (Board ID):** Machine-readable identifier (e.g., `devacademyl3e1`).
*   **Board Revision:** Optional version identifier (e.g., `@0.2.0`). Captures hardware changes.
*   **Board Qualifiers:** Additional tokens after the name/revision, separated by `/`. Define specific build targets.
    *   **SoC/CPU Cluster:** Identifies the target processor on multi-processor boards (e.g., `cpuapp`, `cpunet`, `cpuflpr`). Defined by the SoC layer.
    *   **Variant:** Designates specific configurations or build types (e.g., `ns` for Non-Secure/TF-M build, `xip` for execute-in-place, `sense` for a sensor-equipped hardware variant).
*   **Board Target:** The full string used by build tools (e.g., `west build -b <target>`). Combines name, revision (optional), and qualifiers.
    *   Single-core example: `devacademyl3e1/nrf52833`
    *   Multi-target example: `nrf54l15dk/nrf54l15/cpuapp/ns`

### Where to define your custom board

1.  **Upstream Zephyr:** For public DKs, modules, reference designs, open-source products. Requires documentation and maintainer review.
2.  **Dedicated Directory (Out-of-Tree):** Recommended for closed-source products. Store board files outside the SDK/Zephyr tree. Pass the directory path to the build system (`-DBOARD_ROOT=`). **(Method used in this lesson's exercises).**
3.  **Application `boards/` Folder:** Suitable for prototyping/debugging within a specific application.

### Board files (HWMv2 Structure)

Assuming a board ID `devacademyl3e1` from vendor `<vendor>`:

**Mandatory Files:**

```
boards/<vendor>/devacademyl3e1/
├── board.yml                     # Core board metadata (SoC, revisions, variants)
├── Kconfig.devacademyl3e1          # Selects SoC Kconfig support
├── devacademyl3e1_<qualifiers>.dts # Board-level Devicetree (one per target)
└── devacademyl3e1_<qualifiers>-pinctrl.dtsi # Pin control definitions (one per target)
```
*(Note: `<qualifiers>` part is omitted if the board only has one target)*

**Optional & Special Use Case Files:**

```
boards/<vendor>/devacademyl3e1/
├── ... (mandatory files) ...
├── devacademyl3e1_<qualifiers>_defconfig # Board default Kconfig settings (one per target)
├── Kconfig.defconfig                   # Default values for board Kconfig options
├── board.cmake                         # Flash/debug runner support
├── CMakeLists.txt                      # Add custom C init files (rarely needed)
├── <board_init_files>.c                # Custom C init code (rarely needed)
├── doc/                                # Documentation (for upstreaming)
│   ├── devacademyl3e1.png
│   └── index.rst
├── Kconfig                             # Defines board-specific Kconfig menu/options
├── devacademyl3e1_<qualifiers>.yml     # Twister (test runner) metadata (one per target)
├── devacademyl3e1_<qualifiers>_<revision>.conf    # Kconfig fragment for specific revision
├── devacademyl3e1_<qualifiers>_<revision>.overlay # Devicetree overlay for specific revision
└── dts/                                # Optional subfolder for DTS includes/bindings
    └── bindings/                       # Custom devicetree bindings
```

#### File Details:

1.  **`board.yml` (Mandatory):**
    *   Defines board `name` (ID), `vendor`. Optionally `full_name` (human-readable).
    *   Lists `socs` used (at least one).
    *   Optionally defines `revisions` and `variants`.
    *   CPU clusters are inherited from the SoC definition.
    *   VS Code extension auto-generates this; usually needs minimal changes.
    *(Examples shown for nRF52840 Dongle, nRF54L15 DK, nRF9161 DK)*

2.  **`Kconfig.<board_id>` (Mandatory):**
    *   Selects the Kconfig support for the specific SoC variant(s) used (e.g., `select SOC_NRF52833_QIAA`).
    *   Defines the `BOARD_<NORMALIZED_BOARD_NAME>` symbol (e.g., `config BOARD_DEVACADEMYL3E1`).
    *   Uses `if/endif` blocks based on normalized board target for multi-target boards.
    *(Examples shown for single-target devacademyl3e1 and multi-target nRF54L15 DK)*

3.  **`<board_target>.dts` (Mandatory, one per target):**
    *   Board-level devicetree. Includes the base SoC DTS (`#include <nordic/nrf52833_qiaa.dtsi>`).
    *   Defines board-specific hardware: connectors, LEDs, buttons, sensors, enabled peripherals, memory partitioning (`chosen` node).
    *   Can include `<board_target>-pinctrl.dtsi`.
    *   VS Code DeviceTree editor helps populate this.

4.  **`<board_target>-pinctrl.dtsi` (Mandatory, one per target):**
    *   Defines pin multiplexing configurations for peripherals using the `&pinctrl` node structure. Maps peripheral signals (e.g., `UART_TX`) to physical pins (e.g., `P0.06`).

5.  **`<board_target>_defconfig` (Optional but Recommended, one per target):**
    *   Kconfig fragment automatically included for builds targeting this board.
    *   Should enable the *bare minimum* hardware support needed for the board to function (e.g., GPIO, basic console if present).
    *   Application `prj.conf` is responsible for enabling application-specific features.
    *(Example shows adding UART, RTT, GPIO support for devacademyl3e1)*

6.  **`Kconfig.defconfig` (Optional but Recommended):**
    *   Sets *default values* for Kconfig options *specific to this board*, often conditionally based on the build target.
    *   Uses `if BOARD_<NORMALIZED_TARGET> / endif` blocks.
    *   Example: Setting default `BT_CTLR` if `CONFIG_BT` is enabled by the application.
    *(Examples shown for devacademyl3e1 and nRF54L15 DK)*

7.  **Other Optional Files:**
    *   `board.cmake`: Defines flash/debug commands (e.g., which runner `nrfjprog`, `jlink`).
    *   `CMakeLists.txt` / `<init>.c`: Add custom C initialization code run pre/post-kernel (rare).
    *   `doc/`: Documentation files (required for upstreaming to Zephyr).
    *   `Kconfig`: Defines board-specific Kconfig options/menus visible in tools like `menuconfig`.
    *   `<board_target>.yml`: Twister test framework metadata.
    *   `<board_target>_<revision>.conf/.overlay`: Revision-specific Kconfig/DTS fragments applied on top of base files when building for that revision (e.g., `myboard@1.0.0`). Update `board.yml` to define revisions.

> **Note**: When creating a custom board, examining existing DK definitions for the same SoC in `<sdk>/zephyr/boards/nordic/` and `<sdk>/nrf/boards/nordic/` is highly recommended. Also see the [Zephyr Board Porting Guide](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/guides/porting/board_porting.html).

---

## Board files for multi-core hardware & TF-M

*(Information relevant for nRF Connect SDK v2.7.0 - v2.9.0 - HWMv2)*

This topic covers specifics for defining boards based on SoCs with multiple cores or TrustZone-M support (nRF54L, nRF53, nRF91 Series).

Key differences from nRF52 Series:
*   **Architecture:** Armv8-M (vs. Armv7-M).
*   **CPU:** Cortex-M33 (vs. Cortex-M4).
*   **TrustZone-M:** Hardware security extension enabling Secure (SPE) and Non-Secure (NSPE) Processing Environments, often used with **Trusted Firmware-M (TF-M)**.
*   **Multiple Cores:** nRF53 has Application + Network cores. nRF54L has Application + RISC-V (FLPR) cores.

### Trusted Firmware-M (TF-M)

TF-M provides a Secure Processing Environment (SPE). Applications typically run in the Non-Secure Processing Environment (NSPE).

*   **Build Target Option 1: `<board_target>/<cpu_cluster>/ns`** (e.g., `nrf9151dk/nrf9151/ns`, `nrf5340dk/nrf5340/cpuapp/ns`)
    *   Enforces security separation.
    *   Application built as NSPE image.
    *   TF-M (or another SPE image like SPM) is automatically built as the SPE image.
    *   Images are merged for flashing. **(Required for many nRF Connect SDK samples, especially networking/modem related).**
*   **Build Target Option 2: `<board_target>/<cpu_cluster>`** (e.g., `nrf9151dk/nrf9151`, `nrf5340dk/nrf5340/cpuapp`)
    *   No security separation (TF-M disabled).
    *   Application built as a single image with full privileges.

*(Diagram description: Comparing Secure/Non-Secure builds)*

### Working with the nRF53 Series (nRF5340)

*   **Network core (cpunet):** Low-power M33 core for radio protocols. Build target: `<board_target>/cpunet`.
*   **Application core (cpuapp):** High-performance M33 core with TrustZone. Build targets:
    *   `<board_target>/cpuapp` (TF-M disabled)
    *   `<board_target>/cpuapp/ns` (TF-M enabled, application runs as NSPE)

### Working with the nRF91 Series (nRF9160/61/51/31)

*   Single user-programmable Cortex-M33 core with TrustZone.
*   Separate modem core (runs precompiled firmware).
*   Build targets:
    *   `<board_target>/nrf91xx` (TF-M disabled - *naming varies slightly based on exact SiP*)
    *   `<board_target>/nrf91xx/ns` (TF-M enabled, application runs as NSPE)

### Working with the nRF54L Series (nRF54L15)

*   **Application core (cpuapp):** Cortex-M33 with TrustZone. Build targets:
    *   `<board_target>/cpuapp` (TF-M disabled)
    *   `<board_target>/cpuapp/ns` (TF-M enabled)
*   **RISC-V coprocessor (cpuflpr):** Fast Lightweight Peripheral Processor. Build targets:
    *   `<board_target>/cpuflpr`: Runs from SRAM (Recommended). Requires `nordic-flpr` snippet in `cpuapp` build.
    *   `<board_target>/cpuflpr/xip`: Runs from RRAM (Execute-In-Place). Requires `nordic-flpr-xip` snippet in `cpuapp` build.

### Enabling TF-M in board definition

Assuming a custom board `devacademyl3e2` based on nRF9151.

**In Kconfig and Metadata Files:**

1.  **`board.yml`:** Must define the `ns` variant for the appropriate SoC.
    ```yaml
    board:
      name: devacademyl3e2
      vendor: nordic
      socs:
      - name: nrf9151 # Assumes SoC definition provides cpuapp cluster implicitly
        variants:
        - name: 'ns' # Define the non-secure variant
    ```
2.  **`Kconfig.defconfig`:** Conditionally set `FLASH_LOAD_OFFSET` and `FLASH_LOAD_SIZE` based on whether building the secure (`BOARD_...`) or non-secure (`BOARD_..._NS`) target, typically using values from devicetree partitions (`dt_chosen...` macros).
    *(See original text for full Kconfig.defconfig example logic)*
3.  **Two `_defconfig` files:**
    *   `devacademyl3e2_nrf9151_defconfig` (for secure/non-TF-M build): Must enable `CONFIG_ARM_TRUSTZONE_M=y`. Include other board defaults (GPIO, UART, etc.).
    *   `devacademyl3e2_nrf9151_ns_defconfig` (for non-secure build): Must enable `CONFIG_ARM_TRUSTZONE_M=y` *and* `CONFIG_TRUSTED_EXECUTION_NONSECURE=y`. Include other board defaults.

**In Devicetree Files:**

4.  **Memory Partitioning:** Define memory regions for Secure (`sram0_s`, `slot0_partition`) and Non-Secure (`sram0_ns`, `slot0_ns_partition`) execution. This is often done by including a common partitioning file provided by the SDK (e.g., `<sdk>/dts/common/nordic/nrf91xx_partition.dtsi`).
    4.1 Create a common DTS include file (e.g., `devacademyl3e2_nrf9151_common.dtsi`) that includes the common pinctrl file and the SoC partitioning file.
       > **More on this**: If using MCUboot, the Partition Manager often overrides DTS partitioning. Covered in Lesson 9.
    4.2 Create separate board DTS files for each target (`devacademyl3e2_nrf9151.dts` and `devacademyl3e2_nrf9151_ns.dts`).
       *   Each includes the common DTS file (`#include "devacademyl3e2_nrf9151_common.dtsi"`).
       *   Each includes the appropriate SoC definition (`nrf9151_laca.dtsi` or `nrf9151ns_laca.dtsi`).
       *   Each uses the `chosen` node to select the correct flash (`zephyr,code-partition`) and SRAM (`zephyr,sram`) partitions for that specific build target (secure vs. non-secure).
       *   The non-secure DTS (`_ns.dts`) should disable peripherals allocated to the secure domain (e.g., `&uart1 { status = "disabled"; };` if UART1 is used by TF-M).
    *(See original text for example `.dts` content)*

---

## Exercise 1 – Custom board for single-core SoC

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0 - HWMv2)*

Create a custom board definition (`DevAcademyL3E1`) based on nRF52833 DK schematics (minus Arduino headers), using the VS Code "Create a new board" tool.

### Exercise steps

1.  Create a root directory for custom boards (e.g., `C:\my_boards`).
2.  In VS Code -> Welcome page -> **Create a new board**.
3.  Follow prompts:
    *   Board Name: `DevAcademyL3E1` (Human readable)
    *   Board ID: `devacademyl3e1` (Auto-generated)
    *   SDK Version: Select your v2.7.0+ version.
    *   SoC: `nrf52833_qiaa` (Select exact variant).
    *   Board Root: `C:\my_boards` (Directory from step 1).
    *   Vendor: `nordic` (Or your company name, no spaces).
4.  **Add Board Root to VS Code Settings:** File -> Preferences -> Settings -> Extensions -> nRF Connect -> Board Roots -> Add Item -> Enter `C:\my_boards`.
5.  **Open Custom Board Folder:** File -> Open Folder -> `C:\my_boards\devacademyl3e1`.
6.  **Edit `devacademyl3e1_defconfig`:** Add default Kconfigs for basic functionality based on DK schematic (assuming interface MCU provides these):
    ```kconfig
    # Append these lines
    CONFIG_USE_SEGGER_RTT=y
    CONFIG_GPIO=y
    CONFIG_SERIAL=y
    CONFIG_CONSOLE=y
    CONFIG_UART_CONSOLE=y
    ```
7.  **Create/Build Hello World:** Create a new application from the Hello World sample. Add a build configuration targeting your *new* custom board (`devacademyl3e1/nrf52833`). Build it (it might not run correctly yet, but building enables the DeviceTree Visual Editor).
8.  **Populate Devicetree using Editor/Text:**
    *   Open DeviceTree Visual Editor (Actions Panel).
    *   Open `devacademyl3e1.dts` and `devacademyl3e1-pinctrl.dtsi` in text editor.
    *   **Enable GPIO/GPIOTE:** Add to `devacademyl3e1.dts`:
        ```devicetree
        &gpiote { status = "okay"; };
        &gpio0 { status = "okay"; };
        &gpio1 { status = "okay"; }; // Assuming nRF52833 has gpio1
        ```
    *   **Define LEDs (P0.13-P0.16, Active Low):** Add inside root (`/`) node in `devacademyl3e1.dts`:
        ```devicetree
            leds {
                compatible = "gpio-leds";
                led0: led_0 { gpios = <&gpio0 13 GPIO_ACTIVE_LOW>; label = "Green LED 0"; };
                led1: led_1 { gpios = <&gpio0 14 GPIO_ACTIVE_LOW>; label = "Green LED 1"; };
                led2: led_2 { gpios = <&gpio0 15 GPIO_ACTIVE_LOW>; label = "Green LED 2"; };
                led3: led_3 { gpios = <&gpio0 16 GPIO_ACTIVE_LOW>; label = "Green LED 3"; };
            };
        ```
    *   **Define Buttons (P0.11, P0.12, P0.24, P0.25, Active Low, Pull-up):**
        *   Add `#include <zephyr/dt-bindings/input/input-event-codes.h>` at top of `devacademyl3e1.dts`.
        *   Add inside root (`/`) node in `devacademyl3e1.dts`:
            ```devicetree
            buttons {
                compatible = "gpio-keys";
                button0: button_0 { gpios = <&gpio0 11 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>; label = "Push button 0"; zephyr,code = <INPUT_KEY_0>; };
                button1: button_1 { gpios = <&gpio0 12 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>; label = "Push button 1"; zephyr,code = <INPUT_KEY_1>; };
                button2: button_2 { gpios = <&gpio0 24 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>; label = "Push button 2"; zephyr,code = <INPUT_KEY_2>; };
                button3: button_3 { gpios = <&gpio0 25 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>; label = "Push button 3"; zephyr,code = <INPUT_KEY_3>; };
            };
            ```
    *   **Configure UART0 (P0.06=TX, P0.08=RX, P0.05=RTS, P0.07=CTS):**
        *   Add to `devacademyl3e1.dts`:
            ```devicetree
            &uart0 {
                compatible = "nordic,nrf-uarte";
                status = "okay";
                current-speed = <115200>;
                pinctrl-0 = <&uart0_default>;
                pinctrl-1 = <&uart0_sleep>;
                pinctrl-names = "default", "sleep";
            };
            ```
        *   Add inside `&pinctrl` node in `devacademyl3e1-pinctrl.dtsi`:
            ```devicetree
            uart0_default: uart0_default { /* Same as nRF52833 DK */ ... };
            uart0_sleep: uart0_sleep { /* Same as nRF52833 DK */ ... };
            ```
            *(Copy exact content from nRF52833 DK pinctrl file or exercise solution)*
        *   Add chosen properties inside `/ { chosen { ... } };` in `devacademyl3e1.dts`:
            ```devicetree
            zephyr,console =  &uart0;
            zephyr,shell-uart =  &uart0;
            zephyr,uart-mcumgr = &uart0; // If needed
            ```
    *   **Configure I2C0 (P0.26=SDA, P0.27=SCL):**
        *   Add to `devacademyl3e1-pinctrl.dtsi`: `i2c0_default`, `i2c0_sleep` definitions (copy from DK/solution).
        *   Add to `devacademyl3e1.dts`:
            ```devicetree
            &i2c0 { status = "okay"; pinctrl-0 = <&i2c0_default>; ... };
            ```
    *   **Configure SPI1 (P0.31=SCK, P0.30=MOSI, P1.08=MISO):**
        *   Add to `devacademyl3e1-pinctrl.dtsi`: `spi1_default`, `spi1_sleep` definitions (copy from DK/solution).
        *   Add to `devacademyl3e1.dts`:
            ```devicetree
            &spi1 { status = "okay"; pinctrl-0 = <&spi1_default>; ... };
            ```
    *   **Configure PWM0 (Output on LED0 pin P0.13):**
        *   Add to `devacademyl3e1-pinctrl.dtsi`: `pwm0_default`, `pwm0_sleep` definitions (copy from DK/solution, include `nordic,invert;` if needed for LED).
        *   Add to `devacademyl3e1.dts`:
            ```devicetree
            &pwm0 { status = "okay"; pinctrl-0 = <&pwm0_default>; ... };
            ```
        *   Add PWM LED definition inside root (`/`) node in `devacademyl3e1.dts`:
            ```devicetree
            pwmleds {
                compatible = "pwm-leds";
                pwm_led0: pwm_led_0 {
                    pwms = <&pwm0 0 PWM_MSEC(20) PWM_POLARITY_INVERTED>; // Channel 0, 20ms period, inverted for active-low LED
                };
            };
            ```
    *   **Add Aliases:** Add standard aliases inside `/ { aliases { ... } };` in `devacademyl3e1.dts`:
        ```devicetree
        led0 = &led0; led1 = &led1; led2 = &led2; led3 = &led3;
        pwm-led0 = &pwm_led0;
        sw0 = &button0; sw1 = &button1; sw2 = &button2; sw3 = &button3;
        bootloader-led0 = &led0; mcuboot-button0 = &button0; mcuboot-led0 = &led0;
        watchdog0 = &wdt0; // If watchdog is enabled
        ```
9.  **Testing:**
    *   Build and flash **Hello World** for `devacademyl3e1/nrf52833`. Verify console output.
    *   Build and flash **Button sample** (`zephyr/samples/basic/button`). Verify LED1 toggles on Button 1 press and console output appears.
    *   Build and flash **PWM LED sample** (`zephyr/samples/basic/pwm_blinky`). Verify LED1 fades/blinks and console output appears.
    *   Build and flash a **BLE sample** (e.g., `peripheral_uart`). Verify advertising/connection. (Radio node usually enabled in SoC DTS).
    *   Test I2C/SPI with external hardware following relevant lessons/samples.

The solution for this exercise can be found in the GitHub repository for this course.

---

## Exercise 2 – Custom board for a multi-core & TF-M capable SoC/SiP

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0 - HWMv2)*

Create a custom board definition (`DevAcademyL3E2`) based on nRF9151 DK, demonstrating multi-target support (with/without TF-M). This involves copying and renaming existing DK files.

### Exercise steps

#### Preparing the template

1.  Create root directory `C:\my_boards`.
2.  **Copy DK Folder:** Copy the entire `<sdk_path>/zephyr/boards/nordic/nrf9151dk` folder into `C:\my_boards`.
    > **Important**: If your target SiP/SoC is different (e.g., nRF5340), copy the corresponding DK folder (e.g., `nrf5340dk`).
3.  **Add Board Root to VS Code Settings** (as done in Exercise 1, Step 3).
4.  **Target Name:** We will name the board `DevAcademyL3E2` (human), `devacademyl3e2` (ID). Targets will be `devacademyl3e2/nrf9151` and `devacademyl3e2/nrf9151/ns`.
5.  **Rename Files and Content:**
    5.1 **Rename Folder:** Rename `C:\my_boards\nrf9151dk` to `C:\my_boards\devacademyl3e2`.
    5.2 **Open Folder:** Open `C:\my_boards\devacademyl3e2` in VS Code (ensure it's the only folder in the workspace).
    5.3 **Rename Files:** Rename all files starting with `nrf9151dk_...` to `devacademyl3e2_...`. Rename `Kconfig.nrf9151dk` to `Kconfig.devacademyl3e2`.
    5.4 **Delete `doc` folder.**
    5.5 **Replace Content (Case Sensitive):**
        *   Edit -> Replace in Files (Ctrl+Shift+H).
        *   Search for `nrf9151dk` (Match Case ON), Replace with `devacademyl3e2`. Click Replace All.
        *   Search for `NRF9151DK` (Match Case ON), Replace with `DEVACADEMYL3E2`. Click Replace All.
        *   Search for `nRF9151 DK` (Match Case ON), Replace with `DevAcademyL3E2`. Click Replace All.
        *(This updates `board.yml`, includes, Kconfig symbols, CMake files, comments etc.)*

#### Adjusting the template to match your schematic / Software Configuration

6.  **Modify Files:** Now that you have a renamed template, modify the `.dts`, `-pinctrl.dtsi`, `_defconfig`, and potentially `Kconfig.defconfig` files within `C:\my_boards\devacademyl3e2` to match the *actual* hardware schematics and desired default software configurations for *your* custom `DevAcademyL3E2` board. Use the principles from Exercise 1 and the multi-target/TF-M concepts covered earlier (e.g., ensuring correct partition selection in `Kconfig.defconfig`, enabling `TRUSTED_EXECUTION_NONSECURE` in the `_ns_defconfig`, etc.).

#### Testing

7.  **Build and Flash Samples:**
    *   Create new applications based on samples.
    *   In the "Add Build Configuration" window, you should now see your custom board `devacademyl3e2` listed under "Custom Boards", with its targets (`devacademyl3e2/nrf9151`, `devacademyl3e2/nrf9151/ns`).
    *   **Test Serial Console:** Build/flash Hello World for both targets (`.../ns` and non-`ns`). Verify output. Note the TF-M child image build for the `ns` target.
    *   **Test LEDs/Buttons:** Build/flash Button sample for `.../ns` target. Verify functionality.
    *   **Test PWM:** Build/flash PWM LED sample for `.../ns` target. Verify functionality.
    *   **Test Modem:** Build/flash AT Client or AT Monitor sample for `.../ns` target (required for modem samples). Verify AT commands work.
    *   **Test I2C/SPI:** Use external hardware and relevant samples/lessons.

    > **Important**: For complex samples that include their own `boards/` overlays/configs (like `nrf_cloud_multi_service`), you may need to copy the existing `nrf9151dk_nrf9151_ns.conf/.overlay` files within that *sample's* `boards/` directory and rename the copies to match your custom board target (e.g., `devacademyl3e2_nrf9151_ns.conf/.overlay`) for the sample to build correctly for your board.

The solution for this exercise can be found in the GitHub repository for this course (`l3/l3_e2_sol` select version).# Sysbuild

## Overview

Sysbuild is a high-level build system that simplifies the management of complex multi-image builds. It is an improved and extensible build system for multi-image builds, replacing the nRF Connect SDK-specific Multi-image builds system we had in older nRF Connect SDK versions.

Sysbuild became available in nRF Connect SDK version 2.7.0 and is enabled by default for all nRF Connect SDK projects from version 2.8.0 onwards.

In this lesson, we will provide an overview of Sysbuild, highlighting its use cases and the default images provided by the SDK. We will explore the situations where Sysbuild is essential and learn how to configure it within an application. This will include setting Sysbuild-specific Kconfig options in the relevant files. We will explain the structure and purpose of key configuration files, as well as the directory used for image overlays. Furthermore, we will discuss memory partitioning schemes in nRF Connect SDK and cover how to configure and manage partitions using the Partition Manager. Additionally, we will provide guidance on utilizing tools like the nRF Kconfig GUI in VS Code to assist with Sysbuild configuration.

In the hands-on portion of this lesson, we will practice both adding/configuring an SDK-provided Sysbuild image (MCUboot bootloader) and creating a custom image from scratch.

---

## Sysbuild explained

This lesson aims to explain Sysbuild, its use case, and how to use it. Sysbuild became available in nRF Connect SDK version 2.7.0 and is enabled by default for all nRF Connect SDK projects from version 2.8.0 onwards.

### Concepts

To quote [Sysbuild documentation](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/index.html): “Sysbuild is a higher-level build system that can be used to combine multiple other build systems together. It is a higher-level layer that combines one or more Zephyr build systems and optional additional build systems into a hierarchical build system.”

In other words, Sysbuild runs before the normal Zephyr build system and helps handle multiple build processes as a single, unified build.

Sysbuild replaces the older, nRF Connect SDK-specific "Multi-image builds" system. Key advantages include:

*   Clear separation of files/boundaries between images.
*   Ability to seamlessly configure images separately or combined.
*   Compatibility with upstream Zephyr & integration with HWMv2 (Hardware Model v2, covered in Lesson 3).

### Use cases

In the nRF Connect SDK, Sysbuild is primarily used for:

1.  **Multi-core Applications:** Building separate images for different cores on a single SoC (e.g., application core and network core on nRF5340, or application core and FLPR core on nRF54L15). Sysbuild manages the configuration and build process for all cores within a single project structure, simplifying development.
    *(Diagram description: Sysbuild managing builds for App Core and Network Core)*
2.  **Bootloaders:** Building a bootloader (like MCUboot) and an application image for the same core, ensuring they are placed correctly in memory and potentially merging them into a single flashable hex file.
    *(Diagram description: Sysbuild managing builds for Bootloader and Application for a single core)*

> **Note**: Since Sysbuild is enabled by default (from NCS v2.8.0), it's active even for single-image builds, although its multi-image management features are not utilized in that case.

See ["Migrating from multi-image builds to Sysbuild"](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/migration.html) for other potential use cases.

### Why do I need to know about Sysbuild?

While creating custom images is less common, developers frequently need to **configure existing images** provided by the SDK via Sysbuild.

As of nRF Connect SDK v2.9.0, default images include:

*   **Bootloaders:**
    *   MCUboot
    *   Nordic Secure Immutable Bootloader (NSIB)
*   **Network Core Images (for nRF5340 SoC):**
    *   nRF5340: Empty firmware
    *   HCI IPC
    *   Bluetooth: Host for nRF RPC Bluetooth Low Energy
    *   IEEE 802.15.4 over RPMsg
    *   IPC radio firmware

These images often require project-specific configuration (e.g., disabling MCUboot logging for release builds). Understanding Sysbuild configuration is necessary for this.

Sysbuild Kconfig options (prefixed with `SB_CONFIG_`) can enable these default images. Configuration details are covered later.

### A high-level build system

Key rules for Sysbuild interaction:

*   Sysbuild configuration mainly affects Sysbuild itself.
*   Sysbuild can configure its child images (e.g., application, bootloader).
*   Images **cannot** configure Sysbuild or other images directly.

*(Diagram description: Arrows showing configuration flow: Sysbuild Config -> Sysbuild Features, Sysbuild Config -> App Config, Sysbuild Config -> Extra Image Config, Sysbuild Config -> Spawn New Images. No arrows originate from App or Extra Image.)*

### Documentation

*   [Configuring Sysbuild (NCS Docs)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/config.html)
*   [Bootloader Image IDs (NCS Docs)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/bootloaders.html#image-ids)
*   [Sysbuild Samples (NCS)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/samples/samples_sysbuild.html)
*   [Sysbuild Design (Zephyr Docs)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/build/sysbuild/design.html)
*   [Sysbuild Migration Guide (Zephyr Docs)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/migration.html)

---

## Sysbuild configuration

*(Information relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

This section explains how to configure Sysbuild within an application project.

### Sysbuild Kconfig

Sysbuild uses Kconfig symbols, similar to application configuration (`prj.conf`), but with specific rules:

*   **Prefix:** Sysbuild Kconfig symbols start with `SB_CONFIG_` (e.g., `SB_CONFIG_BOOTLOADER_MCUBOOT`).
*   **File:** Sysbuild Kconfig options are set in a file named `sysbuild.conf` located in the main application's root directory.

*(Diagram description: Folder structure showing `sysbuild.conf` alongside `prj.conf` and `CMakeLists.txt`)*

A list of common Sysbuild Kconfig options is in the [Migration Guide](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/migration.html). You can also explore options using `west build -t sysbuild_menuconfig` or the nRF Kconfig GUI in VS Code (by selecting the "(sysbuild)" entry in the APPLICATIONS view).

*(Diagram description: VS Code showing how to select the sysbuild context and open its Kconfig GUI)*

### Sysbuild configuration folder

The main application's root folder acts as the "home" for Sysbuild configuration for the entire project.

**Sysbuild Configuration Files:**

| File Path                     | Explanation                                    | Project Equivalent (for comparison) |
| :---------------------------- | :--------------------------------------------- | :---------------------------------- |
| `<main_app>/sysbuild.conf`    | Sets Sysbuild Kconfig options                  | `prj.conf`                          |
| `<main_app>/Kconfig.sysbuild` | Defines custom Sysbuild Kconfig symbols        | `Kconfig`                           |
| `<main_app>/sysbuild.cmake`   | Manages CMake logic for Sysbuild               | `CMakeLists.txt`                    |
| `<main_app>/sysbuild/`        | Directory for *overlaying* child image configs | N/A                                 |

This lesson covers `sysbuild.conf`, `sysbuild.cmake`, and the `sysbuild/` directory.

See the `zephyr/samples/sysbuild/hello_world` sample for a practical example.

### Image names

Each build target within Sysbuild has an **image name**.
*   The main application image typically uses the application's folder name (e.g., `hello_world`, `l8_e1`).
*   Extra images have defined names (e.g., `mcuboot`, `hci_ipc`, `custom_image`).
You can see the image names as subdirectory names within the main `build/` folder after building.

*(Diagram description: Build folder structure showing `build/hello_world/` and `build/mcuboot/`)*

### Image overlays and Kconfig fragments

The `<main_app>/sysbuild/` directory is used to **customize the configuration of extra (child) images** without modifying their source code.

**Methods for Customizing Child Images:**

1.  **Overlaying (Recommended):** Modifies the child image's existing configuration.
    *   **Kconfig:** Create `<main_app>/sysbuild/<image_name>.conf`. This file acts as a Kconfig fragment applied *on top of* the child image's default `prj.conf`.
    *   **Devicetree:** Create `<main_app>/sysbuild/<image_name>.overlay`. This file overlays the child image's base devicetree.

2.  **Overwriting (Less Common):** Completely replaces parts of the child image's configuration. *Use with caution.*
    *   Place files inside `<main_app>/sysbuild/<image_name>/`.
    *   `<...>/prj.conf`: Replaces the child image's base `prj.conf`. **Must exist** if using any other overwriting files below for that image.
    *   `<...>/app.overlay`: Replaces the child image's base devicetree overlay (if any).
    *   `<...>/boards/<board>.conf`: Board-specific Kconfig fragment *for the child image*.
    *   `<...>/boards/<board>.overlay`: Board-specific devicetree overlay *for the child image*.

See [Sysbuild Migration Guide -> Examples for MCUboot](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/build/sysbuild/migration.html#mcuboot) for more examples.

---

## Sysbuild – Partition Manager

### Partition Manager

Zephyr typically uses fixed partitions defined in the devicetree (`fixed-partitions` compatible). However, nRF Connect SDK often needs a more dynamic approach, especially for multi-image builds and DFU/FOTA. This is handled by the **Partition Manager**.

*   **Enabled by Default:** Partition Manager (`SB_CONFIG_PARTITION_MANAGER=y`) is enabled by default when Sysbuild is active.
*   **YAML Configuration:** Uses `.yml` files (instead of DTS) to define partition requirements and layout rules.
*   **Build-Time Generation:** Generates the final partition scheme based on enabled application features and image requirements.
*   **Sysbuild Level:** Partitioning defined by Partition Manager applies consistently across **all** images in the Sysbuild project, ensuring compatibility (no overlaps, correct addresses for linking, bootloader/app agreement). DTS partitioning must be consistent manually if used instead.

### Partitioning in nRF Connect SDK

Three main schemes:

1.  **Devicetree Fixed Partitioning:** Uses standard Zephyr `fixed-partitions`. Suitable for simple, single-image applications without DFU.
2.  **Dynamic Partitioning (Partition Manager):** Default for many NCS scenarios (nRF91+TF-M, nRF53, nRF52+DFU). Automatically creates partitions based on Kconfig flags (e.g., `CONFIG_NVS`, `CONFIG_BOOTLOADER_MCUBOOT`). Rules defined in `pm.yml` files within SDK subsystems/modules.
3.  **Static Partitioning (Partition Manager):** Uses a `pm_static.yml` file *in the application directory* to define a fixed, explicit partition layout. Overrides dynamic rules. Required for production DFU/FOTA firmware; ensures layout stability across builds. Used by default in some complex samples (Matter, Thingy:53).

### Why is partitioning important?

For multi-image builds (bootloader+app, multi-core), ensuring images don't overlap, are linked to the correct addresses, and agree on partition boundaries is critical. Partition Manager automates this consistency.

### Working with the Partition Manager

*   **View Layout:** Check `build/partitions.yml` after building, or use the VS Code Memory Report tool (available after build).
*   **CLI Report:** `west build -t partition_manager_report` (see [docs](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/scripts/partition_manager/partition_manager.html#report)).
*   **`pm.yml` Files:** Define partition requirements and default sizes. Found in SDK components (e.g., `nrf/samples/bootloader/pm.yml`, `nrf/subsys/partition_manager/`).
*   **Configuring Partitions:** Use Kconfig options defined in relevant `pm.yml` files (often prefixed `CONFIG_PM_PARTITION_SIZE_...`). Set these options in the Kconfig fragment for the *relevant image* (e.g., set `CONFIG_PM_PARTITION_SIZE_MCUBOOT` in `<main_app>/sysbuild/mcuboot.conf`). Searching `CONFIG_PM_` in Kconfig GUI helps, but includes Power Management options too.
*   **Static Configuration (`pm_static.yml`):** Create this file in the main application root to define a fixed layout. Copying `build/partitions.yml` is a good starting point.

---

## Exercise 1 – Configuring extra image

Enable and configure MCUboot (an SDK-provided Sysbuild image) in a basic project.

### Exercise steps

Open the exercise base code: `l8/l8_e1` (select version) using "Copy a sample".

1.  **Build and Flash Base:** Build for your board and flash. Verify the "Hello from DevAcademy..." log message appears. Note only one image (`l8_e1`) in the VS Code APPLICATIONS view.
2.  **Add MCUboot via Sysbuild:**
    2.1 Create `sysbuild.conf` in the project root (`l8/l8_e1/`).
    2.2 Enable MCUboot by adding to `sysbuild.conf`:
       ```kconfig
       # STEP 2.1 - Add MCUboot
       SB_CONFIG_BOOTLOADER_MCUBOOT=y
       ```
       > **Important (nRF7002 DK only):** Add a file `sysbuild/mcuboot.conf` and disable SPI NOR driver to avoid conflicts on this specific DK:
       > ```kconfig
       > # sysbuild/mcuboot.conf for nRF7002DK
       > CONFIG_SPI=n
       > CONFIG_SPI_NOR=n
       > ```
3.  **Pristine Build and Flash:** Perform a pristine build and flash. Observe the terminal: MCUboot logs appear first, followed by the application logs. Note the two images (`l8_e1` and `mcuboot`) now listed in the VS Code APPLICATIONS view.
4.  **Configure MCUboot Image:**
    4.1 Create the directory `l8_e1/sysbuild/`.
    4.2 Create the file `l8_e1/sysbuild/mcuboot.conf`.
    4.3 Add Kconfig options to `mcuboot.conf` to disable serial output from MCUboot:
       ```kconfig
       # STEP 4.1 - Disable anything on UART in MCUboot
       CONFIG_SERIAL=n
       # Optional: Also disable console and logging for smaller size
       # CONFIG_CONSOLE=n
       # CONFIG_LOG=n
       ```
5.  **Pristine Build and Flash:** Perform another pristine build and flash. Observe the terminal: Only the application logs should appear now; MCUboot logs are suppressed.
6.  **Verify Configuration (Optional):**
    *   Check generated config files: `build/mcuboot/zephyr/.config` (should show `CONFIG_SERIAL=n`), `build/l8_e1/zephyr/.config` (should show `CONFIG_SERIAL=y`), `build/zephyr/.config` (Sysbuild's own config).
    *   Use **nRF Kconfig GUI**:
        *   In VS Code APPLICATIONS view, click on `mcuboot (...)`.
        *   Open nRF Kconfig GUI (Actions view).
        *   Search for `CONFIG_SERIAL`. It should be **unchecked**.
        *   Switch context back to `l8_e1 (...)` in APPLICATIONS view.
        *   Open nRF Kconfig GUI again.
        *   Search for `CONFIG_SERIAL`. It should be **checked**.

---

## Exercise 2 – Adding custom image

Add a custom secondary image (`custom_image`) to run alongside the main application (`l8_e2`) on a multi-core device (nRF54L15 or nRF5340).

> **Requirements:** nRF54L15 DK or nRF5340 DK required.

### Exercise steps

The base code contains two separate application folders: `l8/l8_e2` (main app) and `l8/custom_image` (secondary app).

1.  **Build/Test Individual Apps:**
    1.1 Build `l8/l8_e2` targeting the *application core* (`.../cpuapp`). Flash and verify its "Hello from DevAcademy..." and LED toggle output.
    1.2 Build `l8/custom_image` *also targeting the application core* for testing. Flash and verify its Nordic logo and benchmark output. (Running directly on the secondary core is complex due to initialization dependencies).
2.  **Configure Sysbuild in Main App (`l8/l8_e2`):**
    2.1 Create `l8/l8_e2/sysbuild.cmake`. Add the `ExternalZephyrProject_Add` call to include `custom_image`, targeting the appropriate *secondary core*.
       *   **For nRF54L15 DK (FLPR Core):**
           ```cmake
           # l8/l8_e2/sysbuild.cmake
           cmake_minimum_required(VERSION 3.20.5)
           find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

           # Add custom_image targeting the FLPR core
           ExternalZephyrProject_Add(
             APPLICATION custom_image
             SOURCE_DIR ${APP_DIR}/../custom_image # Path relative to l8_e2
             BOARD nrf54l15dk/nrf54l15/cpuflpr     # Target FLPR core
           )
           ```
       *   **For nRF5340 DK (Network Core):**
           ```cmake
           # l8/l8_e2/sysbuild.cmake
           cmake_minimum_required(VERSION 3.20.5)
           find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

           # Add custom_image targeting the Network core
           ExternalZephyrProject_Add(
             APPLICATION custom_image
             SOURCE_DIR ${APP_DIR}/../custom_image # Path relative to l8_e2
             BOARD nrf5340dk/nrf5340/cpunet     # Target Network core
           )
           ```
       > **Important (Partition Manager):** For simplicity, this exercise disables Partition Manager. To enable it with Sysbuild, additional lines are needed in `sysbuild.cmake` to share partition info (see Sysbuild Hello World sample).
    2.2 Create `l8/l8_e2/sysbuild.conf` and disable Partition Manager:
       ```kconfig
       # l8/l8_e2/sysbuild.conf
       # STEP 2.2 - Disable the Partition Manager
       SB_CONFIG_PARTITION_MANAGER=n
       ```
3.  **Initialize Secondary Core from Application Core (`l8/l8_e2`):** The application core needs to start the secondary core.
    *   **For nRF54L15 DK (FLPR):**
        *   Apply the `nordic-flpr` snippet's DTS changes manually to the *application core's* overlay (`l8/l8_e2/boards/nrf54l15dk_nrf54l15_cpuapp.overlay`). This defines memory regions for FLPR code/data and enables the VPR peripheral. *(Copy the exact DTS nodes from the original exercise text Step 3.2)*.
        *   (No specific C code needed in `main.c` for basic FLPR start, the snippet handles it via DTS config).
    *   **For nRF5340 DK (Network):**
        *   The network core typically requires the Remote Procedure Call library (`CONFIG_NRF_RPC`) or similar IPC mechanism enabled in *both* cores' `prj.conf` files for communication and startup.
        *   The application core usually needs C code to explicitly release the network core from reset (e.g., using `<nrfx_clock.h>`, `<nrfx_reset_reason.h>`). Check nRF53 examples like Peripheral LBS or Peripheral UART for standard startup procedures. *(This step was omitted in the provided text but is generally required)*.
4.  **Build and Flash Main App:** Perform a **Pristine Build** of `l8/l8_e2` targeting the *application core* (`.../cpuapp`). Flash the resulting merged hex file.
    *   Observe the VS Code APPLICATIONS view showing both `l8_e2 (cpuapp)` and `custom_image (cpuflpr/cpunet)` under the build.
5.  **Test:**
    *   Open *two* serial terminals, one for each VCOM port associated with your DK (check Device Manager or `dmesg`).
    *   Reset the board.
    *   One terminal should show the `l8_e2` application core logs (LED toggling).
    *   The other terminal should show the `custom_image` secondary core logs (Nordic logo, benchmarks).

    > **Note**: By default, nRF53 Network core logs via `UART0`, FLPR via `UART30`. These are routed to different VCOM ports on the DKs. Custom logging pins require overlays in the `custom_image` project. Remember to reserve peripherals used by the secondary core in the application core's overlay (as shown for UART30 in the FLPR example).