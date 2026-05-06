# Bootloaders and DFU/FOTA

## Overview

The bootloader is a key part of microcontroller development, enabling both security and firmware updates. MCUboot is the default bootloader used in the Zephyr RTOS and is inherited as such by the nRF Connect SDK. In this lesson, we will go through generic bootloader concepts, MCUboot-specific concepts, and Device Firmware Updates (DFU) and Firmware Over the Air (FOTA) for MCUboot.

In the exercise section, we will cover how to add MCUboot to your project and how to configure MCUboot. In addition, we will cover some different methods of DFU, for the nRF52, nRF53, nRF54L, nRF91, and nRF70 Series.

---

## Bootloader basics

The first three topics on Bootloaders and DFU will cover general bootloader and DFU concepts.

To begin this step-by-step look at how a bootloader works, starting from non-volatile memory.

As a starting note, remember that while related, the **Bootloader** and **Device Firmware Updates (DFU)** are different.

### Non-volatile memory

Memory that is not erased when a chip is power cycled is called non-volatile memory (typically Flash memory). This memory is organized into registers (often 32-bit on nRF chips).

*(Diagram description: Representation of non-volatile memory as a grid)*

When an application is programmed onto a chip without a bootloader, it's stored starting from address `0x00000000`. When the chip powers on, it begins execution from this address (or technically, the reset vector at `0x00000004` on Arm Cortex-M, which points to the start). Often, the application doesn't fill the entire flash memory.

*(Diagram description: Flash memory layout showing application at the start, followed by empty space)*

### Bootloader

A basic bootloader does what its name implies: it runs at **Boot** time and **Loads** the application. The bootloader itself is a small, separate program stored in flash memory, typically at the beginning (address `0x00000000`). When the chip powers on, the bootloader runs first. Its primary job is to prepare the system and then transfer execution control to the main application, which is now located at a higher address in flash.

*(Diagram description: Flash memory layout showing Bootloader at the start, followed by the Application, then empty space)*

> **Note**: A bootloader is just a second application hex file running on the chip.

### Application verification

The bootloader, especially the initial one programmed, often cannot be updated easily and is referred to as an **Immutable Bootloader** (or First-Stage Bootloader). Because it's immutable and programmed by a trusted source, it forms a **Root of Trust**.

> **Note**: It's also possible to have second-stage *upgradable* bootloaders, but that's beyond this course scope. See [Bootloaders and Device Firmware Updates](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/app_dev/bootloaders_and_dfu/index.html).

This trusted bootloader can verify the integrity and authenticity of the main application before running it, typically using **public-key cryptography** (specifically digital signatures).

**Digital Signature Process:**

1.  **Key Pair Generation:** The developer generates a **private key** (kept secret) and a corresponding **public key**.
2.  **Public Key Embedding:** The public key is embedded within the bootloader code.
3.  **Signing:** The application firmware image is processed with the private key to generate a **digital signature**, which is appended to the image.
4.  **Verification:** At boot time, the bootloader uses the embedded public key to check if the application's signature is valid (i.e., created by the corresponding private key).

If verification succeeds, the bootloader knows the application is authentic (from the developer) and hasn't been tampered with. It then jumps to the application's entry point. If verification fails, the bootloader refuses to run the application, preventing potentially malicious or corrupted code execution.

*(Diagram description: Bootloader successfully verifying application signature vs. failing verification and not booting)*

> **Note**: Developers typically only need to generate the key pair and provide the private key to the build system (covered later). The signing and verification processes are handled automatically by tools (like `imgtool.py` for MCUboot) and the bootloader itself. Verification is enabled by default in NCS bootloaders.

---

## Device Firmware Update (DFU) essentials

Nordic Development Kits (DKs) usually have two main chips: the target nRF chip and an onboard debugger chip (often an nRF5340) which provides programming/debugging access via USB.

*(Diagram description: DK showing target nRF chip and onboard debugger chip)*

Production devices typically omit the onboard debugger. **DFU** is the mechanism for updating the firmware on the target nRF chip without requiring a physical debugger connection.

DFU can use various communication protocols. Let's consider UART first.

### DFU over UART from the bootloader

Can the DFU receiver code run in the bootloader or the application? Since the goal is to replace the application, and an application cannot overwrite itself while running, the DFU receiver code must run *before* the application starts, i.e., in the **bootloader**.

*(Diagram description: Bootloader + Application layout)*

The bootloader can be configured to enter a special "DFU mode" (often triggered by holding a button during reset) instead of immediately booting the application. In DFU mode, the bootloader listens for incoming firmware updates on a specific interface (like UART). An external entity (e.g., a PC) sends the new, signed application firmware image in chunks over UART. The bootloader receives these chunks and writes them to a designated area in flash memory. After the transfer is complete, the device resets. On the next boot, the bootloader verifies the newly received application image. If valid, it boots the new application.

This method is often called **Serial Recovery** (MCUboot's term) because it allows reprogramming the application even if the application itself is corrupted or non-functional, as long as the bootloader is intact.

*(Diagram description: Bootloader entering DFU mode, receiving firmware over UART, writing to Application slot)*

> **Note**: What is the empty space at the top of memory diagrams for? It's available for non-volatile storage (e.g., using NVS) if the application/bootloader doesn't use all available flash.

### DFU over UART from the application

Running complex communication drivers (like BLE or Wi-Fi) within the constrained bootloader environment can be impractical due to size limitations. An alternative is to handle the DFU reception in the main **application**.

However, the application still cannot overwrite itself directly. The solution involves using **multiple firmware slots** in flash memory:

1.  The currently running application (in the **primary slot**) receives the new firmware update image via UART (or another protocol).
2.  The application writes the received image to a separate, designated area in flash called the **secondary slot**.
3.  The application signals the bootloader (e.g., by setting a flag) that an update is ready and triggers a reset.
4.  On reboot, the bootloader detects the update request. It verifies the signature of the image in the secondary slot.
5.  If valid, the bootloader **moves** (or copies) the new image from the secondary slot to the primary slot, overwriting the old application.
6.  The bootloader then boots the newly installed application from the primary slot.

This is often called **dual-slot DFU**. Its main drawback is that it roughly halves the flash space available for the application itself, as space must be reserved for the secondary slot.

*(Diagram description: Application receiving update, writing to secondary slot. Bootloader then moving secondary to primary)*

### Dual slot DFU with swapping

A problem with the simple dual-slot approach: if the newly updated application is faulty and crashes, the device might be "bricked" because the application (which handles receiving updates) can no longer run.

To mitigate this, MCUboot (and similar bootloaders) often implement **swapping** with **revert capability**:

1.  Bootloader receives update request (new image is in secondary slot).
2.  Bootloader *copies* the *current* application from the primary slot to a temporary **swap area** (sometimes called a scratch partition, or it might cleverly use parts of the secondary slot).
3.  Bootloader copies the *new* application from the secondary slot to the primary slot.
4.  Bootloader marks the update as "pending" or "test".
5.  Bootloader boots the new application from the primary slot.
6.  The *new application* is responsible for verifying its own integrity and functionality. If successful, it sends a "confirm" command to the bootloader (e.g., by writing to a specific flash location).
7.  If the bootloader reboots and finds the image marked as "test" (not yet confirmed), *or* if the boot fails verification on startup, it **reverts** the process: it copies the *old* application back from the swap area to the primary slot, effectively rolling back the update.

This ensures that a faulty update doesn't permanently brick the device.

*(Diagram description: Dual-slot DFU showing temporary storage/swapping mechanism)*

*(Reference to David Brown's MCUboot swap algorithm videos)*

### Firmware Over The Air (FOTA)

DFU performed over a wireless protocol (Bluetooth LE, Wi-Fi, Cellular IoT LTE-M/NB-IoT) is commonly called **FOTA**.

Because wireless stacks are large, FOTA almost always uses the **dual-slot DFU from the application** method described above. The application handles the wireless communication to receive the update image, writes it to the secondary slot, and triggers the bootloader to perform the swap/validation process.

---

## MCUboot, and relevant libraries

*(Information relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

This section covers the specific bootloader and DFU libraries used in NCS.

Official documentation: [Bootloaders and Device Firmware Updates](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/app_dev/bootloaders_and_dfu/index.html).

### MCUboot

**MCUboot** is the default open-source bootloader used in Zephyr and NCS.
*   **Source:** Forked from Apache Mynewt, maintained by Zephyr Project, with downstream NCS version.
*   **Documentation:** [Using MCUboot in nRF Connect SDK](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/mcuboot/index.html).
*   **Enabling:** Add `SB_CONFIG_BOOTLOADER_MCUBOOT=y` to `sysbuild.conf`. This automatically adds MCUboot as a child image via Sysbuild and typically sets up a dual-slot partition layout by default (primary + secondary slots).
    *(Diagram description: Default dual-slot layout: MCUboot, Primary App, Secondary App)*
*   **Image Format:** DFU images must be signed and correctly formatted. The build system uses MCUboot's `imgtool.py` script automatically to generate update files (e.g., `app_update.bin`, `zephyr.signed.bin`). Use `west build -v ...` to see exact commands.
*   **Update Process (Dual Slot):**
    1.  New image received (by application or bootloader serial recovery) and written to `mcuboot_secondary` slot.
    2.  Device reset.
    3.  MCUboot checks the secondary slot.
    4.  If image is valid and flagged for update (**Test** or **Confirm**):
        *   **Test:** MCUboot swaps images (new->primary, old->secondary/scratch). Boots new image once. If not confirmed by the running application before next reset, MCUboot swaps back (reverts).
        *   **Confirm:** MCUboot swaps images permanently. Boots new image.
    5.  If no valid image/flag in secondary, MCUboot boots the image in the primary slot.

### Sysbuild and the Partition Manager

*   **Sysbuild:** Used to build MCUboot alongside the application (as covered in Lesson 8).
*   **Partition Manager:** Used to define memory partitions for MCUboot, primary slot, secondary slot, etc. (as covered in Lesson 8). Ensures consistency between bootloader and application views of memory.

### Libraries/tools related to DFU and FOTA

*   **MCUmgr:** A Zephyr subsystem providing device management services, including firmware updates and file system access, over various transports (Serial, BLE). Uses Simple Management Protocol (SMP). Kconfig options usually start with `CONFIG_MCUMGR_`.
    *   Device receiving commands = SMP Server.
    *   Device/PC sending commands = SMP Client.
*   **DFU Target (`dfu_target` library):** NCS-specific library that handles *writing* received firmware updates to the correct location (e.g., `mcuboot_secondary` slot for application updates, or directly to modem for modem updates). It does *not* handle the transport itself.
*   **FOTA Download (`fota_download` library):** NCS-specific library for downloading firmware images from a URL (typically HTTP/HTTPS) for internet-connected devices. Usually works in conjunction with DFU Target.

*(Diagram description: Flow showing FOTA Download -> DFU Target -> Flash Memory)*

MCUmgr handles both transport (Serial/BLE) and writing (via DFU Target/IMG Manager). FOTA Download handles transport (HTTP/HTTPS) and passes data to DFU Target for writing. Custom transports can also feed data to DFU Target manually.

### MCUboot and DFU documentation summary

*   [NCS Bootloaders and DFU Overview](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/app_dev/bootloaders_and_dfu/index.html)
*   [MCUboot Documentation (Upstream/Zephyr)](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/mcuboot/design.html)
*   [Using MCUboot in NCS](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/mcuboot/index.html)
*   Device Specific DFU Guides (e.g., [nRF52 FOTA](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/device_guides/working_with_nrf52/developing.html#fota-updates))
*   [Zephyr SMP Server Sample](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/samples/subsys/mgmt/mcumgr/smp_svr/README.html)
*   NCS Samples often include MCUboot/DFU options (e.g., Peripheral LBS, Matter Door Lock).
*   [NCS MCUboot Tests](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/tests/bootloader/mcuboot/README.html)
*   [NCS FOTA Download Library Docs](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/libraries/others/fota_download.html)
*   Cloud FOTA Guides (e.g., [nRF Cloud FOTA](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/nrf_cloud/nrf_cloud_fota.html), [AWS FOTA](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/aws/fota.html), [Azure FOTA](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/azure_iot_hub/fota.html))

### DFU transmission tools (SMP Clients)

*   **PC:**
    *   [MCUmgr CLI](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/guides/device_mgmt/mcumgr.html#mcumgr-cli) (Command line tool)
    *   **AuTerm** (Used in exercises for UART/USB) - GUI tool, requires separate download/setup.
*   **Mobile:**
    *   **nRF Connect Device Manager** (iOS/Android, used in BLE exercise)
    *   nRF Connect for Mobile (iOS/Android, also supports SMP)
*   **Cloud:** Cloud platform UI (e.g., nRF Cloud, AWS IoT Console) initiates downloads via FOTA Download library on device.
*   **nRF Device as Client:** Possible using `mcumgr smp_client` library (e.g., LwM2M Client sample). Not covered in this lesson.

---

## DFU for the nRF5340 SoC

The dual-core nRF5340 requires special handling for DFU:

*   **Network Core Bootloader:** Needs its own bootloader, `b0n` (Build Zero network core bootloader).
*   **Network Core Updates:** Application core cannot write directly to network core flash. Updates must be transferred from App core -> Net core using the **PCD (Peripheral CPU Dependant) library**.
*   **Update Methods:**
    1.  **Non-simultaneous:** Update one core at a time. App core update is standard MCUboot DFU. Net core update involves sending the net core image to the app core, which then transfers it via PCD to the net core's secondary slot. Net core's `b0n` handles the final swap. *Recommended only for serial DFU, can break App/Net core interface compatibility during FOTA.*
       *(Diagram descriptions: Non-simultaneous App core update, then Net core update)*
    2.  **Simultaneous:** Update both cores in a single DFU process. Requires an extra flash slot (`mcuboot_secondary1`). App core image goes to `mcuboot_secondary`, Net core image goes to `mcuboot_secondary1`. External flash is often used for these secondary slots due to size constraints. MCUboot uses a simulated `mcuboot_primary1` slot; when swapping the Net core image "into" this simulated slot, the image is actually transferred via PCD. *Recommended for FOTA.*
       *(Diagram description: Simultaneous update using external flash for secondary slots)*

Configuration details: [Simultaneous multi-image DFU](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/app_dev/bootloaders_and_dfu/multi_image_dfu.html). Exercises will cover both methods.

---

## Exercise 1 – DFU over UART

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Add MCUboot to the Blinky sample and perform DFU over UART using both Serial Recovery (from bootloader) and DFU from the application (via MCUmgr).

### Exercise prerequisites

*   **AuTerm:** Install from [releases page](https://github.com/uavcan/auterm/releases) (download binary, follow README).
*   **Configure AuTerm:**
    1.  Open AuTerm -> Config tab.
    2.  Select correct COM port for your DK under "Port".
*   **(Recommended) Disable DK Mass Storage:** Prevents interference with UART. Use J-Link Commander/JLinkExe:
    ```bash
    # Replace SEGGER_ID with your DK's ID (from VS Code Connected Devices)
    JLinkExe -device NRF52840_XXAA -if SWD -speed 4000 -autoconnect 1 -SelectEmuBySN <SEGGER_ID>
    # In J-Link prompt:
    MSDDisable
    exit
    ```
    Power-cycle the DK afterward. Re-enable later with `MSDEnable` if needed.

### Exercise steps

Open the exercise base code: `l9/l9_e1` (Blinky sample) using "Copy a sample".

1.  **Enable MCUboot (Single Slot for Serial Recovery):**
    1.1 In `sysbuild.conf`, add:
       ```kconfig
       # STEP 1.1 - Enable MCUboot
       SB_CONFIG_BOOTLOADER_MCUBOOT=y
       ```
    1.2 Also in `sysbuild.conf`, configure single-slot mode:
       ```kconfig
       # STEP 1.2 - Configure bootloader to use only one slot.
       SB_CONFIG_MCUBOOT_MODE_SINGLE_APP=y
       ```
2.  **Enable Logging for MCUboot:**
    2.1 Create directory `l9/l9_e1/sysbuild/`.
    2.2 Create file `l9/l9_e1/sysbuild/mcuboot.conf`. Add comments:
       ```kconfig
       # STEP 2.3 - Enable logging for MCUboot
       # STEP 3.1 - Enable Serial Recovery over UART
       # STEP 3.2 - Disable UART Console, since Serial Recovery uses UART peripheral
       # STEP 3.3 - Turn on an LED so we can see when Serial Recovery mode is active
       ```
    2.3 Add logging Kconfigs to `sysbuild/mcuboot.conf`:
       ```kconfig
       # STEP 2.3 - Enable logging for MCUboot
       CONFIG_LOG=y
       CONFIG_MCUBOOT_LOG_LEVEL_INF=y
       ```
    Build and flash. Check terminal for MCUboot logs before Blinky starts. Check Memory Report; should show only `mcuboot` and `mcuboot_primary` partitions.

3.  **Add Serial Recovery to MCUboot:**
    3.1 Enable serial recovery and UART transport in `sysbuild/mcuboot.conf`:
       ```kconfig
       # STEP 3.1 - Enable Serial Recovery over UART
       CONFIG_MCUBOOT_SERIAL=y
       CONFIG_BOOT_SERIAL_UART=y
       ```
    3.2 Disable UART console in MCUboot (conflicts with serial recovery) in `sysbuild/mcuboot.conf`:
       ```kconfig
       # STEP 3.2 - Disable UART Console, since Serial Recovery uses UART peripheral
       CONFIG_UART_CONSOLE=n
       ```
    3.3 Enable indication LED in `sysbuild/mcuboot.conf`:
       ```kconfig
       # STEP 3.3 - Turn on an LED so we can see when Serial Recovery mode is active
       CONFIG_MCUBOOT_INDICATION_LED=y
       ```
    3.4 **Configure Button/LED:** Create `sysbuild/mcuboot.overlay`. Add aliases to map physical Button 2 and LED 2 to MCUboot's recovery button/LED:
       ```devicetree
       /* STEP 3.4 - Configure button and LED for Serial Recovery */
       / {
         aliases {
           mcuboot-button0 = &button1; /* Button 2 on DK -> button1 alias */
           mcuboot-led0 = &led1;     /* LED 2 on DK -> led1 alias */
         };
       };
       ```
       *(Note: Button/LED numbering might differ on nRF54L15 DK)*

#### Test Serial Recovery

4.  **Build and Flash** (Pristine build recommended).
    4.1 **Enter Recovery Mode:** Hold Button 2 while resetting the DK. LED 2 should turn ON, indicating recovery mode.
    4.2 **Connect AuTerm:** Open AuTerm -> MCUmgr tab -> Click Connect. Verify connection status.
    4.3 **List Images:** Click Images -> Get -> Go. Should list the current image in slot 0.
    4.4 **Prepare Update:** Modify `main.c` (e.g., change `SLEEP_TIME_MS` to 100). **Rebuild** the project (do NOT flash).
    4.5 **Upload Update:** In AuTerm -> Upload tab:
        *   Browse to `build/l9_e1/zephyr/app_update.bin`.
        *   Select action: "No action" (single slot doesn't use Test/Confirm).
        *   Click Upload.
    4.6 **Reset DK:** Use the reset button or MCUmgr -> OS -> Reset -> Go in AuTerm. Observe the changed LED blink rate.

#### DFU over UART from the application

5.  **Add DFU from Application:**
    5.1 **Switch back to Dual Slot:** In `sysbuild.conf`, comment out or set to `n`:
       ```kconfig
       # SB_CONFIG_MCUBOOT_MODE_SINGLE_APP=y
       # OR
       SB_CONFIG_MCUBOOT_MODE_SINGLE_APP=n
       ```
    5.2 Add MCUmgr Kconfigs to **`prj.conf`** (main application config):
       ```kconfig
       # STEP 5.2 - Enable mcumgr DFU in application
       CONFIG_MCUMGR=y
       CONFIG_MCUMGR_GRP_OS=y
       CONFIG_MCUMGR_GRP_IMG=y
       CONFIG_MCUMGR_TRANSPORT_UART=y
       # Dependencies (ensure these are enabled)
       CONFIG_NET_BUF=y
       CONFIG_ZCBOR=y
       CONFIG_CRC=y
       CONFIG_FLASH=y
       CONFIG_IMG_MANAGER=y
       CONFIG_STREAM_FLASH=y
       CONFIG_FLASH_MAP=y
       CONFIG_BASE64=y
       ```
    5.3 **Build and Flash** (Pristine recommended). Start DK normally (no button hold).
    5.4 **Test Application DFU:**
        *   Connect AuTerm (MCUmgr tab -> Connect).
        *   List images (Images -> Get -> Go). Should show image in slot 0 (active) and slot 1 (empty).
        *   Modify `main.c` again (e.g., `SLEEP_TIME_MS = 500`). Increment `VERSION_MINOR` in the `VERSION` file to `1`.
        *   **Pristine Build** (do NOT flash).
        *   Upload `build/l9_e1/zephyr/app_update.bin` using AuTerm -> Upload tab.
        *   Select action: **Test**. Click Upload.
        *   List images again. Slot 1 should now contain the new version, flagged pending.
        *   Reset DK (AuTerm OS -> Reset or button). MCUboot performs the swap.
        *   List images. New version should be in slot 0 (active), old in slot 1. Verify new blink rate.
        *   Confirm image: Images -> Set State -> Enter hash of image 0 -> Select Confirm -> Go. This prevents revert on next reset.
        *   (Optional) Test revert: Upload another version (e.g., v1.2) with "Test", reset, *do not confirm*, reset again. Observe it reverts to v1.1.

#### nRF5340 update

*   The steps above update the **application core** only.
*   To update the **network core** using DFU from the application (non-simultaneous):
    *   Build the network core image separately (targeting `.../cpunet`).
    *   Generate the DFU package for the network core: `build/.../cpunet/zephyr/signed_by_mcuboot_and_b0_ipc_radio.bin`.
    *   Upload *this* file using AuTerm (still connected to the application core's UART). MCUmgr/PCD handles transferring it to the network core.

---

## Exercise 2 – DFU with custom keys

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Sign DFU images using your own private key instead of the default development key.

*(Diagram description: Public/private key relationship for signing/verification)*

> **Warning**: Using the default MCUboot key in production allows *anyone* to update your device firmware! **Always use custom keys for production.**

### Using the Key Management Unit (KMU) on the nRF54L Series

nRF54L devices have a KMU for secure key storage.
*   **Option 1 (All Devices):** Embed public key in MCUboot image (standard method).
*   **Option 2 (nRF54L only, Recommended):** Store public key in KMU. Requires separate provisioning step.

This exercise covers both methods via tabs in the original text.

### Exercise steps

Assume using Exercise 1 setup.

1.  **Generate Custom Key:** Use `imgtool.py` (adjust SDK path).
    *   **Standard (ECDSA P256):**
        ```bash
        python <NCS_PATH>/bootloader/mcuboot/scripts/imgtool.py keygen -t ecdsa-p256 -k private_key.pem
        ```
    *   **nRF54L15 (Ed25519 for KMU):**
        ```bash
        python <NCS_PATH>/bootloader/mcuboot/scripts/imgtool.py keygen -t ed25519 -k private_key_ed25519.pem
        ```
    **Backup `private_key*.pem` securely! Losing it means losing DFU capability.**

2.  **Configure Project:** Set Sysbuild Kconfigs in `sysbuild.conf`.
    2.1 Set key file path (use `${APP_DIR}` for key in project folder):
       ```kconfig
       # STEP 2.1 - Add private key for MCUboot
       SB_CONFIG_BOOT_SIGNATURE_KEY_FILE="${APP_DIR}/private_key.pem"
       # For nRF54L15 KMU use: SB_CONFIG_BOOT_SIGNATURE_KEY_FILE="${APP_DIR}/private_key_ed25519.pem"
       ```
    2.2 Set matching key type:
       *   **Standard (ECDSA P256):**
           ```kconfig
           # STEP 2.2. - Configure key type
           SB_CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y
           SB_CONFIG_BOOT_SIGNATURE_TYPE_ED25519=n # Ensure others are disabled if set
           ```
       *   **nRF54L15 (Ed25519):**
           ```kconfig
           # STEP 2.2. - Configure key type
           SB_CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=n # Ensure others are disabled
           SB_CONFIG_BOOT_SIGNATURE_TYPE_ED25519=y
           # Enable KMU storage for public key
           SB_CONFIG_MCUBOOT_HW_KEY=y
           SB_CONFIG_MCUBOOT_HW_KEY_AREA_SIZE=0x400 # Adjust if needed
           ```

    2.3 **Provision Public Key to KMU (nRF54L15 DK Only):** This step requires manually writing the public key hash to the KMU using tools like `nrfjprog` or potentially a dedicated provisioning application *before* flashing the MCUboot/app built with `SB_CONFIG_MCUBOOT_HW_KEY=y`. This provisioning step is complex and **not fully detailed here**. Refer to nRF54L documentation/samples on KMU provisioning for the exact procedure. *Without provisioning, MCUboot built with `SB_CONFIG_MCUBOOT_HW_KEY` will fail verification.*

3.  **Pristine Build and Flash.** Observe build logs; the warning about default key should be gone, and your custom key file should be mentioned. Perform DFU (as in Ex 1, steps 5.3-5.4) to verify update works with the *correct* custom key.
4.  **Test Failure with Wrong Key:**
    4.1 Generate a *different* key (e.g., `do_not_use_this_key.pem`).
    4.2 Change `SB_CONFIG_BOOT_SIGNATURE_KEY_FILE` in `sysbuild.conf` to point to this *wrong* key.
    4.3 **Pristine Build** (generates `app_update.bin` signed with wrong key).
    4.4 Try to DFU this new `app_update.bin` onto the device (which still has MCUboot expecting the *original* key). MCUboot should reject the image during verification after reset, potentially logging an error.
5.  **Restore:** Change `SB_CONFIG_BOOT_SIGNATURE_KEY_FILE` back to the *original* key file, pristine build, and you should be able to DFU successfully again.

---

## Exercise 3 – DFU with external flash

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Configure MCUboot and the application to use external SPI/QSPI flash for the secondary update slot (`mcuboot_secondary`), maximizing internal flash for the application.

*(Table showing which DKs have QSPI vs SPI external flash)*

### Exercise steps

Open the exercise base code: `l9/l9_e3` (select QSPI or SPI folder based on DK).

1.  **Enable QSPI/SPI Drivers:**
    *   **Application (`prj.conf`):**
        ```kconfig
        # STEP 1.1 - Enable QSPI/SPI driver for Application
        # Use CONFIG_NORDIC_QSPI_NOR=y for QSPI boards
        # Use CONFIG_SPI=y and potentially CONFIG_FLASH_JESD216=y for SPI boards
        CONFIG_NORDIC_QSPI_NOR=y # Example for QSPI
        ```
    *   **MCUboot (`sysbuild/mcuboot.conf`):**
        ```kconfig
        # STEP 1.2 - Enable QSPI/SPI driver for MCUboot
        CONFIG_NORDIC_QSPI_NOR=y # Example for QSPI
        ```

2.  **Enable External Flash in Devicetree:**
    2.1 **Application Overlay (`app.overlay`):** Enable the external flash node (`&mx25r64` or `&gd25wb256`) and set the `nordic,pm-ext-flash` chosen property.
       ```devicetree
       /* STEP 2.1 - Add external flash to application */
       &mx25r64 { /* Or &gd25wb256 for nRF91x1 */
           status = "okay";
       };
       / {
           chosen {
               nordic,pm-ext-flash = &mx25r64; /* Or &gd25wb256 */
           };
       };
       ```
    2.2 **MCUboot Overlay (`sysbuild/mcuboot.overlay`):** Add the *exact same* nodes as in 2.1.
       ```devicetree
       /* STEP 2.2 - Add external flash to MCUboot */
       &mx25r64 { status = "okay"; };
       / { chosen { nordic,pm-ext-flash = &mx25r64; }; };
       ```
    2.3 Build the project. Check Memory Report; external flash (`PM_EXT_FLASH`) should appear.

3.  **Configure Sysbuild (`sysbuild.conf`)**: Tell Partition Manager to place `mcuboot_secondary` in external flash.
    ```kconfig
    # STEP 3.1 - MCUboot should use external flash for secondary slot
    SB_CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY=y
    ```
4.  **Pristine Build.** Check Memory Report again. `mcuboot_secondary` should now reside in the `PM_EXT_FLASH` region. Note the increased sizes available for `mcuboot_primary`.
5.  **Increase MCUboot Sector Count:** External flash often uses larger sectors. Increase `CONFIG_BOOT_MAX_IMG_SECTORS` in `sysbuild/mcuboot.conf` to accommodate potentially larger application sizes in the secondary slot. (Value depends on flash chip and max expected app size, 512 is a large example).
    ```kconfig
    # STEP 4.1 - Increase number of sectors (adjust value as needed)
    CONFIG_BOOT_MAX_IMG_SECTORS=512
    ```
6.  **Test DFU:** Perform DFU over UART as in Exercise 1 (steps 5.3-5.4) to verify the external flash configuration works.

---

## Exercise 4 – DFU over USB

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Configure DFU using the SoC's native USB peripheral (requires DK with nRF USB connector, e.g., nRF5340 DK, nRF52840 DK). Uses CDC ACM (Virtual COM port over USB).

*(Table showing DK USB support)*
*(Diagram description: nRF5340 DK schematic showing USB peripheral connection)*

### Exercise steps

Open the exercise base code: `l9/l9_e4`.

#### USB configuration for Serial Recovery

1.  **Enable CDC ACM in MCUboot:** Add to `sysbuild/mcuboot.conf`:
    ```kconfig
    # STEP 1.1 - Configure serial recovery to use CDC_ACM (USB)
    CONFIG_BOOT_SERIAL_CDC_ACM=y
    # Optionally disable UART transport if not needed
    # CONFIG_BOOT_SERIAL_UART=n
    ```
2.  **Add CDC ACM node to MCUboot Devicetree:** Add to `sysbuild/mcuboot.overlay`:
    ```devicetree
    /* STEP 2.1 - Configure CDC ACM node referencing USB peripheral */
    &zephyr_udc0 { /* The USB device controller node */
        cdc_acm_uart0: cdc_acm_uart_0 { /* Node name can be arbitrary */
            compatible = "zephyr,cdc-acm-uart";
        };
    };
    ```
3.  **Build.** You might encounter a size error because USB drivers increase MCUboot size.
    *(Diagram description: Build error showing partition overflow)*
4.  **Increase MCUboot Partition Size:** If overflow occurs, increase size in `sysbuild/mcuboot.conf` (e.g., `0x10000` or more):
    ```kconfig
    # STEP 3.1 - Increase flash space for MCUboot
    CONFIG_PM_PARTITION_SIZE_MCUBOOT=0x10000
    ```
5.  **Test Serial Recovery over nRF USB:**
    5.1 **Pristine Build and Flash.**
    5.2 **Connect PC to nRF USB Port:** Disconnect Debugger USB, connect to the port labeled "nRF USB".
    5.3 Perform Serial Recovery DFU (Hold Button 2, reset, use AuTerm) connecting AuTerm to the *new* COM port enumerated by the nRF USB CDC ACM driver.

#### USB configuration for DFU from the application

6.  **Configure Application for USB CDC ACM:**
    6.1 **Overlay (`app.overlay`):** Add CDC ACM node (same as step 2.1):
       ```devicetree
       /* STEP 5.1 - Configure CDC ACM */
       &zephyr_udc0 {
           cdc_acm_uart0: cdc_acm_uart_0 {
               compatible = "zephyr,cdc-acm-uart";
           };
       };
       ```
    6.2 **Overlay (`app.overlay`):** Point `uart-mcumgr` chosen property to the CDC ACM node:
       ```devicetree
       /* STEP 5.2 - Choose CDC ACM for mcumgr transport */
       / {
           chosen {
               zephyr,uart-mcumgr = &cdc_acm_uart0;
           };
       };
       ```
    6.3 **Kconfig (`prj.conf`):** Enable USB device stack and dependencies:
       ```kconfig
       # STEP 5.3 - Enable USB subsystem
       CONFIG_USB_DEVICE_STACK=y
       CONFIG_UART_LINE_CTRL=y # Required by CDC ACM
       CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n # Initialize manually
       ```
    6.4 **Source Code (`main.c`):** Include USB header:
       ```c
       /* STEP 5.4 - Include header for USB */
       #include <zephyr/usb/usb_device.h>
       ```
    6.5 **Source Code (`main.c`):** Enable USB stack at runtime (e.g., in `main()`):
       ```c
       /* STEP 5.5 - Enable USB */
       if (IS_ENABLED(CONFIG_USB_DEVICE_STACK)) {
           ret = usb_enable(NULL);
           if (ret != 0) {
               LOG_ERR("Failed to enable USB");
               return 0; // Handle error
           }
           LOG_INF("USB initialized");
       }
       ```
7.  **Build and Flash.**
8.  **Connect PC to nRF USB Port.**
9.  **Test Application DFU:** Perform DFU using AuTerm (as in Ex 1, steps 5.3-5.4), connecting to the nRF USB CDC ACM COM port.

---

## Exercise 5 – FOTA over Bluetooth Low Energy

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Add Bluetooth LE FOTA capability to the Peripheral LBS sample using MCUmgr SMP service. Update using a mobile app.

*(Table showing BLE support on DKs)*

### Exercise steps

Open the exercise base code: `l9/l9_e5` (Peripheral LBS derivative) using "Copy a sample".

1.  **Test Base Sample:** Build, flash, and verify basic BLE LBS functionality using nRF Connect for Mobile or similar.
2.  **Add MCUboot and FOTA:**
    2.1 **Enable MCUboot:** Add to `sysbuild.conf`:
       ```kconfig
       # STEP 2.1 Enable MCUboot
       SB_CONFIG_BOOTLOADER_MCUBOOT=y
       ```
    2.2 **Enable BLE FOTA:** Add helper Kconfig to `prj.conf`:
       ```kconfig
       # STEP 2.2 - Enable FOTA over Bluetooth LE using NCS helper config
       CONFIG_NCS_SAMPLE_MCUMGR_BT_OTA_DFU=y
       ```
       This automatically selects necessary MCUmgr, transport, image manager, and other dependencies for BLE SMP service when `CONFIG_BT_PERIPHERAL` is enabled (which it is in LBS sample).
       > **Note**: For production, manually select the required underlying Kconfigs instead of using the `CONFIG_NCS_SAMPLE_...` helper. See the Kconfig help text for `NCS_SAMPLE_MCUMGR_BT_OTA_DFU` to see which options it enables. Consider enabling security `CONFIG_MCUMGR_TRANSPORT_BT_PERM_RW_AUTHEN`.

3.  **Pristine Build and Flash.**
4.  **Prepare Update Image:**
    4.1 Modify `main.c` (e.g., `RUN_LED_BLINK_INTERVAL` to 200).
    4.2 Modify `VERSION` file (e.g., `VERSION_MINOR = 1`).
    4.3 **Pristine Build** (Do NOT flash). Locate `build/l9_e5/zephyr/app_update.bin` (or `zephyr.signed.bin`) or `build/dfu_application.zip`. Transfer this file to your mobile device.
5.  **Update using nRF Connect Device Manager App:**
    5.1 Install **nRF Connect Device Manager** (iOS/Android).
    5.2 Open app. **Disable filter** (top right settings -> uncheck "Filter for compatible devices") to see the "Nordic_LBS" device.
    5.3 Connect to "Nordic_LBS".
    5.4 Go to **Image** tab (bottom bar).
    5.5 Click **Select file**, choose the transferred update file (`.bin` or `.zip`).
    5.6 Choose update mode (e.g., **Test & Confirm**). Click **Start**. Observe transfer progress.
       *(Diagram description: Screenshots of Device Manager app during update)*
    5.7 Device will reset after transfer. Reconnect to verify new behavior (faster blink). Check version in Image -> Advanced -> Read.

---

## Exercise 6 – FOTA over LTE-M/NB-IoT

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Perform FOTA on an nRF91 Series DK using nRF Cloud Device Management and the FOTA Download library over cellular.

Reference: [nRF91 FOTA Documentation](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/app_dev/bootloaders_and_dfu/nrf91_dfu.html).

This exercise uses the **FOTA Download** library integrated with the **nRF Cloud library**. The application connects to nRF Cloud; nRF Cloud notifies the device of available updates; the nRF Cloud library triggers the FOTA Download library to fetch the image via HTTPS; FOTA Download writes it to `mcuboot_secondary`; device reboots; MCUboot swaps.

### Exercise steps

Open the exercise base code: `l9/l9_e6` (nRF Cloud Multi-Service derivative) using "Copy a sample".

> **Disclaimer**: Base code is simplified. Compare with full `nrf/samples/cellular/nrf_cloud_multi_service` for production features.
> **Prerequisite**: DK must be provisioned to your nRF Cloud account (Cellular IoT Fundamentals L1E1).

1.  **Build and Flash Base:** Build for your nRF91 DK (`..._ns` target). Flash. Connect serial terminal. Verify connection to nRF Cloud logs.
2.  **Enable nRF Cloud FOTA:** Add to `prj.conf`:
    ```kconfig
    # STEP 2 - Enable FOTA support in nRF Cloud library
    CONFIG_NRF_CLOUD_FOTA=y
    ```
3.  **Pristine Build and Flash.**
4.  **Prepare Update Image:**
    4.1 Modify `VERSION` file (e.g., `VERSION_MINOR = 1`).
    4.2 Modify `main.c` slightly (e.g., change a log message) to confirm update.
    4.3 **Pristine Build** (Do NOT flash).
5.  **Setup FOTA in nRF Cloud:** (See [nRF Cloud FOTA Docs](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/nrf_cloud/nrf_cloud_fota.html))
    5.1 **Add Device to Group:** Ensure your DK is in a group (Device Management -> Groups).
    5.2 **Upload Bundle:** Go to Firmware Updates -> Bundles -> Add Bundle. Upload `build/dfu_application.zip`. Fill in name/version (e.g., `App_v1.1`).
    5.3 **Create Update:** Go to Firmware Updates -> Create FOTA Update. Fill name/description. Select the bundle just created. Select your device group or individual device. Click "Create Update" (leave "Deploy now" unchecked initially).
    5.4 **Monitor Device:** Connect serial terminal to the DK.
    5.5 **Deploy Update:** On the FOTA Update page in nRF Cloud, click "Deploy Update". Monitor nRF Cloud UI and device logs. The device should receive an MQTT notification, start downloading via HTTPS, log progress, and eventually report completion.
    5.6 **Reset:** After "Download complete" log, reset the DK. Observe MCUboot logs, then the application should boot with the changes (e.g., new version log). nRF Cloud library will automatically confirm the image. Verify updated version in nRF Cloud -> Devices -> `your_device` -> Device Info -> Firmware.
6.  **(Optional) Auto-Reboot:**
    6.1 Include `<zephyr/sys/reboot.h>` in `src/cloud_connection.c`.
    6.2 Add `sys_reboot(SYS_REBOOT_COLD);` inside the `case NRF_CLOUD_EVT_FOTA_DONE:` in `cloud_event_handler()`.
    6.3 Build, flash, prepare v1.2, upload bundle, create/deploy update. Observe automatic reboot after download.
7.  **(Optional) Modem FOTA:** Check current modem firmware version in nRF Cloud device info. If an update is available ([Modem FW Releases](https://www.nordicsemi.com/Products/Development-hardware/nRF9160-DK/Download#infotabs)), download the appropriate **delta update** file. Create a *Modem* update bundle in nRF Cloud using the delta file. Create and deploy the FOTA update. Process is similar to application FOTA. (Full modem updates require external flash configuration).

The solution is in the GitHub repo (`l9/l9_e6_sol`).

---

## Exercise 7 – FOTA over Wi-Fi

*(Instructions relevant for nRF Connect SDK v2.7.0 - v2.9.0)*

Perform FOTA on an nRF7002 DK using AWS IoT Core and the AWS IoT library over Wi-Fi.

Reference: [AWS FOTA Documentation](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/aws/fota.html).

This exercise uses the **AWS IoT library**, which has built-in support for triggering the **FOTA Download** library based on AWS IoT Jobs. FOTA Download fetches the image via HTTPS, writes to `mcuboot_secondary`, device reboots, MCUboot swaps.

### Exercise steps

Open the exercise base code: `l9/l9_e7` (AWS IoT Sample derivative) using "Copy a sample".

1.  **Configure Wi-Fi Credentials** in `prj.conf`:
    ```kconfig
    # STEP 1 - Configure the Wi-Fi credentials
    CONFIG_WIFI_CREDENTIALS_STATIC_SSID="<your_network_SSID>"
    CONFIG_WIFI_CREDENTIALS_STATIC_PASSWORD="<your_network_password>"
    ```
    Build and flash (`nrf7002dk/nrf5340/cpuapp/ns` target). Observe initial logs. It will fail to connect to AWS initially due to missing endpoint/certificates.

2.  **Set up AWS IoT Core:** (Requires AWS account)
    *   Log in to AWS Console -> IoT Core.
    *   Follow steps in [AWS IoT Setup Guide](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/aws/getting_started/index.html) or the brief steps below:
3.  **Get AWS IoT Endpoint:** In IoT Core -> Settings (left menu) -> Copy the "Endpoint" address under "Device data endpoint". Paste this into `prj.conf`:
    ```kconfig
    # STEP 3 - Add AWS IoT Endpoint
    CONFIG_AWS_IOT_BROKER_HOST_NAME="<paste_endpoint_here>"
    ```
    Build and flash again. Connection will still fail (error -22) due to missing certificates/Thing.
4.  **Create AWS IoT Thing and Certificates:**
    4.1 IoT Core -> Manage -> All Devices -> Things -> Create things -> Create single thing.
    4.2 Name your Thing (e.g., `academy_thing`). Click Next.
    4.3 Select "Auto-generate a new certificate". Click Next.
    4.4 **Create Policy:** Click "Create policy".
        *   Name: `academy_policy` (or similar).
        *   Policy document -> JSON.
        *   Paste permissive JSON policy (for development only - **secure properly for production!**):
            ```json
            {
              "Version": "2012-10-17",
              "Statement": [ { "Effect": "Allow", "Action": "iot:*", "Resource": "*" } ]
            }
            ```
        *   Click Create.
    4.5 Go back to the "Create thing" browser tab. Refresh policies if needed. Select `academy_policy`. Click "Create thing".
    4.6 **Download Certificates:** Download ALL files provided: Device certificate (`xxxx-certificate.pem.crt`), Private key (`xxxx-private.pem.key`), Public key (`xxxx-public.pem.key`), and Amazon Root CA 1 (`AmazonRootCA1.pem`). **Store these securely.** Click Done.
    4.7 Configure Thing Name in `prj.conf`:
        ```kconfig
        # STEP 4.2 - Add AWS Thing name
        CONFIG_AWS_IOT_CLIENT_ID_STATIC="academy_thing"
        ```
    4.8 **Copy Certificates:** Copy the *content* of the downloaded certificate files into the corresponding files in the project's `certs/` directory, replacing the dummy content:
        *   `AmazonRootCA1.pem` -> `certs/ca-cert.pem`
        *   `xxxx-certificate.pem.crt` -> `certs/client-cert.pem`
        *   `xxxx-private.pem.key` -> `certs/private-key.pem`
    4.9 **Build and Flash with Erase.** Device should now connect successfully to AWS IoT Core. Observe logs confirming connection and potentially shadow updates.

5.  **Perform FOTA with AWS IoT Core:**
    5.1 **Enable AWS FOTA** in `prj.conf`:
       ```kconfig
       # STEP 5.1 - Enable AWS FOTA
       CONFIG_AWS_FOTA=y
       # Use same security tag as MQTT connection
       CONFIG_AWS_FOTA_DOWNLOAD_SECURITY_TAG=CONFIG_MQTT_HELPER_SEC_TAG
       ```
    5.2 Build and flash again.
    5.3 **Prepare Update:** Modify `main.c` (e.g., change log message). Increment `CONFIG_AWS_IOT_SAMPLE_APP_VERSION` in `prj.conf` (e.g., to `"v1.0.1"`).
    5.4 **Build** (Do NOT flash).
    5.5 **Create FOTA Job:** Follow steps in [AWS FOTA: Creating a FOTA job](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/protocols/aws/fota.html#creating-a-fota-job). This involves:
        *   Uploading the firmware update file (`build/l9_e7/zephyr/app_update.bin`) to an AWS S3 bucket.
        *   Creating an AWS IoT Job document specifying the S3 location and target devices (your Thing ARN).
        *   Starting the Job.
    5.6 **Monitor:** Observe device logs. It should receive the job notification via MQTT, start downloading the update via HTTPS (using certificates), report completion, tag the image, and reboot automatically. MCUboot swaps, the new application runs and confirms itself.

The solution is in the GitHub repo (`l9/l9_e7_sol`).