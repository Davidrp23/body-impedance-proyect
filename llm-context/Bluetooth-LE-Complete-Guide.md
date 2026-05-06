# What is Bluetooth LE?

Bluetooth Classic is the version of Bluetooth you have most likely used before due to its prevalence in common items such as wireless headsets. It is quite evident that Bluetooth is a perfect fit for applications such as streaming music. The data throughput is high enough to support it without connection problems or packet loss, plus it’s very easy to use. You probably need to recharge your smartphone and your wireless speakers after some time, but that is not a problem in this kind of application.

However, for low-power wearables or massive IoT applications, frequent battery charging is not feasible, especially when such high data transfer speeds are not necessary. Therefore, starting from Bluetooth Core Specification version 4.0, the Bluetooth SIG (Special Interest Group) introduced Bluetooth Low Energy (LE), with the intention of making it a key enabler for low-power IoT applications.

## Bluetooth LE features

Bluetooth LE, as its name implies, focuses on achieving low energy consumption by sacrificing data rate. Sacrificing data rate refers to two mechanisms here. Firstly, data packets are made smaller, ranging from 27 to 251 bytes. Secondly, data is being sent as seldom as possible to avoid long radio-on times, which is a significant factor in power consumption. This makes Bluetooth LE more suitable for battery-operated devices that need to operate on minimal power and only send small bursts of data.

Bluetooth LE differs from Bluetooth Classic in other aspects as well, such as supported topologies and node types. This is because Bluetooth LE was intended for completely different use cases than Bluetooth classic, therefore different network topologies were necessary.

The table below summarizes some of the key aspects of Bluetooth LE.

| Feature                                              | Value                                     |
| :--------------------------------------------------- | :---------------------------------------- |
| Operating band                                       | 2400 MHz – 2483.5 MHz<br/>~ 2.4 GHz        |
| Channel bandwidth                                    | 2 MHz                                     |
| Number of RF channels                                | 40                                        |
| Maximum transmit power                               | 20 dBm<br/>0.1 W                          |
| Maximum application data throughput                  | 1.4 Mbps                                  |
| Maximum range at reduced data rates (125 & 500 kbps) | ~1000 m                                   |
_Summary of Bluetooth LE specification_

> **Note**
> Range will always depend on a number of factors related to the software and hardware configuration of the devices used, as well as the specific environment where the devices operate. Therefore, it is very difficult to have a generalized precise range estimate.

However, an online range estimator like the one here [https://www.bluetooth.com/learn-about-bluetooth/key-attributes/range/](https://www.bluetooth.com/learn-about-bluetooth/key-attributes/range/) could give an acceptable estimate of what range to expect out of your Bluetooth LE devices, given the configuration indicated in the guide calculator.

A key advantage of Bluetooth Low Energy is its low cost when compared to other low-power personal area networks, making it attractive for applications requiring mass deployments.

The technology is also prevalent in smartphones (most smartphones support both Bluetooth Classic and Bluetooth LE), making it easy to test and prototype applications everywhere. In addition to the smartphone, one more Bluetooth LE device is needed to be able to test two-way communication. Since practically everyone has a smartphone, this reduces the cost and complexity required to conduct tests compared to other technologies where specific hardware is needed.

With Nordic Semiconductor’s wide variety of Bluetooth LE offerings, you will also get implementation flexibility, open-source documentation and continuous customer support. You can read more about Nordic Semiconductor’s Bluetooth LE offerings on our website.

## Bluetooth LE protocol stack

A deep understanding of all the individual layers of the protocol stack is not an absolute necessity for enabling and using Bluetooth LE in your application. Nonetheless, understanding the basics of the different layers and some of their main functions does help with having an overview of what’s happening under the hood with the Bluetooth LE stack. This is what we will cover in next section.

Certain layers, due to their importance, will be further explained in subsequent lessons.

The image below depicts the protocol stack architecture, showing which layers make up the Bluetooth LE host and which make up the Bluetooth LE controller.

At the top, you have the application. This is the layer that the user interacts with, through API’s, to make use of the Bluetooth LE protocol. Important parts of the application layer include profiles, services, and characteristics, which will be explained more thoroughly in the upcoming lessons. The next layers make up the host, which essentially determines how Bluetooth LE devices store and exchange data between each other. Lastly, the controller makes up the lower layers, with the most notable part being the physical radio which generates the radio waves and encodes the signals with the data you want to send.

### Host

The Bluetooth LE host consists of the following layers:

*   **Logical Link Control & Adaptation Protocol (L2CAP):** provides data encapsulation services to the upper layers.
*   **Security Manager Protocol (SMP):** defines and provides methods for secure communication.
*   **Attribute Protocol (ATT):** allows a device to expose certain pieces of data to another device.
*   **Generic Attribute Profile (GATT):** defines the necessary sub-procedures for using the ATT layer.
*   **Generic Access Profile (GAP):** interfaces directly with the application to handle device discovery and connection-related services.

The Zephyr Bluetooth Host implements all these layers and provides an API for applications.

### Controller

The Bluetooth LE controller is comprised of the following layers:

*   **Physical Layer (PHY):** determines how the actual data is modulated onto the radio waves, and how it is transmitted and received.
*   **Link Layer (LL):** manages the state of the radio, defined as one of the following – standby, advertising, scanning, initiating, connection.

The Bluetooth LE controller implementation we will be using in this course is the SoftDevice Controller, found in the nRF Connect SDK. Both the SoftDevice Controller and the Zephyr Bluetooth Host form the full Bluetooth LE protocol stack that is available in the nRF Connect SDK.

> **Important**
> The nRF Connect SDK contains an alternative controller implementation, the Zephyr Bluetooth LE Controller. However, we strongly recommend using the SoftDevice Controller, as it is specifically designed for the nRF52, nRF53 and nRF54 Series devices.

## GAP: Device roles and topologies

The Bluetooth LE protocol supports two different communication styles: connection-oriented communication and broadcast communication.

**Definition:**
**Connection-oriented communication:** When there is a dedicated connection between devices, forming bi-directional communication.
**Broadcast communication:** When devices communicate without establishing a connection first, by broadcasting data packets to all devices within range.

### Device roles

The GAP layer defines specific device roles for nodes in a Bluetooth LE network. These roles determine important aspects such as how the device advertises its presence, or how it scans and connects to other nodes.

Advertising and scanning refers to the process by which Bluetooth LE devices become aware of each other’s presence and connection possibilities. For two Bluetooth LE devices to connect to each other, one of them needs to advertise its presence and willingness to connect, while the other will scan for such devices.

**Definition:**
**Advertising:** The process of transmitting advertising packets, either just to broadcast data or to be discovered by another device.
**Scanning:** The process of listening for advertising packets.

### Central and peripheral

In the previous example, the device that advertises its presence and willingness to connect is acting as the peripheral. While the device that scans for advertisements is the central. If the peripheral’s advertisement packets are scanned by the central, the central can choose to initiate a connection by sending a connection request to the peripheral. The peripheral and the central are then said to have established a connection.

**Definition:**
**Central:** A device role that scans and initiates connections with peripherals.
**Peripheral:** A device role that advertises and accepts connections from centrals.

The central device can send connection requests to more than one peripheral simultaneously, and it assumes the role of the host in this connection. Peripherals can also accept connection requests from other centrals by restarting the advertising process after a connection has been established.

Since the central acts as the host, it is responsible for typical host-role duties such as connection management and much of the data processing. This means peripherals generally use less power than a central.

IoT devices that are resource constrained and require low-power are usually the peripheral device in a Bluetooth LE connection, while the central device is something like a mobile phone, which has more power.

> **Note**
> Since the most common use-case for our devices is as a peripheral, that is the connection topology we will examine in the exercises in this course.

### Broadcaster and observer

Sometimes devices only wish to broadcast information without being in a connection with another device. In this case, a special kind of peripheral, called a broadcaster, can send out advertisement packets, but without receiving any packets or allowing connection requests. The information that is broadcasted is included in the advertisement packets. A very good example of broadcasters are beacon devices. They only transmit information, without the need to connect to a specific device. On the other end, a special kind of central device called an observer, listens for the advertising packets, but without sending a connection request to initiate a connection.

**Definition:**
**Broadcaster:** A special kind of peripheral that broadcasts advertisement packets without accepting any connection requests.
**Observer:** A special kind of central that listens to advertising packets without initiating a connection.

For simplicity, we will stick to the peripheral/central device roles throughout this course, unless otherwise noted.

### Network topologies

Now that we have established the different roles of a Bluetooth LE device, let’s look at how the device roles are used in the different network topologies possible with Bluetooth LE.

#### Broadcast topology

In a broadcast topology, data transfer happens without the devices ever establishing a connection. This is done by using the advertisement packets to broadcast the data to any device that is in range to receive the packets. A peripheral (more specifically a broadcaster) advertises the data, and the central (more specifically an observer) will scan and read the data from the advertisement packets.

_An example of a broadcast topology_

This type of communication is commonly used in proximity beacons, in indoor navigation, and many other applications that require a low-power device to transmit small amounts of data to several devices simultaneously.

The advantage to a broadcast topology is that there is no limit to how many devices one can broadcast to. Anyone in range of the advertisement packets can receive the information. This is also much more power efficient than connection-oriented communication. However, due to the limited data available in the advertisement packets, the throughput is limited. There is also no acknowledgment from the receiving devices.

#### Connected topology

A connected network topology establishes a connection before data transfer occurs. Unlike the broadcast topology, the communication is now bidirectional.

> **Note**
> Although the Bluetooth LE specification technically does not limit the number of connections possible, there are bandwidth and hardware limitations that come with using small embedded devices.

Below is an example of a connected topology where a central has established communication with three peripherals, and one of those peripherals is already connected to two other centrals.

_An example of a connected topology_

The advantage of a connected topology is the increased throughput that comes with establishing a direct link before communication. Additionally, the communication is bi-directional, meaning that the central and peripheral can communicate with each other, as opposed to broadcasting, where the peripheral just broadcasts to the central without being able to receive anything back.

**More on this:**
With the introduction of Periodic Advertising with Responses (PAwR) in Bluetooth 5.4, bidirectional communication in connectionless mode is possible. This is however beyond the scope of this course.

#### Multi-role topology

A single device can also operate in multiple different roles simultaneously. For instance, the same device can act as a peripheral in one setting, and a central in another.

_Example of a multi-role topology_

This multi-role functionality is often used in systems where a device, let’s call it a hub, is receiving sensor data from multiple sensors, but also wants to forward this data to mobile phones. In this case, the hub can act as a central and connect to multiple sensors (peripherals), and can also act as a peripheral and transmit sensor data to one or more smartphones (centrals).

## ATT & GATT: Data representation and exchange

In the previous topic, we discussed the role that the GAP layer plays in defining how Bluetooth LE devices communicate with each other in both the advertisement and connection phases. The communication during advertising is only used for device discovery or for broadcasting data and is handled by the GAP layer itself. However, after establishing a connection, there is a need for bidirectional data exchange. This requires specific data structures and protocols tailored for these purposes.

The Attribute protocol (ATT) layer, and the Generic Attribute Profile (GATT) layer right above it, define how data is represented and exchanged between Bluetooth LE devices. The ATT and GATT layers are concerned with the phase after a connection has been established, as opposed to the GAP layer which takes care of the advertisement process which occurs before a connection is established.

### The Attribute Protocol

The ATT layer is the basis on which data is transmitted, received, and handled in the connection phase of Bluetooth LE devices. It is based on a client-server architecture where the server holds the data and can either send it directly to the client or the client can poll the data from the server.

The client and server roles defined in this layer are assigned independently from the peripheral and central roles defined in the GAP layer. So a central can be both a client or a server, and same with a peripheral. This all depends on the application use case and the nature of the data being transferred.

In most cases, the peripheral will be a server since the peripheral is the device that acquires data and holds it. Similarly, the central is typically the client as it is the device receiving said data from the server.

These roles are used by the GATT layer, so they are often referred to as the GATT server and the GATT client.

**Definition:**
**GATT server:** Device that stores data and provides methods for the GATT client to access the data.
**GATT client:** Device that accesses the data on the GATT server, through specific GATT operations which will be explained in Lesson 4.

The ATT layer defines a data structure called the attribute, which is used by the GATT server to store data. The server can hold a number of different attributes at the same time.

**Definition:**
**Attribute:** A standardized data representation format defined by the ATT protocol.

### The Generic Attribute Profile

The Generic Attribute Profile (GATT) layer sits directly on top of the ATT layer, and builds on it by hierarchically classifying attributes into profiles, services and characteristics. The GATT layer uses these concepts to govern the data transfer between Bluetooth LE devices.

_Example of a general profile with services and characteristics_

#### Profiles, services and characteristics

Let’s use a sensor device that measures the heart rate as an example. The heart rate value will be saved as an attribute, called the characteristic value attribute. There will also be another attribute holding metadata about the data stored in the value attribute, called the characteristic declaration attribute. These two attributes together form what’s called a characteristic. In this example, it’s the Heart Rate Measurement characteristic.

All characteristics are enclosed in what’s called a service. Services usually contain multiple characteristics. For this example, the Heart Rate Measurement characteristic is contained in the Heart Rate service. This service also has other characteristics, like the Body Sensor Location characteristic for example.

Then above this, a profile is one or more services that address the same use case. The Heart Rate service is found in the Heart Rate profile, along with the Device Information Service. The Device Information service contains characteristics such as the Manufacturer Name characteristic and the Firmware Revision characteristic.

_Example of the Heart Rate profile_

Before a client starts interacting with a server, the client is not aware of the nature of the attributes stored on that server. Therefore, the client first performs what’s called Service Discovery where it inquires from the server about the attributes.

> **Note**
> The complete list of GATT profiles defined by the Bluetooth SIG can be found [here](https://www.bluetooth.com/specifications/gatt/)। The Bluetooth specification also allows vendors to define their own profiles for use cases not covered by the SIG-defined profiles. (Assuming "here" was a placeholder for a link, I've made it a generic link to Bluetooth SIG GATT specifications).

## PHY: Radio modes

At the bottom of the Bluetooth LE stack is the physical layer (PHY). PHY refers to the physical layer radio specifications that govern the operation of the Bluetooth LE radio. This layer defines different modulation and coding schemes adopted by Bluetooth LE radio transmitters that affect things like the throughput of the radio. This in turn changes the battery consumption of the device or the range of the connection.

### 1M PHY

1M PHY, or 1 Megabit PHY, is the classic PHY supported by all Bluetooth LE devices. As its name implies, 1M PHY uses 1 megabit per second.

When initiating a connection between two Bluetooth LE devices, this is the mode that will be used, to begin with. Then the peers can request another mode if both devices support it.

### 2M PHY

2 Megabit PHY is a new mode introduced in Bluetooth v5.0. As the name implies, it effectively doubles the data rate to 2 megabit per second, or 2 Mbps. Since the data is transmitted at a higher data rate (faster), the radio needs to stay on for less time, decreasing battery usage. The downside is the decrease in receiver sensitivity which translates to less communication range.

### Coded PHY

While 2M PHY exists for users willing to sacrifice range for increased data rate, coded PHY was introduced to serve applications where users can achieve longer communication range by sacrificing data rate. Coded PHY uses coding schemes to correct packet errors more effectively, which also means that a single bit is represented by more than 1 symbol. Coded PHY uses 2 modes, S=2 and S=8. In the S=2 mode, 2 symbols represent 1 bit, therefore the data rate is 500 kbps. While in the S=8 mode, 8 symbols are used to represent a bit and the data rate becomes 125 kbps.

## Exercise 1: Testing a Bluetooth LE connection

In this exercise, we will be using the Bluetooth: Peripheral LBS sample, running on your Nordic board, to establish a Bluetooth LE connection between the board and your smartphone. The Peripheral LBS sample makes the Nordic board act as a Bluetooth LE peripheral, advertising its presence to your smartphone, which will act as the central.

When connected, the Nordic board will act as a GATT Server, exposing the LED Button Service (LBS) to your smartphone, the GATT Client. LBS has two characteristics, Button and LED. The GATT Client, in our case a smartphone, can write and read to these characteristics to control the LEDs and read the status of the button on the Nordic board. The Nordic board acts as the GATT server here.

For all exercises in this course, when building the sample application, you can use any of the boards listed under Hardware Requirements on the course page and their corresponding build targets.

> **Note**
> This course builds on the nRF Connect SDK Fundamentals course and focuses on Bluetooth Low Energy. You need to read Lesson 1 in the nRF Connect SDK Fundamentals to learn how to install nRF Connect SDK on your machine and build applications. Furthermore, completing the nRF Connect SDK Fundamentals course is strongly advised as it provides a comprehensive understanding of the nRF Connect SDK.

The exercises in this course assume you have a basic understanding of the nRF Connect SDK.

### Exercise steps

1.  **Build and flash the Peripheral LBS sample.**
    1.1 In Visual Studio Code, in the WELCOME panel, select “Browse samples” and search for “Bluetooth LE LED Button service”.
    _Select this sample, and it will appear under the APPLICATIONS panel._
    1.2 Add a build configuration and select whichever board you are using.
    1.3 Build and flash the application to your device.
    If this was successful, you should notice LED1 (LED0 on nRF54 DKs) blinking on your device.

2.  **Use your smartphone to test the application**
    2.1 Download nRF Connect for Mobile from your app store, and launch it on your smartphone.
    2.2 Turn on Bluetooth and Location services on your smartphone.

3.  **(optional) Open a terminal to view the log output from the application**
    The UART peripheral is gated through the SEGGER debugger/programmer chip (i.e interface MCU) to a USB-CDC virtual serial port that you can connect directly to your PC.
    _Connect to the COM port of your DK in VS Code by expanding your device under Connected Devices and selecting the COM port for the device. The number for the COM port may differ on your PC._

    > **Note**
    > When using the nRF5340 DK, you will have two COM ports, one for the application core and one for the network core. We want to view the output from the application core.

    Use the default settings 115200 8n1 rtscrs:off. Then reset the device to see the full log message.
    If the advertising was successful, your log output should look like this:
    ```
    *** Booting nRF Connect SDK ***
    Starting Bluetooth Peripheral LBS example
    I: 2 Sectors of 4096 bytes
    I: alloc wra: 0, f58
    I: data wra: 0, 140
    Bluetooth initialized
    Advertising successfully started
    ```
    LED1 (LED0 on nRF54 DKs) should also be blinking, indicating that the device is advertising.

    > **Note**
    > On the nRF54 DKs (Ex: nRF54L15 DK), the board’s LEDs and Buttons are labeled with PCB labels (PCB silkscreen) that start with 0 (LED0-LED3) and (BUTTON0-BUTTON3). In previous-generation development kits, the indexing starts with 1 (LED1-LED4) and (BUTTON1-BUTTON4).

4.  **Establish a connection to your Nordic board.**
    4.1 From the nRF Connect for Mobile app, press the SCAN button. Your smartphone will now act as a central device, scanning for any Bluetooth LE devices that are advertising in its presence.
    4.2 Several Bluetooth-enabled devices surrounding you will start appearing. Choose the one called Nordic_LBS and press CONNECT.
    4.3 Press Connect again if prompted with this view.
    In rare cases with some Android phones, you might need to first press the 3 dots at the top right corner, then press “Bond”, before connecting to the NORDIC_LBS device.
    4.4 You will know a connection has been established when LED2 (LED1 on nRF54 DKs) on your device is on.

5.  **Observe the interface on the app.**
    *   You can check that you are connected to the correct device.
    *   The services available on this device. Here we see the Nordic LED Button Service, since this is the sample we have flashed to the device.
    *   Inside that Service, there is a Characteristic called “Button“, or “Blinky Button State“. It reflects the status of button 1 on the Nordic board. Hence, its properties are “Read” and “Notify”. “Notify” refers to the case when the peripheral pushes data to the central. More on notifications in subsequent lessons.
    *   Inside that same Service, there is also another Characteristic called “LED” or “Blinky LED State“. It allows you to toggle LED 3 (LED2 on nRF54 DKs) on the Nordic board. Hence, its property is “WRITE”.

6.  **Read the status of button 1 using the “Button” Characteristic.**
    *   To receive and view the button 1 status(button 0 on nRF54 DKs), you need to view the “Value” tab in your “Button” Characteristic. This is done by pressing the single down-arrow icon.
    *   To enable notifications regarding this Characteristic to be pushed to your app, you need to press the icon with several down-arrows.
    *   Now, you should be able to see the status of button 1 (button 0 on nRF54 DKs) as released.

7.  **Observe the status of button 1 (button 0 on nRF54 DKs).**
    7.1 Press button 1 on your Nordic board.
    7.2 Observe the value shown below changes to “Button pressed”.

8.  **Toggle LED 3 (LED2 on nRF54 DKs).**
    8.1 Press the up arrow icon next to the LED characteristic.
    8.2 Write a value to the LED characteristic to turn it on. Select ON and then SEND to turn the LED on.
    8.3 Observe that LED3 is turned on.
    8.4 Turn off the LED by selecting OFF.# Advertising process

## Advertising and discovery

When a Bluetooth LE device is in an advertising state, it sends out advertising packets to announce its presence and potentially connect to another device. These advertising packets are sent out periodically at advertising intervals.

**Definition:**
**Advertising intervals:** The interval at which an advertising packet is sent. In the range of 20 ms to 10.24 s, with a step increase of 0.625 ms.

The smaller the advertising interval is, the more frequently the advertising packets are sent, and consequently, the more power is consumed. Therefore, the tradeoff here is power consumption vs. how fast the advertiser’s advertisement packets will be received by a scanner, commonly referred to as discoverability. To avoid packet collisions, a random delay of 0-10 ms is added before each advertisement packet. This ensures that devices with the same advertising interval do not end up with advertisement packet collisions all the time.

### Advertisement channels

Bluetooth LE devices communicate through 40 different frequency channels. These channels are divided into three primary advertisement channels and 37 secondary advertisement channels. Primary advertisement channels are the channels mainly used for advertisement purposes. Secondary advertisement channels can sometimes be used for advertisement purposes as well, but are mainly used for data transfer after establishing a connection. Throughout this course we will focus only on primary advertisement channels.

_Figure showing Bluetooth LE channels, highlighting primary advertising channels 37, 38, and 39._

To ensure a certain degree of redundancy, advertising packets are sent on all three primary advertising channels, channels 37, 38, and 39. Simultaneously, a scanning device will scan these three channels to look for advertising devices.

Since advertising packets are essential to establishing connectivity, the primary advertising channels are carefully chosen. Channels 37, 38, and 39, despite being consecutive numbers, are not actually neighboring channels, as you can see in the figure above. The separation between the three channels serves to avoid adjacent-band interference. Additionally, these three specific channels suffer the least from noise from other technologies using the ISM band, such as Wi-Fi.

### Scan interval and scan window

Similar to an advertising interval, a scan interval refers to how often a scanner will scan for advertisement packets. The scan window refers to the time the scanner spends scanning for packets, which in practice represents the duty cycle in which the device is scanning vs not scanning during each scan interval.

**Definition:**
**Scan interval:** The interval at which a device scans for advertisement packets.
**Scan window:** The time that a device spends scanning for packets at each scan interval.
Both range from 2.5 ms to 10.24 seconds with a step increase of 0.625 ms.

Since a device advertises on three different advertisement channels, the scanner will rotate through the advertisement channels, by switching the channel after each scan interval.

_Example of an advertiser (peripheral) and a scanner (central) illustrating scan intervals and windows._

Short advertising intervals lead to shorter discovery times but increase power consumption. Similarly, a higher scan window to scan interval ratio shortens the discovery time, but increases the power consumption. The time it takes to connect vs the power consumption will always be a tradeoff, but if you control both the scanner and the peripheral, you can choose intervals that work well together. Note that scanning in general uses a lot more power than advertising, and hence, the scanner/central is usually the device with the larger battery.

### Scan request and response

When a peripheral is advertising, a central can also choose to send a scan request to the peripheral, asking for additional information that is not included in the advertisement packets. If the scan request is accepted, the peripheral will respond with what’s called a scan response, also transmitted over the three primary advertisement channels.

**Definition:**
**Scan request:** A message sent by a central device to a peripheral to request additional information not present in the advertisement packet.
**Scan response:** A message sent as a response to a scan request, containing additional user data.

This is a way for the peripherals to send additional data without having to establish a connection with the central first. The peripheral can alternatively choose to send back an empty scan response if it has no more additional information to provide.

Another way to increase the amount of data a peripheral can advertise at once is with a feature called extended advertising. With this feature, the advertisement packets broadcast on the primary advertisement channels are pointing to supplementary information that is being advertised on the secondary advertisement channels. Extended advertising is beyond the scope of this course, and we will be focusing only on legacy advertisement.

## Advertising types

There are many different ways that a peripheral can advertise.

**Definition:**
**Connectable vs. non-connectable:** Determines whether the central can connect to the peripheral or not.
**Scannable vs. non-scannable:** Determines if the peripheral accepts scan requests from a scanner.
**Directed vs. undirected:** Determines whether advertisement packets are targeted to a specific scanner or not.

The type of advertisement being used is set in the advertisement packet. We will take a look at how to set the advertising type in the exercise section of this lesson.

There are four main advertisement types to cover in legacy advertisements, as well as a fifth one that is used in scan responses but will not be covered here.

*   **Scannable and connectable (ADV_IND):** This is the most common type of advertising. If a peripheral uses this type of advertising, it means that it is both scannable and connectable. This means that the peripheral is advertising its presence and allows the central to send a scan request and will respond with a scan response (hence scannable) which is followed by establishing a connection (hence connectable).
*   **Directed connectable (ADV_DIRECT_IND):** This type of advertisement is used for directed advertisement where the advertiser does not accept scan requests. It is directed, connectable but non-scannable. This can be used in cases where the advertiser already knows the scanner and just wants to reconnect quickly. A good example for this scenario is a Bluetooth mouse that has lost the connection with the PC and just wants to reconnect again. In this case, there is no need to accept scan requests and it is faster to send a directed advertisement packet to shorten the connection process.
*   **Non-connectable and scannable (ADV_SCAN_IND):** An advertiser using this type of advertisement will only accept scan requests, but will not allow establishing a connection with it (hence non connectable).
*   **Non-connectable and non-scannable (ADV_NONCONN_IND):** This type of advertisement does not accept scan requests nor does it accept establishing connections. A typical use-case for this type of advertisement is a beacon, where the device does not need to switch the radio to receiver mode since they do not allow receiving any data, which in turn reduces battery consumption.

As you can see, the advertising types are connectable or non-connectable, scannable or non-scannable, directed or undirected. The following table gives an overview of the four types of legacy advertising and their properties.

| Type             | Connectable | Scannable | Directed |
| :--------------- | :---------: | :-------: | :------: |
| ADV_IND          |      x      |     x     |          |
| ADV_DIRECT_IND   |      x      |           |    x     |
| ADV_SCAN_IND     |             |     x     |          |
| ADV_NONCONN_IND  |             |           |          |

## Bluetooth address

Every Bluetooth LE device is identified by a unique 48-bit address. Bluetooth addresses are categorized as either public or random. Random addresses are further classified as either static or private, depending on whether they change or not. And lastly, private addresses are either resolvable or non-resolvable. The image below shows how Bluetooth addresses are categorized. Note that random and private addresses are merely classification types and not actual address types.

_Image showing categorization of Bluetooth addresses._

A Bluetooth LE device uses at least one of these address types:

*   Public address
*   Random static address
*   Random private resolvable
*   Random private non-resolvable

> **Note**
> The public address assigned to a device is drawn out of the same IEEE address pool as MAC addresses (e.g. for ethernet, Wi-Fi), and therefore it is also commonly referred to as a Bluetooth MAC address.

### Public address

A public address is a fixed address that is programmed into the device at the manufacturer. It must be registered with the IEEE registration authority, and it’s globally unique to that device and cannot change during the lifetime of the device. There is a fee associated with obtaining this type of address.

### Random address

A random address is much more commonly used, as it does not require registration with the IEEE and can be manually configured by the user. This is also the default address type in the samples in the nRF Connect SDK. It is either programmed within the device or created during runtime. You can either have a static or a private address.

### Random static address

A random static address can be allocated and fixed throughout the lifetime of the device. It can be altered at bootup, but not during runtime. This is a low-cost alternative to a public address because you don’t need to register it.

As mentioned above, all Bluetooth LE devices must use either a public address or a random static address, where the latter is far more common.

### Random private address

A private address can be used when a device wishes to protect its privacy. This is an address that changes periodically and is used to hide the device’s identity and to deter device tracking.

A random private address can be resolvable or non-resolvable, and are described below.

#### Resolvable random private address

A resolvable private address is, true to its name, resolvable as intended listeners have a pre-shared key by which they can figure out the new address every time it changes. The pre-shared key is the Identity Resolving Key (IRK) and is used both to generate and to resolve the random address.

The random address is basically just used by the peer to be able to resolve the actual address of the Bluetooth LE device, which is still either the public or the random static address. The IRK allows the peer to translate the random private address into the device’s real Bluetooth LE address.

#### Non-resolvable random private address

A non-resolvable private address is not resolvable by other devices and is only intended as a way to prevent tracking. This type of address is not commonly used.

To summarize there are four different types of addresses:

*   **Public address:** Programmed into the device by the manufacturer, and is registered with the IEEE.
*   **Random static address:** Configurable at boot up and is fixed through the lifetime of the device. Does not need to be registered with the IEEE, and is a common alternative to a public address.
*   **Resolvable random private address:** (optional) An address that changes periodically, but is resolvable by means of a pre-shared key.
*   **Non-resolvable random private address:** (optional) An address that changes periodically and is not resolvable.

## Advertisement packet

Let’s examine how an advertisement packet is structured.

The BLE packet is pictured below, with the main portion going to what’s called the Protocol Data Unit (PDU). The PDU consists of either an advertising PDU (sometimes called an advertising channel PDU) or a data PDU (sometimes called a data channel PDU), depending on whether the BLE packet is used for advertisement or data transmission.

_Bluetooth LE packet structure_

As we can see in the image, the advertising PDU consists of a header and a payload.

The header part of the advertising PDU consists of:

_Advertisement PDU header_

*   **PDU Type:** Determines the advertisement type that we discussed in Advertising types, such as ADV_IND.
*   **RFU:** Reserved for future use.
*   **ChSel:** Set to 1 if LE Channel Selection Algorithm #2 is supported.
*   **TxAdd (Tx Address):** 0 or 1, depending on the transmitter address is public or random.
*   **RxAdd (Rx Address):** 0 or 1, depending on the receiver address is public or random.
*   **Length:** The length of the payload

More information about these fields can always be found in the Core Specification of Bluetooth LE on the Bluetooth SIG website.

The payload of the advertising PDU is divided into two sections, where the first 6 bytes represent the advertiser’s address (AdvA) and the rest goes to the actual advertisement data (AdvData).

_Advertisement PDU payload_

*   **AdvA:** Bluetooth address of the advertising device
*   **AdvData:** Advertisement data packet

> **Note**
> The payload structure depends on the kind of advertising. When doing directed advertisement (ADV_DIRECT_IND) some space is needed to also specify the receiver’s address. Therefore, the AdvData field is replaced by a receiver address field with a size of 6 bytes. Advertisement packets of this type (ADV_DIRECT_IND) do not include a payload.

The advertisement data section is represented as shown in the figure below.

_Advertising packet payload_

The advertisement data packet is composed of multiple structures called advertisement data structures (AD structures). Each AD structure has a length field, a field to specify the type (AD Type), and a field for the actual data itself (AD Data). Note that the most common AD type is 1 byte long.

The advertising data types are defined by the Bluetooth specification and are documented in the nRF Connect SDK here, under “EIR/AD data type definitions”.

Below are a few commonly used ones, that we will be using in following exercises.

*   **Complete local name (BT_DATA_NAME_COMPLETE):** This is simply the device name, that the human user sees when scanning for nearby devices (via a smartphone, for instance).
*   **Shortened local name (BT_DATA_NAME_SHORTENED):** A shorter version of the complete local name.
*   **Uniform Resource Identifier (BT_DATA_URI):** Used to advertise a URI like website addresses (URLs).
*   **Service UUID:** The Service Universally Unique Identifier is a number universally unique to a specific service. It can help scanners identify devices that are interesting to connect to. Different options are available here.
*   **Manufacturer Specific Data (BT_DATA_MANUFACTURER_DATA):** This is a popular type that enables companies to define their own custom advertising data, as in the case of iBeacon.
*   **Flags:** 1-bit variables that can flag a certain property or operational mode of that device.

Here is an example of an advertising data structure that is setting the flag BT_LE_AD_NO_BREDR.

_Example of an advertising data structure_

### Flags

The advertisement flags are one-bit flags encapsulated in one byte, meaning that there are up to 8 flags that can be set. We will take a look at some of the most commonly used flags:

*   **BT_LE_AD_LIMITED:** Sets LE Limited Discoverable Mode, used with connectable advertising to indicate to a central that the device is only available for a certain amount of time before the advertising times out
*   **BT_LE_AD_GENERAL:** Sets LE General Discoverable Mode, used in connectable advertising to indicate that advertising is available for a long period of time (timeout = 0).
*   **BT_LE_AD_NO_BREDR:** Indicates that classic Bluetooth (BR/EDR) is not supported

Both BT_LE_AD_LIMITED & BT_LE_AD_GENERAL are meant for a device in a peripheral role.

## Exercise 1: Setting the advertising data

In this exercise, we will cover core Bluetooth LE APIs in nRF Connect SDK. We will first learn how to enable the Bluetooth LE stack and the default configurations associated with it.

Then we will dive into how to configure our hardware to broadcast non-connectable advertising, making the device act as a beacon so that neighboring scanning devices can see the data.

### Exercise steps

**0. Prepare the project and build and flash it to your board**

0.1 Clone the GitHub repository for this course.

> Note that the repository contains the exercise code base and solutions. Make sure to select the branch that corresponds with the nRF Connect SDK version of your choosing:
>
> *   `main` (default branch): For nRF Connect SDK version v3.0.0
> *   `v2.9.0-v2.7.0`: For nRF Connect SDK versions v2.9.0 to v2.7.0
> *   `v2.6.2-v2.3.0`: For nRF Connect SDK versions v2.6.2 to v2.3.0
>
> Some of the exercises have varying exercise texts depending on which version you are using. This is reflected by tabs at the beginning of the exercise text.

Copy the link to the repository and use VS Code’s Command Palette (Go to View -> Command Palette -> type Git Clone and paste in the repository link) to clone the `https://github.com/NordicDeveloperAcademy/bt-fund` repository somewhere close to your root directory (Ex: `C:\myfw\btfund`).

Avoid storing the repo in locations with long paths, as the build system might fail on some operating systems (Windows) if the application path is too long.

0.2 In the nRF Connect extension in VS Code, select Open an existing application, and open the base code for this exercise, found in `bt-fund/l2/l2_e1`.

**1. Include the Bluetooth LE stack in your project.**

In order to include the Bluetooth LE stack in your nRF Connect SDK project, you need to enable `CONFIG_BT` in `prj.conf`. This option will already be enabled in all upcoming exercises.

```kconfig
CONFIG_BT=y
```

Enabling this symbol will apply a set of default configurations for the stack.

The highlights of the default configuration are listed below:

*   Broadcast support (`BT_BROADCASTER`) is enabled.
*   The SoftDevice Controller is used (`BT_LL_CHOICE = BT_LL_SOFTDEVICE`).
*   The TX Power is set to 0 dBm (`BT_CTLR_TX_PWR = BT_CTLR_TX_PWR_0`)

**2. Set the Bluetooth LE device name.**

The name is a C string that can theoretically be up to 248 bytes long (excluding NULL termination). In practice, it is highly recommended to keep it as short as possible, as when we include it in the advertising data, we have only 31 bytes, and these 31 bytes are shared by all advertising data. It can also be an empty string. In this exercise, we will call our device `Nordic_Beacon`.

Add the following line in `prj.conf`:

```kconfig
CONFIG_BT_DEVICE_NAME="Nordic_Beacon"
```

We will include the device name in the advertising data in a later step.

**3. Include the header files of the Bluetooth LE stack needed**

Include the following header files needed for enabling the stack, populating the advertising data, and starting advertising.

Add the following lines in `main.c`:

```c
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gap.h>
```

**4. Prepare the advertising data.**

For the advertising data, we will use both the advertising packet and the scan response packet.

4.1 Prepare the advertising packet.

4.1.1 Declare an array `ad[]` of type `struct bt_data`, which will be the advertising packet to send out.

Add the following lines in `main.c`:

```c
static const struct bt_data ad[] = {
	/* STEP 4.1.2 - Set the advertising flags */

	/* STEP 4.1.3 - Set the advertising packet data  */

};
```

4.1.2 Populate the flags using the helper macro `BT_DATA_BYTES()`.

The first thing we need to prepare in the advertising packet is the advertising flags, `BT_DATA_FLAGS`.

To help us populate these flags, we will use the helper macro `BT_DATA_BYTES()`, which has the following signature:
`BT_DATA_BYTES(type, val...)`

In this exercise, we are creating a broadcaster with non-connectable advertising. Therefore, we will only set the advertising flag `BT_LE_AD_NO_BREDR`, to indicate that classic Bluetooth (BR/EDR) is not supported.

> **Note**
> Since Nordic’s products only support Bluetooth LE, this flag should always be set to this value.

Add the following line in `main.c` (inside the `ad` array):

```c
BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_NO_BREDR),
```

4.1.3 Set the advertising packet data using the helper macro `BT_DATA()`.

There are numerous standard data types that can be included in the advertising data (either in the advertising packet or the scan response). These data types are defined in the Bluetooth Supplement to the Core Specification.

Below are a few commonly used ones, that we will be using in following exercises. The complete list of advertising data types can be found [here](https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/) (link to Bluetooth SIG GAP Assigned Numbers).

*   **Complete local name (BT_DATA_NAME_COMPLETE):** This is simply the device name. We will include the Complete Local Name in the advertising packet of this exercise.
*   **Shortened local name (BT_DATA_NAME_SHORTENED):** A shorter version of the Complete Local name.
*   **Uniform Resource Identifier (BT_DATA_URI):** You can use this type for advertising URI like website addresses (URLs). We will include the URL of Nordic Developer Academy (`https://academy.nordicsemi.com/`) in the scan response packet of this exercise.
*   **Service UUID:** Different options are available here. This is useful if you want a central to filter advertising devices based on services. We will include the UUID for the LBS and NUS services in upcoming exercises.
*   **Manufacturer Specific Data (BT_DATA_MANUFACTURER_DATA):** This is a popular type that enables companies to define their own custom advertising data, as in the case of iBeacon. We will cover using this data type in the exercise of the next lesson.

For now, we want to include the complete local name, `BT_DATA_NAME_COMPLETE`, in the advertising packet.

We will use the macro `BT_DATA()` to populate data into the advertising packet. The macro expects three parameters as shown in the signature below:
`BT_DATA(type, data, data_len)`

Add the following line in `main.c` (inside the `ad` array):

```c
BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
```

> Note: in legacy advertising we have only 31 octets available. To send more than 31 octets in advertisements, we will need to use the scan response, as we will see next.

4.2. Prepare the scan response.

In the scan response, we will include the URL for Nordic Developer Academy, for the sake of demonstration.

4.2.1 Declare the scan response packet.

Same as we did for the advertising packet, we will declare it as an array `sd[]` of type `struct bt_data`.

Add the following code in `main.c`:

```c
static const struct bt_data sd[] = {
        /* 4.2.3 Include the URL data in the scan response packet*/

};
```

4.2.2 Declare the URL data to include in the scan response packet.

We will declare the URL as an array of `static unsigned char`. In the first byte, we need to specify the URI Scheme Name String Mapping as specified in the Assigned Numbers Document from the Bluetooth SIG. The scheme is used to save data transmitted over the air. So for example, instead of transmitting advertising of 6 bytes for the “https:”, we only need to send one byte (0x17).

_Description: URI Scheme Name String Mapping defined by the Bluetooth SIG in Assigned Numbers Document helps compress common URI schemes like "https:" to a single byte._

Add the following lines in `main.c`:

```c
static unsigned char url_data[] ={0x17,'/','/','a','c','a','d','e','m','y','.',
                                 'n','o','r','d','i','c','s','e','m','i','.',
                                 'c','o','m'};
```

4.2.3 Include the URL data in the scan response packet. Add the following line inside the `sd` packet.

```c
BT_DATA(BT_DATA_URI, url_data,sizeof(url_data)),
```

**5. Enable the Bluetooth LE stack.**

The function `bt_enable()` is used to enable the Bluetooth LE stack in the application. This function must be called before any other calls that require communication with the Bluetooth LE hardware (for example, start advertising).

`bt_enable()` is blocking when passing `NULL` to it, and non-blocking if you pass a `bt_ready_cb_t` callback.

Add the following lines in `main()`:

```c
int err; // Ensure err is declared if not already

err = bt_enable(NULL);
if (err) {
	LOG_ERR("Bluetooth init failed (err %d)\n", err);
	return -1; // Or handle error appropriately
}
LOG_INF("Bluetooth initialized\n");
```

**6. Start advertising.**

Now that we have prepared the advertising data (both the advertising packet and the scan response packet), we are ready to start advertising.

Do this by calling the function, `bt_le_adv_start()`, which has the following signature:
`int bt_le_adv_start(const struct bt_le_adv_param *param, const struct bt_data *ad, size_t ad_len, const struct bt_data *sd, size_t sd_len)`

_bt_le_adv_start() function signature_

The first parameter this function expects is the advertising parameters. Here, we can either use predefined macros that cover the most common cases. Or we can declare a variable of type `struct bt_le_adv_param` and set the parameters manually.

For now, we will use one of the predefined macros. In exercise 2, we will set this parameter manually. In our case, we will be using `BT_LE_ADV_NCONN` – non-connectable advertising with a minimum advertising interval of 100 ms and a maximum advertising interval of 150 ms.

The second and third parameters are the advertising packet (created in step 4.1) and its size, while the fourth and fifth parameters are the scan response (created in step 4.2) and its size.

Add the following lines inside `main()`:

```c
err = bt_le_adv_start(BT_LE_ADV_NCONN, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
if (err) {
	LOG_ERR("Advertising failed to start (err %d)\n", err);
	return -1; // Or handle error appropriately
}
```

**7. Build and flash the application on your board.**

You should notice that LED1 (LED0 on nRF54 Series devices) on your board is blinking, indicating that your board is advertising.

**8. Open nRF Connect for Mobile on your smartphone.**

In the SCANNER tab press on the SCAN button to begin scanning.

**9. Tap on `Nordic_Beacon` to view the advertising data.**

_Mobile app view showing Nordic_Beacon details_

The first thing to notice is that there is no CONNECT button displayed. This is because we are advertising non-connectable packets (`BT_LE_ADV_NCONN`). Let’s now spend some time interpreting the data.

*   RSSI level is the received signal strength indicator on the receiver side
*   Advertising interval. Since we chose `BT_LE_ADV_NCONN`, the advertising interval is between 100-150 ms
*   Advertising flags that we set in step 4.1.2 (Bluetooth Classic BR/EDR not supported)
*   The complete local name, that we set in step 2
*   The URI data that we included in the scan response packet. Note that you can tap on the OPEN button to open the link directly in a browser.

We encourage you to try and change these parameters in the code, build and flash your board to see how easy it is to control the advertising data.

## Exercise 2

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In this exercise, we will build on top of the previous exercise to focus on advertising parameters, Manufacturer Specific Data, and updating the advertising data dynamically.

We will still broadcast non-connectable advertising in this exercise. However, as opposed to the previous exercise, we will not use a predefined macro to manage the advertising parameters and fine-control the advertising interval.

We will also learn how to dynamically change the content of advertising data. We will create custom advertising data that represents how many times Button 1 (Button 0 on nRF54 Series devices) is pressed on the board and we will include it in the advertising packet.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l2/l2_e2`.

**1. Create the variable `adv_param` of type `bt_le_adv_param`.**

This variable type can control many aspects of advertising. Let’s see how we can use it to control the advertising interval.

To create the variable, we will be using the helper macro `BT_LE_ADV_PARAM()`, which has the following signature:
`BT_LE_ADV_PARAM(options, interval_min, interval_max, peer)`

_BT_LE_ADV_PARAM() helper macro signature_

*   **Advertising options:** Specific macros to configure the advertising options. For example, choosing which channel (37, 38, 39) to advertise on.
*   **Minimum advertising interval:** (N * 0.625 milliseconds): Less than or equal to the maximum advertising interval. The allowable range for N is 32 to 16384, which translates to 20 ms to 10.24 seconds. The API has predefined values to use for advertising intervals.
*   **Maximum advertising interval:** (N * 0.625 milliseconds): Larger than or equal to the minimum advertising interval. The allowable range for N is 32 to 16384, which translates to 20 ms to 10.24 seconds. The API has predefined values to use for advertising intervals.
*   **Peer address:** Included if directed advertising is used. Otherwise, set to `NULL`.

Add the following lines in `main.c`:

```c
static const struct bt_le_adv_param *adv_param =
	BT_LE_ADV_PARAM(BT_LE_ADV_OPT_NONE, /* No options specified */
			800, /* Min Advertising Interval 500ms (800*0.625ms) */
			801, /* Max Advertising Interval 500.625ms (801*0.625ms) */
			NULL); /* Set to NULL for undirected advertising */
```

The above code will set the advertising interval to about 500 ms (500 ms/0.625 ms = 800 (N)). As we discussed before, there will be a random delay added to avoid packet collisions.

**2. Declare the Manufacturer Specific Data**

Manufacturer Specific Data is used to create and include custom data in Bluetooth LE advertising. The data to be included can be in any format suitable for your use case/application.

2.1 Declare the Company identifier (Company ID)

The first two bytes in the Manufacturer Specific Data are the company identifier as registered in Bluetooth SIG in the Assigned Numbers Document. For educational/testing purposes, we will use Nordic Semiconductor Company Identifier.

Add the following line in `main.c`:

```c
#define COMPANY_ID_CODE 0x0059
```

> **Note:** Bluetooth LE products are not allowed to broadcast a custom company ID without being a Bluetooth SIG member. When you are ready to release your product, you would have to apply for a Bluetooth SIG membership to get your own unique Company ID.

2.2 Declare the structure for your custom data

In this exercise, we will keep it simple and declare our custom data as `unsigned short` (2 bytes). The data will represent how many times Button 1 is pressed. Therefore we will create a structure `adv_mfg_data_type` that has two members. The first is, of course, the Company ID and the second is `number_press` which represents how many times button 1 is pressed on the board.

Add the following `struct` definition to `main.c`:

```c
typedef struct adv_mfg_data {
	uint16_t company_code; /* Company Identifier Code. */
	uint16_t number_press; /* Number of times Button 1 is pressed */
} adv_mfg_data_type;
```

2.3 Define and initialize a variable of type `adv_mfg_data_type` that we created in the previous step.

```c
static adv_mfg_data_type adv_mfg_data = { COMPANY_ID_CODE, 0x00 };
```

We are all set with the Manufacturer Specific Data declaration. In the next step, we will add a button press callback function that updates the `number_press` and update the advertising data through the function `bt_le_adv_update_data()`.

**3. Include the Manufacturer Specific Data in the advertising packet.**

Add the following line inside the definition of the advertising packet `ad`.

```c
BT_DATA(BT_DATA_MANUFACTURER_DATA, (unsigned char *)&adv_mfg_data, sizeof(adv_mfg_data)),
```

**4. Initialize the Buttons library and set a callback function.**

4.1 We will use the DK Buttons and LEDs library to setup an interrupt (call back function) to be called every time button 1 (button 0 on nRF54 Series devices) is pressed.

Add the `init_button()` function definition in `main.c`. (Ensure `dk_buttons.h` is included and `button_changed` is declared).

```c
#include <dk_buttons_and_leds.h> // Typically needed

// Forward declaration for button_changed if defined later
static void button_changed(uint32_t button_state, uint32_t has_changed);

static int init_button(void)
{
	int err;

	err = dk_buttons_init(button_changed);
	if (err) {
		printk("Cannot init buttons (err: %d)\n", err);
	}

	return err;
}
```

It calls the `dk_buttons_init()` function to initialize your board’s buttons and assign `button_changed()`, which will be defined in step 5, as a call back function every time a button is pressed.

4.2 Call `init_button()` in `main()`

Add the following line in `main()` (ensure `err` is declared):

```c
// int err; // if not already declared in main
err = init_button();
if (err) {
	printk("Button init failed (err %d)\n", err);
	return -1; // Or handle error
}
```

**5. Add the definition of the callback function and update the advertising data dynamically.**

We will update the advertising data dynamically from inside the `button_changed()` callback function. We will use the function `bt_le_adv_update_data()`.

`int bt_le_adv_update_data(const struct bt_data *ad, size_t ad_len, const struct bt_data *sd, size_t sd_len)`

_bt_le_adv_update_data() API Function signature_

The `bt_le_adv_update_data()` is very similar to the `bt_le_adv_start()` that we covered in the previous exercise, except it does not take Advertising Parameters options. It relies on the advertising parameters set before in `bt_le_adv_start()`.

Add the definition of the button callback function. (Ensure `USER_BUTTON` is defined, typically `DK_BTN1_MSK` or similar).

```c
// Assuming USER_BUTTON is defined, e.g., #define USER_BUTTON DK_BTN1_MSK
// Also ensure 'ad' and 'sd' are accessible (e.g. global or passed appropriately)
static void button_changed(uint32_t button_state, uint32_t has_changed)
{
	if (has_changed & button_state & USER_BUTTON) { // Ensure USER_BUTTON is correctly defined
		adv_mfg_data.number_press += 1;
		bt_le_adv_update_data(ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
	}
}
```

In the callback function, we will do the following:

*   Check which button was pressed: `if (has_changed & button_state & USER_BUTTON)`
*   Update the count of the number of presses: `adv_mfg_data.number_press += 1;`
*   Update the advertising data dynamically `bt_le_adv_update_data(ad, ARRAY_SIZE(ad),sd, ARRAY_SIZE(sd));`

**6. Build and flash the application on your board.**

You should notice that LED1 (LED0 on nRF54 Series devices) on your board is blinking now. Indicating that your board is advertising.

**7. Open nRF Connect for Mobile on your smartphone.**

> **Note**
> On the nRF54L15 DK, the board’s LEDs and Buttons are labeled with PCB labels (PCB silkscreen) that start with 0 (LED0-LED3) and (BUTTON0-BUTTON3). In previous-generation development kits, the indexing starts with 1 (LED1-LED4). So, on the nRF54L14 DK, we will be working with LED0 and BUTTON0.

In the SCANNER tab, press on the SCAN button to begin scanning.

_Mobile app scanner view_

Notice how the connection interval has changed from the previous exercise which was between 100-150 ms associated with the `BT_LE_ADV_NCONN` macro to around 500ms.

**8. Tap on `Nordic_Beacon` to view the advertising data.**

You should notice now that the Manufacturer data is included in the advertising With the company ID of Nordic Semiconductor.

**9. Tap on the Manufacturer data to change how the data is displayed and select Unsigned Int16 or Manufacturer data (Bluetooth Core 4.1).**

_Image: Data shown as Manufacturer data (Bluetooth Core 4.1)_

_Image: Changing data to Unsigned int 16_

The data will be shown as Unsigned Int 16:

_Image: The data shown as Unsigned Int 16_

**10. Press Button 1 on your board (Button 0 on nRF54 Series devices)**

You should observe that the count increments by one every time the button is pressed. You need to be in scanning mode on your phone to see the change. Press SCAN at the top right corner in nRF Connect for Mobile to see the updated data.

By default, the scanning period on nRF Connect for Mobile is set to 45 seconds. You can change the scanning period by going to Settings->Scanner->Scanning Period.

## Exercise 3

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In this exercise, we will switch gears from non-connectable advertising, which we covered in Exercises 1 and 2, to connectable advertising. Connectable advertising is used by peripherals to advertise their presence and allows centrals to establish a connection to it.

We will also include the UUID for the LBS service in the advertising data, which can be used by a central to determine whether it wants to connect based on available services. Lastly, we will learn how to manually configure the Bluetooth LE address of the peripheral. Note, the address will only appear when using Android phones, not iOS.

The LED Button Service (LBS) is a custom service created by Nordic, and will be covered in more depth in lesson 4.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l2/l2_e3`.

**1. Include support for the peripheral role from the Bluetooth LE stack.**

Add the following line in `prj.conf`:

```kconfig
CONFIG_BT_PERIPHERAL=y
```

When you enable this flag, you will get the functionalities needed for the peripheral role, including GATT and ATT. The default number for simultaneous connections `CONFIG_BT_MAX_CONN` is 1.

**2. Change the Bluetooth LE device name from `Nordic_Beacon` to `Nordic_Peripheral`.**

Add the following line in `prj.conf`:
```kconfig
CONFIG_BT_DEVICE_NAME="Nordic_Peripheral"
```

**3. Prepare the advertising data.**

3.1 Set the flags and populate the device name in the advertising packet.

As done before, we are including the device name in the packet. We are also enabling the discovery mode flag, as the device will act as a Bluetooth LE peripheral, not a beacon. We will set the discovery to `BT_LE_AD_GENERAL`.

Add the following lines inside the definition of `ad` (in `main.c`):

```c
BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
```

3.2 Populate the scan response packet with the LBS service UUID.

3.2.1 Include the header file of the UUID helper macros and definitions.

Add to `main.c`:
```c
#include <zephyr/bluetooth/uuid.h>
```

3.2.2 Include the 128-bit UUID of the LBS service in the scan response packet.

This UUID can be found here: LED Button Service (LBS) – Service UUID.
`(0x00001523, 0x1212, 0xefde, 0x1523, 0x785feabcd123)`

Add the following line inside `sd` (the scan response data array in `main.c`):

```c
BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_128_ENCODE(0x00001523, 0x1212, 0xefde, 0x1523, 0x785feabcd123)),
```

**4. Set up the random static address.**

4.1 Include the header file for managing Bluetooth LE addresses.

Add to `main.c`:
```c
#include <zephyr/bluetooth/addr.h>
```

4.2 Change the random static address.

In the past two exercises, the Bluetooth LE address generated was a Non-Resolvable Random Private Address, which is generated randomly every time on bootup. This is the default type of address set for non-connectable advertising. For connectable advertising, the default is a random static address. We will learn how to manually configure the random static address in this step and set it to the address `FF:EE:DD:CC:BB:AA`.

We will use the function `bt_id_create()` to set a new random static address. We will use the function `bt_addr_le_from_str()` to convert a string to a Bluetooth LE address. For types, it supports “random” and “public” addresses.

Add the following code snippet inside `main.c` (likely at the beginning of `main()` function, ensure `err` is declared):

```c
// int err; // if not already declared
bt_addr_le_t addr;
err = bt_addr_le_from_str("FF:EE:DD:CC:BB:AA", "random", &addr);
if (err) {
	printk("Invalid BT address (err %d)\n", err);
}

err = bt_id_create(&addr, NULL);
if (err < 0) {
	printk("Creating new ID failed (err %d)\n", err);
}
```

**5. Start to advertise connectable advertising.**

This is done by calling `bt_le_adv_start()`. To specify it is connectable advertising, we could either do it by passing `BT_LE_ADV_CONN` (instead of the `BT_LE_ADV_NCONN` macro used in exercise 1) as the first parameter. Or we can set an advertising parameter as we did in exercise 2. The advantage of creating an advertising parameter is that it gives us more control over advertising.

5.1 Create the advertising parameter for connectable advertising. Again, this is optional, you could also simply pass `BT_LE_ADV_CONN` as the first parameter to `bt_le_adv_start()`.

Define in `main.c`:
```c
static const struct bt_le_adv_param *adv_param = BT_LE_ADV_PARAM((BT_LE_ADV_OPT_CONNECTABLE|BT_LE_ADV_OPT_USE_IDENTITY), 
                800, /*Min Advertising Interval 500ms (800*0.625ms) */
                801, /*Max Advertising Interval 500.625ms (801*0.625ms)*/
                NULL); /* Set to NULL for undirected advertising*/
```

5.2 Start advertising by calling `bt_le_adv_start()` and passing the advertising parameter along with the advertising packet and scan response and their sizes.

Add in `main()`:
```c
// Ensure ad and sd are defined and accessible
err = bt_le_adv_start(adv_param, ad, ARRAY_SIZE(ad),
			      sd, ARRAY_SIZE(sd));
if (err) {
	LOG_ERR("Advertising failed to start (err %d)\n", err);
	return -1; // Or handle error
}
```

**6. Build and flash the application on your board.**

You should notice that LED1 (LED0 on nRF54 Series devices) on your board is blinking now. Indicating that your board is advertising.

**7. Open nRF Connect for Mobile on your smartphone and start scanning.**

_nRF Connect for Mobile (Android example) showing scanned device_

We should see now that the address of the device is set to `FF:EE:DD:CC:BB:AA`, and the UUID of the LBS service is now advertised. Also, we should notice the CONNECT button next to the device name, indicating that the device is advertising in connectable mode. We will cover connections in the next couple of lessons.# Connection process

In the previous lesson, we covered how the advertisement process in Bluetooth LE is a way for the peripheral to make its presence known so it can be discovered by a central, and in the end, establish a connection with it.

## Connecting

Establishing a connection requires two devices, one acting as a peripheral that is currently advertising, and one acting as a central that is currently scanning. When a central device picks up an advertisement packet from a peripheral device, it can initiate a connection. Usually, this involves scanning the contents of the advertisement packet, and then deciding whether or not to initiate a connection based on that. When the central sends a connection request, the peripheral and central have established a bi-directional connection (connection-oriented) channel.

_Figure illustrating a central initiating a connection with an advertising peripheral._

As we can see in the figure above, a peripheral that is sending out advertisements that are connectable will always have a short RX window after every advertisement, which is used to listen for incoming connection requests. We call it a connection request, but in reality, the peripheral can’t choose whether to accept or reject the connection request. It has to always accept the connection request, unless it is using an accept list filter. Later, at any point in time, it may choose to disconnect from the central if it doesn’t want to stay connected.

**More on this:**
Using an accept list filter, formerly known as whitelisting, is a way the peripheral can limit which devices are allowed to send it a connection request. This will be covered in lesson 5.

## During the connection

After the peripheral successfully receives the connection request packet, the two devices are in a connection. When a connection is entered, the devices will no longer use the advertising channels (channel 37, 38 and 39), but start using the data channels (channels 0 to 36). To reduce interference and improve throughput during a connection, Bluetooth LE uses channel hopping, meaning the channel used for data transmission is changed frequently. This way, if they are located in an environment that has a lot of noise on some channels, the messages will be retransmitted on another channel in the next connection interval. To ensure data integrity, all packets transmitted over Bluetooth LE will be retried infinitely until an acknowledgment is received or the connection is terminated.

The nature of a Bluetooth LE connection is a main factor in how the devices achieve such low power consumption. In a connection, both devices spend most of their time sleeping. To accomplish this, they agree on how often they will wake up to talk. Otherwise, they turn off the radio, set a timer and go to sleep. The time they agree on sleeping is known as the connection interval, and is set in the initial connection, while the connection event occurs every connection interval when they wake up to talk.

**Definition:**
**Connection interval:** The interval at which two devices in a connection wake up to exchange data.
**Connection event:** Occurs every connection interval, when the central sends a packet to the peripheral.

The following figure shows what a typical connection looks like. Both the central and the peripheral are waking up every connection interval for the connection events and transmitting data.

_Figure showing a typical connection with central and peripheral waking up for connection events._

The connection interval is initially set by the central in the connection request packet, but it can be changed later in the connection. The two devices can send many packets every connection interval if they need to send a lot of data, but when they stop sending data, they have to wait for the next connection event to send more data. Even if there is no useful data to send, the peers need to send empty packets to sync their clocks. If you want to send more data than there is time for in one connection interval, it will be split over several connection intervals.

## Disconnecting

When two devices are connected, they will remain connected forever if nothing happens. There are two ways that a connection can be terminated, meaning the devices disconnect:

1.  **Disconnected by application**
2.  **Disconnected by supervision timeout**

### Disconnected by application

If either of the devices want to, they can send a termination packet that will disconnect the device. This can, for example, be done because a device no longer wishes to be connected to the other device, but it will also happen if there is something wrong with the connection. E.g. if a device you are connected to is claiming to be a previously connected device, but it is not able to sign the packets with the correct encryption keys. The termination packet will contain a field called “disconnect reason” which will say something about why the devices disconnected. Such as, whether it was the user who wanted to disconnect, or if there was an issue with the stack.

### Disconnected by supervision timeout

The other reason a device may disconnect is if it stops responding to packets. There can be several reasons for this. Either the application on the connected device crashed and reset (which is not too uncommon, especially during the development phase), the connected device ran out of battery, or the connected device was taken out of radio range. The amount of time it takes before the connection times out is set by the connection supervision timeout parameter, which we will discuss in more detail in the next topic.

## Connection parameters

When a peripheral and central device enter into a connection, there is a set of connection parameters that are exchanged. Some of them have a standard start value, for backwards compatibility, while some of them are dictated by the central device, and are included in the connection request packet.

The connection interval and the connection supervision timeout were briefly discussed in the previous topic, and are set by the central in the connection request packet, in addition to the peripheral latency. Peripheral latency allows the peripheral to skip waking up for connection events if it doesn’t have data to send.

The radio mode (1M, 2M or coded PHY) is set to 1M by default for backwards compatibility, but can be changed during the connection. The data length and MTU (Maximum Transfer Unit) are also set for backwards compatibility, but we will take a look at how to change these in the exercise section of this topic.

### Connection interval

A Bluetooth LE device spends most of its time “sleeping” (hence the “Low Energy” in the name). In a connection, this is accomplished by agreeing on a connection interval saying how often the devices will communicate with each other. When they are done communicating, they will turn off the radio, set a timer and go into idle mode, and when the timer times out, they will both wake up and communicate again. The implementation of this is handled by the Bluetooth LE stack, but it is up to your application to decide how often you want the devices to communicate by setting the connection interval.

### Supervision timeout

When two devices are connected, they agree on a parameter that determines how long it should take since the last packet was successfully received until the devices consider the connection lost. This is called the supervision timeout. So if one of the devices is unexpectedly switched off, runs out of battery, or if the devices are out of radio range, then this is the amount of time it takes between successfully receiving the last packet before the connection is considered lost.

### Peripheral latency

Peripheral latency allows the peripheral to skip waking up for a certain number of connection events if it doesn’t have any data to send. Usually, the connection interval is a strict tradeoff between power consumption and low latency or delay in communication. If you want to reduce the latency, but still keep a low power consumption, you can use peripheral latency. This is particularly useful in HID (Human Interface Devices) applications, such as computer mouse and keyboard applications, which usually don’t have any data to send, but when it has data to send, we want to have very low latency. Using the peripheral latency option, we can maintain low latency but reduce power consumption by remaining idle for several connection intervals.

### PHY radio mode

Normal Bluetooth LE (1M PHY) transmits at 1Mbps. However, in Bluetooth 5.0, both high-speed (2M PHY) and long-range (Coded PHY) radio modes were introduced, (as covered in PHY: Radio modes). This gives us two more options.

First, we can increase the modulation scheme to use 2Mbps for higher transmit rates. This either means that you can transfer the data faster, and go back to sleep faster to conserve more power, or you can use that extra time to send even more data, practically doubling the throughput of a Bluetooth LE connection. This does however come with the cost of a slightly shorter range.

The other option is to use Coded PHY which results in a significant increase in range, but at the cost of lower throughput.

### Data length and MTU

The data length and MTU (Maximum Transfer Unit) are two different parameters, but they often go hand in hand.

The MTU is the number of bytes that can be sent in one GATT operation (for example, a send operation), while data length is the number of bytes that can be sent in one Bluetooth LE packet. MTU has a default value of 23 bytes, and data length has a default value of 27 bytes. When MTU is larger than data length, such as MTU being 140 bytes while data length is 27 bytes, the data will be segmented into chunks of the data length’s size. This means that, for your application, it appears like one message is being sent, but on the air, the data is actually split into smaller segments.

Ideally, you want all of your data to be sent in one packet, to reduce the time it takes to send the data, so in Bluetooth 4.2, Data Length Extension (DLE) was introduced to allow the data length to be increased from the default 27 bytes to up to 251 bytes. Packing everything together also reduces the number of bytes you need to transmit over the air, as every packet includes a 3-byte header. This saves both time and power, and in turn allows for higher throughput in your Bluetooth LE connection.

The relation between data length and MTU is not one-to-one. On air, the data length can be up to 251 bytes, while the actual payload that you can send is a maximum of 244 bytes. This is because the 251 byte Data PDU payload needs an L2CAP Header of 4 bytes, and an Attribute header of 3 bytes. This leaves you with 251 – 4 – 3 = 244 bytes that you can actually populate with payload data.

_Relation between MTU and Data Size_

Below is a figure showing what it looks like to send a message with 40 bytes before and after changing the default data length. It is clear that sending all the data in one packet leads to less radio on time.

_Left: 40-byte payload without data length extension._
_Right: 40-byte payload with data length extension._
_Source: Online Power Profiler tool_

### Updating the connection parameters

The connection interval, supervision timeout and peripheral latency are dictated by the central, but the peripheral can request changes. However, it is always the central that has the final say with these requests. So in the case where the central is your phone, it is the OS running on the phone that decides whether to accept or reject the new parameters in the connection parameter request.

As for the PHY radio mode, data length and MTU, these cannot be chosen only by the central. Since the ability to change these parameters was introduced in later releases of the Bluetooth Specification, they are always set to their default values when a connection is first established. When the connection is first established, either device can request to update these parameters with new values. The other device will then either send its supported values or state that it does not support updating one or more of those parameters.

Taking the data length as an example, this is always 27 bytes when the connection is first established. Then let’s say that the peripheral wants to update this to 200 bytes, and sends a request to do so. The central may then reply with a message saying it can do 180 bytes, and then they will agree on having the data length set to 180 bytes.

The default value for the PHY radio mode is 1M, and the default MTU is 23.

## Exercise 1: Connecting to your smartphone

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In the last lesson, we started advertising with the Nordic board and then scanned for these advertisements with a phone. You were able to connect to the board via the nRF Connect for Mobile app, but nothing more happened.

In this exercise, we will establish a connection between your Nordic board, as a peripheral, and your smartphone, as a central. Then we will set up some callback functions, to be notified when the connection parameters are changed. Then we will add a temporary service to be able to send data through the established connection.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l3/l3_e1`.

You may notice that we are using the application you ended up with in the previous exercise (lesson 2 exercise 3) as the base code for this exercise.

**1. Include the header file for handling connection events.**

Start by adding the header file needed for handling our Bluetooth Low Energy connections. Add the following close to the top of your `main.c`:

```c
#include <zephyr/bluetooth/conn.h>
```

**2. Set up callbacks to be triggered when a connection has been established or disconnected.**

2.1 Declare a connection callback structure.

Let’s declare a structure called `connection_callbacks` of type `bt_conn_cb`.

This structure is used for tracking the state of the connection. For now, we will use the members `connected` and `disconnected` to track when a new connection has been established and when a connection has been disconnected. Take a look at the API documentation for a full list of all possible events.

> **Note**
> These events are different from the connection events we discussed in the previous topic, which cannot be seen by the application. These events are called connected callback events.

We will call our callbacks `on_connected` and `on_disconnected`.

Add the following lines to `main.c` (ensure `on_connected` and `on_disconnected` are forward-declared or defined before this):

```c
// Forward declarations if defined later
void on_connected(struct bt_conn *conn, uint8_t err);
void on_disconnected(struct bt_conn *conn, uint8_t reason);

struct bt_conn_cb connection_callbacks = {
    .connected              = on_connected,
    .disconnected           = on_disconnected,
};
```

2.2 Define the callback functions `on_connected` and `on_disconnected`.

Because the callbacks are triggered from the Bluetooth libraries, it is important that they have the same function parameters as described in the documentation of the API linked above.

We will start with some simple callback functions that we can build on later. Add the following functions to your `main.c` (ensure `my_conn` is declared, typically as a global `struct bt_conn *my_conn = NULL;` and `LOG_ERR`, `LOG_INF` are available):

```c
// Global or static variable for connection handle
static struct bt_conn *my_conn = NULL;

void on_connected(struct bt_conn *conn, uint8_t err)
{
    if (err) {
        LOG_ERR("Connection error %d", err);
        return;
    }
    LOG_INF("Connected");
    my_conn = bt_conn_ref(conn);

    /* STEP 3.2  Turn the connection status LED on */
}

void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
    LOG_INF("Disconnected. Reason %d", reason);
    bt_conn_unref(my_conn);
    my_conn = NULL; // Good practice to NULL the pointer

    /* STEP 3.3  Turn the connection status LED off */
}
```

The `my_conn` parameter is just a `bt_conn` pointer that has been declared further up in the `main.c` file. We will use it to keep track of our connection in the next exercise.

2.3 Register the callback structure `connection_callbacks`.

Register the callback structure, using the function, `bt_conn_cb_register`. This needs to be called before we start advertising, to avoid a connection being established before we have registered the callback.

Add the following line in `main.c` (typically in `main()` before `bt_enable` or `bt_le_adv_start`):

```c
bt_conn_cb_register(&connection_callbacks);
```

> **Note**
> Note that in many of the Bluetooth Low Energy samples, you will not see `bt_conn_cb_register()` being used. Instead, they use the macro `BT_CONN_CB_DEFINE()`, which will both define and register these callbacks.

**3. Configure an LED to indicate the current connection status.**

3.1 Define the connection status LED

Add the following line close to the top of your `main.c` (ensure `dk_buttons_and_leds.h` or similar is included for `DK_LED2`):

```c
#include <dk_buttons_and_leds.h> // Or equivalent for your board
#define CONNECTION_STATUS_LED   DK_LED2
```

3.2 In the connected event, turn the connection status LED on.

In the callback function for the connected event, `on_connected()`, add the following line to turn the LED on (ensure `dk_set_led` is available):

```c
dk_set_led(CONNECTION_STATUS_LED, 1);
```

3.3 In the disconnected event, turn the connection status LED off.

In the callback function for the disconnected event, `on_disconnected()`, add the following line to turn the LED off:

```c
dk_set_led(CONNECTION_STATUS_LED, 0);
```

**4. Build and flash the application to your board.**

**5. Open a terminal to see the log output from the application.**

Just like we did in lesson 1, connect to the COM port of your DK in VS Code by expanding your device under Connected Devices and selecting the COM port for the device. The number for the COM port may differ on your PC.

> **Note**
> Most of the newer DKs will have more than one COM port. Try both to see which one belongs to the application core. Usually, but not always, it is the one with the smaller number.

Use the default settings 115200 8n1 rtscrs:off. Then reset the device to see the full log message.

Restart the device to see the full log output. At this point, you should be seeing the following log output:
```
*** Booting nRF Connect SDK vX.Y.Z ***
*** Using Zephyr OS vA.B.C ***
[00:00:00.004,302] <inf> Lesson3_Exercise1: Starting Lesson 3 - Exercise 1
[00:00:00.007,659] <inf> Lesson3_Exercise1: Bluetooth initialized
[00:00:00.008,605] <inf> Lesson3_Exercise1: Advertising successfully started
```

**6. Use your smartphone to scan and connect to your board.**

As we have done in previous exercises, use the nRF Connect for Mobile app the scan for devices. Connect to your device, called “Nordic_Peripheral“, by selecting Connect next to the name. This will also open a new window with a lot of tabs, but we will focus on what happens on the board for now.

Notice that the LED on your board indicates a connection, and you should also be seeing the following log output:
```
[00:00:26.831,720] <inf> Lesson3_Exercise1: Connected
```
This means that we are now in the connected state. The phone, acting as a central, picked up the advertising packets from the nRF device, which is the peripheral in this connection.

> **Important**
> If you are using iOS, you will also see the following warning lines in the log after the connected event, that can be ignored.

**7. Disconnect the device from your smartphone**

Let’s disconnect from the peripheral, by clicking the “Disconnect” button in the upper right-hand corner.

You should see the following log output:
```
[00:00:38.627,004] <inf> Lesson3_Exercise1: Disconnected. Reason 19
```
The error codes are defined in the Bluetooth specification, and can indicate why the connection was terminated.

If you open the file `hci_types.h`, you can see that 19, which is written 0x13 in hexadecimal refers to `BT_HCI_ERR_REMOTE_USER_TERM_CONN`, which means that the remote user terminated the connection. If we do the test again, but instead of disconnecting from the app, we take the phone far away from the device, we should see that the disconnect reason is 8. This is `BT_HCI_ERR_CONN_TIMEOUT`, which means that we just saw a supervision timeout occur.

At this point, we want to be able to send some data between the peripheral and the central. To do this, we need to add a service to our application. We will be adding the LED Button Service to the application.

**More on this:**
We will cover Bluetooth LE services and sending data in more detail in lesson 4. For now, it is only relevant to know that this function sends data to the connected device.

**8. Change the application to send a message whenever button 1 is pressed.**

We want to send some data whenever button 1 is pressed, and to be able to do this we need to add the LED Button Service (LBS).

8.1. Include the LBS in the application.

Start by adding this line to your `prj.conf`.
```kconfig
CONFIG_BT_LBS=y
CONFIG_BT_LBS_POLL_BUTTON=y
```
The first line will set up the service, while the other just says that it is possible to manually read the value. We will not do this directly, but we will later use an app that requires this setting to be set.

8.2 Include the LED Button Service header file near the top of your `main.c`.
```c
#include <bluetooth/services/lbs.h>
```

8.3 Add a callback to be notified when button 1 is pressed.

We want to send the button state of button 1 to the central device (your phone) whenever button 1 on the device is pressed.

Add the `button_changed()` callback in your `main.c` (ensure `USER_BUTTON` is defined, e.g., `DK_BTN1_MSK`):
```c
// Ensure USER_BUTTON is defined, e.g. #define USER_BUTTON DK_BTN1_MSK
static void button_changed(uint32_t button_state, uint32_t has_changed)
{
	int err;
	bool user_button_changed = (has_changed & USER_BUTTON) ? true : false;
	bool user_button_pressed = (button_state & USER_BUTTON) ? true : false;
	if (user_button_changed) {
		LOG_INF("Button %s", (user_button_pressed ? "pressed" : "released"));

		// Ensure my_conn is valid before sending
		if (my_conn) { 
		    err = bt_lbs_send_button_state(user_button_pressed);
		    if (err) {
			    LOG_ERR("Couldn't send notification. (err: %d)", err);
		    }
        } else {
            LOG_WRN("No connection to send button state.");
        }
	}
}
```

8.4 Complete the implementation of the `init_button()` function.

In `init_button()`, we will register the function `button_changed()` to be called when buttons on the board are pressed.
(Ensure `init_button()` is called in `main()` and `button_changed` is declared before `dk_buttons_init` or forward-declared).
```c
// Inside init_button() or ensure this is done
// static int init_button(void) { ...
    err = dk_buttons_init(button_changed);
    if (err) {
        LOG_ERR("Cannot init buttons (err: %d)", err);
    }
// ... }
```

**9. Build and flash the application to your board, and connect to it via your phone.**

When the connection is established, click the tab saying “Cli…” (or Client if your screen is large enough). This tab holds a list of all the services present on the connected device. Look for the “Nordic LED and Button Service”, and press on it to expand it.

Press on the single arrow pointing downwards to read the button characteristic once, or press the icon with multiple arrows pointing downwards to enable notifications from this characteristic.

If you try now to press button 1 on your board (Button 0 on nRF54 Series devices), you should see the Value field changing between “Button Released” and “Button Pressed”.

Remember that you need to subscribe to the notification from the peer (your smartphone or tablet) before pressing the button on the board. If a peer has not subscribed to the notification, and you press button 1, you will get the error `Lesson3_Exercise1: Couldn't send notification. err: -13` printed on the terminal. More on notifications in the next lesson.

## Exercise 2: Updating the connection parameters

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In the previous exercise, we established a connection between the Nordic board, as a peripheral, and your smartphone, as a central. We were able to send some simple data using the pre-implemented LED Button Service. Although we didn’t see it, the central already selected some connection parameters when it connected to our peripheral. In this exercise, we will look into what those parameters were, and we will also look at what we can do to change our connection parameters.

We will cover Bluetooth LE services and sending data in more detail in lesson 4. For now, it is only relevant to know that we are sending some data to a connected device.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l3/l3_e2`.

**1. Get the connection parameters for the current connection.**

1.1 Declare a structure to store the connection parameters.

In your `on_connected()` callback function, declare a structure `info` of type `bt_conn_info` to store the connection parameters. Then use the function `bt_conn_get_info()` to populate the `info` struct with the connection parameters used in the connection.
(Add this inside `on_connected()` after `my_conn = bt_conn_ref(conn);` and before turning on the LED).
```c
    struct bt_conn_info info;
	// int err; // already declared in on_connected signature
	err = bt_conn_get_info(conn, &info);
	if (err) {
		LOG_ERR("bt_conn_get_info() returned %d", err);
		// return; // Don't return here, or LED won't turn on
	}
```

1.2 Add the connection parameters to your log.

Let’s log the three main connection parameters that we talked about in Connection parameters. Note that the connection interval is represented by a unit of 1.25 ms, and the supervision timeout in units of 10 ms. So we will do some calculations to make it more readable.

Add the following lines to the end of your `on_connected()` callback in `main.c`:
```c
    if (!err) { // Only log if bt_conn_get_info was successful
        double connection_interval = info.le.interval*1.25; // in ms
        uint16_t supervision_timeout = info.le.timeout*10; // in ms
        LOG_INF("Connection parameters: interval %.2f ms, latency %d intervals, timeout %d ms", connection_interval, info.le.latency, supervision_timeout);
    }
```

> **Note**
> In order for the log to be able to process float (double) numbers, we have added the config `CONFIG_FPU=y` to the `prj.conf` file. If you used the template from GitHub, this was already added.

**2. Build and flash the sample to your board.**

Your log should look something like this:
```
*** Booting nRF Connect SDK ***
[00:00:00.251,098] <inf> Lesson3_Exercise2: Starting Lesson 3 - Exercise 2
[00:00:00.008,453] <inf> Lesson3_Exercise2: Bluetooth initialized
[00:00:00.009,490] <inf> Lesson3_Exercise2: Advertising successfully started
```

**3. Connect to the device via your smartphone**

Use nRF Connect for Mobile to locate the device, called “Nordic_Peripheral” and connect to it.

The log output will show us the connection parameters for this connection.
```
[00:00:03.989,349] <inf> Lesson3_Exercise2: Connected
[00:00:03.989,379] <inf> Lesson3_Exercise2: Connection parameters: interval 30.00 ms, latency 0 intervals, timeout 240 ms
```
Note that your connection parameters may differ from the ones shown here.

**4. Modify the callbacks to be notified when the parameters for an LE connection have been updated.**

You may have noticed that the `bt_conn_cb` structure we defined in the previous exercise, also has the member `le_param_updated`. This is used to tell our application that the connection parameters for an LE connection have been updated.

> **Note**
> There is also the event `le_param_req` callback member, which is called when the connected device requests an update to the connection parameters. You probably want to have this in your application, but we will not look into that event in this exercise.

4.1 Modify your `connection_callbacks` parameter, by adding the following line (ensure `on_le_param_updated` is declared/defined):
```c
// Forward declaration if defined later
void on_le_param_updated(struct bt_conn *conn, uint16_t interval, uint16_t latency, uint16_t timeout);

// In struct bt_conn_cb connection_callbacks = { ... };
    .le_param_updated       = on_le_param_updated,
```

4.2 Add the `on_le_param_updated()` event.

Define the callback function `on_le_param_updated()` to log the new connection parameters.

Add the following function in `main.c`:
```c
void on_le_param_updated(struct bt_conn *conn, uint16_t interval, uint16_t latency, uint16_t timeout)
{
    double connection_interval = interval*1.25;         // in ms
    uint16_t supervision_timeout = timeout*10;          // in ms
    LOG_INF("Connection parameters updated: interval %.2f ms, latency %d intervals, timeout %d ms", connection_interval, latency, supervision_timeout);
}
```

4.3 Already now, if we flash the application and connect to it, we may see that after some seconds, this callback will trigger, and you might see something like the log below. Note that this will vary depending on your smartphone.
```
[00:00:00.008,483] <inf> Lesson3_Exercise2: Bluetooth initialized
[00:00:00.009,521] <inf> Lesson3_Exercise2: Advertising successfully started
[00:00:21.988,372] <inf> Lesson3_Exercise2: Connected
[00:00:21.988,403] <inf> Lesson3_Exercise2: Connection parameters: interval 30.00 ms, latency 0 intervals, timeout 240 ms

[00:00:27.239,562] <inf> Lesson3_Exercise2: Connection parameters updated: interval 45.00 ms, latency 0 intervals, timeout 420 ms
```
So this entire time, connection parameters changes were in fact being requested by your device. This is because, even though we didn’t actively request the parameter updates when you enable the Bluetooth stack in nRF Connect SDK, default values for a lot of parameters are set, including the peripheral’s preferred connection parameters. And if these parameters don’t match the ones given by the central in the initial connection, the peripheral will automatically request changes to the connection parameters to try to get the preferred values.

Let’s take a look at what their default values are:

*   **Connection interval:**
    *   `config BT_PERIPHERAL_PREF_MIN_INT`: 24 (1.25ms units -> 30ms)
    *   `config BT_PERIPHERAL_PREF_MAX_INT`: 40 (1.25ms units -> 50ms)
*   **Peripheral latency:**
    *   `config BT_PERIPHERAL_PREF_LATENCY`: 0 (Unit is given in number of connection intervals)
*   **Supervision timeout:**
    *   `config BT_PERIPHERAL_PREF_TIMEOUT`: 42 (10ms units -> 420ms)

These are all found in `Kconfig.gatt`, in `<install_path>\zephyr\subsys\bluetooth\host`.

So we can see from the log output above that the initial connection had supervision timeout of 240 ms. Therefore, the peripheral requested a change in the parameters, and after this update, all the parameters turned out to satisfy our preferences.

**5. Change the preferred connection parameters.**

Let’s change our preferred connection parameters by adding the following lines to our `prj.conf`:
```kconfig
CONFIG_BT_PERIPHERAL_PREF_MIN_INT=800
CONFIG_BT_PERIPHERAL_PREF_MAX_INT=800
CONFIG_BT_PERIPHERAL_PREF_LATENCY=0
CONFIG_BT_PERIPHERAL_PREF_TIMEOUT=400
CONFIG_BT_GAP_AUTO_UPDATE_CONN_PARAMS=y
```
The last config, `CONFIG_BT_GAP_AUTO_UPDATE_CONN_PARAMS`, responsible for automatically sending requests for connection parameters updates, is not really needed as it is set to `y` by default. This is why we saw the update take place even though we didn’t manually request it.

You can disable this Kconfig if you do not want your application to ask for updates automatically. In that case, you can request parameter changes manually in your application by using `bt_conn_le_param_update()`.

The above parameters will set both the minimum and maximum preferred connection interval to 1 second. It will set the preferred peripheral latency to 0 connection intervals, and a preferred supervision timeout of 4 seconds.

**6. Build and flash your application, and connect to it with your smartphone.**

The log will output something like this. Note that it will take around 5 seconds after the connected event before the connection parameters are updated.
```
[00:00:00.008,453] <inf> Lesson3_Exercise2: Bluetooth initialized
[00:00:00.009,490] <inf> Lesson3_Exercise2: Advertising successfully started
[00:06:35.863,891] <inf> Lesson3_Exercise2: Connected
[00:06:35.863,922] <inf> Lesson3_Exercise2: Connection parameters: interval 30.00 ms, latency 0 intervals, timeout 240 ms
[00:06:41.113,983] <inf> Lesson3_Exercise2: Connection parameters updated: interval 1005.00 ms, latency 0 intervals, timeout 4000 ms
```
So we can see that the phone initially connected with a connection interval of 30ms and a supervision timeout of 240ms. After we requested some changes, the connection interval was changed to 1.005s and the supervision timeout to 4s. Although the 1005ms is outside of our minimum and maximum preferences, it is up to the central to decide how to reply to your request. These numbers will vary depending on the central (i.e your smartphone) in the connection, but you will most likely see 1000 ms. It is up to the phone, acting as the central, to set the connection parameters.

> **Note**
> To actually observe the connection interval, nRF Blinky is a mobile app that enables you to actually observe the changes in the connection interval when pressing the button on the device.
> Due to the graphical refresh rate of the nRF Connect for Mobile application, you won’t notice any difference in the connection interval when using this app.

We have now made the application less responsive. It may not make sense that an application that feels slower is better, and – in many cases – it isn’t. But remember that in order to decrease the latency, the devices need to communicate more often, thus using more power. This is something to consider when developing your own Bluetooth LE application, For instance, a temperature sensor does not need to update its value 10 times per second. Play around with these connection parameters to find something that suits your application.

**7. Set our preferred PHY.**

First, we need to set up a set of our preferred PHY, we will use 2M PHY.

7.1 Define the function `update_phy()` to update the connection’s PHY.

Create the following function in `main.c`:
```c
static void update_phy(struct bt_conn *conn)
{
    int err;
    const struct bt_conn_le_phy_param preferred_phy = {
        .options = BT_CONN_LE_PHY_OPT_NONE,
        .pref_rx_phy = BT_GAP_LE_PHY_2M,
        .pref_tx_phy = BT_GAP_LE_PHY_2M,
    };
    err = bt_conn_le_phy_update(conn, &preferred_phy);
    if (err) {
        LOG_ERR("bt_conn_le_phy_update() returned %d", err);
    }
}
```
What we want to do is triggering the PHY update directly from the connected callback event. We set our preferred PHY parameter saying that we prefer to use `BT_GAP_LE_PHY_2M`.

7.2 Call the function to update PHY during the connection.

Call the function `update_phy()` from the end of the `on_connected()` callback function, with the `my_conn` as the input parameter. Add the following line (after logging connection parameters and before turning on LED is fine):
```c
    if (my_conn) { // Ensure my_conn is valid
        update_phy(my_conn);
    }
```

**8. Add the callbacks to be notified when the PHY of the connection has changed.**

In theory, this should work, but we want some way to check whether the PHY actually changes. So, let’s add the `le_phy_updated` callback to the `connection_callbacks`, which will tell us if the PHY of the connection changes.

8.1 Implement the `on_le_phy_updated()` callback function. It can look something like this (ensure `on_le_phy_updated` is declared/defined):
```c
// Forward declaration if defined later
void on_le_phy_updated(struct bt_conn *conn, struct bt_conn_le_phy_info *param);

// ... definition ...
void on_le_phy_updated(struct bt_conn *conn, struct bt_conn_le_phy_info *param)
{
    // PHY Updated
    LOG_INF("PHY updated."); // Simplified initial log
    if (param->tx_phy == BT_CONN_LE_TX_POWER_PHY_1M) { // Note: These are TX_POWER enums, might need BT_GAP_LE_PHY_* for actual PHY type
        LOG_INF("New PHY: 1M");
    }
    else if (param->tx_phy == BT_CONN_LE_TX_POWER_PHY_2M) {
        LOG_INF("New PHY: 2M");
    }
    else if (param->tx_phy == BT_CONN_LE_TX_POWER_PHY_CODED_S8) {
        LOG_INF("New PHY: Long Range (Coded S8)");
    } else {
        LOG_INF("New TX PHY: %u, RX PHY: %u", param->tx_phy, param->rx_phy); // More generic log
    }
}
```
*Self-correction: The `param->tx_phy` and `param->rx_phy` in `bt_conn_le_phy_info` use values like `BT_GAP_LE_PHY_1M`, `BT_GAP_LE_PHY_2M`, `BT_GAP_LE_PHY_CODED`. The `BT_CONN_LE_TX_POWER_PHY_*` are different. Corrected example based on typical usage:*
```c
void on_le_phy_updated(struct bt_conn *conn, struct bt_conn_le_phy_info *param)
{
    LOG_INF("PHY updated.");
    LOG_INF("Selected TX PHY: %s, RX PHY: %s",
            (param->tx_phy == BT_GAP_LE_PHY_1M ? "1M" :
             param->tx_phy == BT_GAP_LE_PHY_2M ? "2M" :
             param->tx_phy == BT_GAP_LE_PHY_CODED ? "Coded" : "Unknown"),
            (param->rx_phy == BT_GAP_LE_PHY_1M ? "1M" :
             param->rx_phy == BT_GAP_LE_PHY_2M ? "2M" :
             param->rx_phy == BT_GAP_LE_PHY_CODED ? "Coded" : "Unknown"));
}
```


8.2 Enable the ability to update the PHY

The callback is ready, but we are currently not able to add it to our `connection_callbacks` struct. If you look at the declaration of `struct bt_conn_cb` in `conn.h`, you will see that this callback is only defined if `CONFIG_BT_USER_PHY_UPDATE` is defined, and by default, it is not.

Add this line to your `prj.conf`:
```kconfig
CONFIG_BT_USER_PHY_UPDATE=y
```

8.3 Add the `le_phy_updated` event to the `connection_callbacks` parameter, by adding the following line to your `connection_callbacks` structure.
```c
// In struct bt_conn_cb connection_callbacks = { ... };
    .le_phy_updated         = on_le_phy_updated,
```

**9. Build and flash the application.**

Now try connecting to your device, and see whether the PHY is updated. What does the log say? It should look something like this:
```
[00:00:00.008,422] <inf> Lesson3_Exercise2: Bluetooth initialized
[00:00:00.009,460] <inf> Lesson3_Exercise2: Advertising successfully started
[00:00:16.133,392] <inf> Lesson3_Exercise2: Connected
[00:00:16.133,422] <inf> Lesson3_Exercise2: Connection parameters: interval 30.00 ms, latency 0 intervals, timeout 240 ms
[00:00:16.224,334] <inf> Lesson3_Exercise2: PHY updated. New PHY: 2M
[00:00:21.189,422] <inf> Lesson3_Exercise2: Connection parameters updated: interval 1005.00 ms, latency 0 intervals, timeout 4000 ms
```

**More on this:**
It is not by chance that we chose 2M as the preferred PHY. Most new phones have support for 2M, while only some phones have support for Coded PHY. If you want to check whether your phone supports Coded PHY, you can replace the `BT_GAP_LE_PHY_2M` in your `preferred_phy` with `BT_GAP_LE_PHY_CODED`. In addition, you need to enable the Kconfig symbol `CONFIG_BT_CTLR_PHY_CODED`.

Lastly, we want to increase our Data Length and MTU size. Even though the LBS service which we are currently using only supports sending one byte of payload data, this is useful in many applications.

**10. Define the function `update_data_length()` to update the data length**

Add this function to your `main.c`:
```c
static void update_data_length(struct bt_conn *conn)
{
    int err;
    struct bt_conn_le_data_len_param my_data_len = {
        .tx_max_len = BT_GAP_DATA_LEN_MAX,
        .tx_max_time = BT_GAP_DATA_TIME_MAX,
    };
    // Make sure to use the passed 'conn' parameter, not global 'my_conn' if it could be different
    err = bt_conn_le_data_len_update(conn, &my_data_len);
    if (err) {
        LOG_ERR("data_len_update failed (err %d)", err);
    }
}
```
Here we are setting the number of bytes and the amount of time to the maximum. Here we are using the defined values `BT_GAP_DATA_LEN_MAX` and `BT_GAP_DATA_TIME_MAX`, which are set to 251 bytes and 17040µs, respectively. You can also set custom parameters if you like. Note that the negotiation that this triggers will result in the maximum parameter that both devices in the connection will support, so you may not get the full 251 bytes that you request. The device that supports the shortest data length will have the final say.

**11.1 Define the function `update_mtu()` to trigger the MTU negotiation**

Add the following function in `main.c` (ensure `exchange_params` and `exchange_func` are declared/defined):
```c
// Forward declaration if defined later
static void exchange_func(struct bt_conn *conn, uint8_t att_err, struct bt_gatt_exchange_params *params);
// Global or static variable
static struct bt_gatt_exchange_params exchange_params;


static void update_mtu(struct bt_conn *conn)
{
    int err;
    exchange_params.func = exchange_func;

    err = bt_gatt_exchange_mtu(conn, &exchange_params);
    if (err) {
        LOG_ERR("bt_gatt_exchange_mtu failed (err %d)", err);
    }
}
```
Similarly to how we requested the data length update, we tell our device to request an MTU update. During an MTU update negotiation, both devices will declare their supported MTU size, and the actual MTU will be set to the lower of the two, since that will be the limiting factor. You may note that this function doesn’t contain the actual MTU size. This is because this needs to be set in your `prj.conf` file, which we will set shortly.

11.2 We also need to declare the `exchange_params` parameter. This needs to be defined outside our `update_mtu()` function, so we will place it close to the top of our `main.c` (done above).

**12. Configure the application to enable data length extension**

Add the following to your `prj.conf` file:
```kconfig
# For General
CONFIG_BT_USER_DATA_LEN_UPDATE=y
CONFIG_BT_CTLR_DATA_LENGTH_MAX=251
CONFIG_BT_BUF_ACL_RX_SIZE=251 # Ensure this is >= CONFIG_BT_CTLR_DATA_LENGTH_MAX
CONFIG_BT_BUF_ACL_TX_SIZE=251 # Ensure this is >= CONFIG_BT_CTLR_DATA_LENGTH_MAX
CONFIG_BT_L2CAP_TX_MTU=247   # This is the MTU your device will request/support
```
_(Note: For nRF5340 DK, specific board files like `nrf5340dk_nrf5340_cpuapp.conf` might override `prj.conf`. Ensure these configs are in the active configuration file.)_

We are first enabling the data length extension by setting `CONFIG_BT_USER_DATA_LEN_UPDATE=y`. Then we set the actual data length by setting `CONFIG_BT_CTLR_DATA_LENGTH_MAX=251`. Then we set the size of the actual buffers that will be used, and lastly, we set the MTU size that we want to use in our application.

**13. Implement the two callback functions that will trigger when the data length is updated and when the MTU is updated.**

13.1 Let us start by adding the data length update callback.
(Ensure `on_le_data_len_updated` is declared/defined).
```c
// Forward declaration if defined later
void on_le_data_len_updated(struct bt_conn *conn, struct bt_conn_le_data_len_info *info);

// ... definition ...
void on_le_data_len_updated(struct bt_conn *conn, struct bt_conn_le_data_len_info *info)
{
    uint16_t tx_len     = info->tx_max_len;
    uint16_t tx_time    = info->tx_max_time;
    uint16_t rx_len     = info->rx_max_len;
    uint16_t rx_time    = info->rx_max_time;
    LOG_INF("Data length updated. TX: len %d bytes, time %d us. RX: len %d bytes, time %d us", tx_len, tx_time, rx_len, rx_time);
}
```

13.2 We also need to include it in our `connection_callbacks`:
```c
// In struct bt_conn_cb connection_callbacks = { ... };
    .le_data_len_updated    = on_le_data_len_updated,
```

13.3 Then we need to implement the callback that we set in the `update_mtu()` function (`exchange_func`):
```c
// Definition (declaration was done earlier)
static void exchange_func(struct bt_conn *conn, uint8_t att_err,
			  struct bt_gatt_exchange_params *params)
{
	LOG_INF("MTU exchange %s", att_err == 0 ? "successful" : "failed");
    if (!att_err) {
        // The MTU is the complete L2CAP PDU size. Payload MTU is this minus L2CAP and ATT headers.
        // bt_gatt_get_mtu(conn) returns the negotiated ATT_MTU value.
        // For notifications/indications, payload is ATT_MTU - 3 (Opcode + Handle).
        uint16_t payload_mtu = bt_gatt_get_mtu(conn) - 3;
        LOG_INF("New ATT_MTU: %d bytes, Usable payload for Notifications/Indications: %d bytes", bt_gatt_get_mtu(conn), payload_mtu);
    }
}
```

13.4 Forward the declaration of `exchange_func()`. (This was done in step 11.1)

13.5 Call the functions to update the data length and MTU size in `on_connected()`.

Make sure to call all of the parameter exchange functions that we just implemented from the `on_connected()` callback function (e.g., after `update_phy`):
```c
    // Inside on_connected(), after update_phy(my_conn);
    if (my_conn) {
        k_sleep(K_MSEC(1000));  // Delay added to avoid link layer collisions.
        update_data_length(my_conn);
        update_mtu(my_conn); // This should happen after DLE ideally, or after connection is stable
    }
```
The delay on one second is added to avoid a link layer collision. We don’t need to go into details, but it is not allowed, according to the Bluetooth Low energy specification to have two of these requests active concurrently. *(Self-correction: This refers to LL control procedures. MTU exchange is a GATT procedure, DLE is an LL procedure. They operate on different layers but staggering them is still good practice).*

**14. Build and flash the application to your device, and connect to it using your smartphone.**

Your log output should look something like this:
```
[00:00:00.008,056] <inf> Lesson3_Exercise2: Bluetooth initialized
[00:00:00.009,094] <inf> Lesson3_Exercise2: Advertising successfully started
[00:00:22.159,820] <inf> Lesson3_Exercise2: Connected
[00:00:22.159,820] <inf> Lesson3_Exercise2: Connection parameters: interval 30.00 ms, latency 0 intervals, timeout 240 ms
[00:00:22.508,392] <inf> Lesson3_Exercise2: Data length updated. TX: len 251 bytes, time 2120 us. RX: len 251 bytes, time 2120 us
[00:00:22.627,807] <inf> Lesson3_Exercise2: PHY updated. New PHY: 2M
[00:00:22.658,050] <inf> Lesson3_Exercise2: MTU exchange successful
[00:00:22.658,050] <inf> Lesson3_Exercise2: New ATT_MTU: 247 bytes, Usable payload for Notifications/Indications: 244 bytes

[00:00:27.428,161] <inf> Lesson3_Exercise2: Connection parameters updated: interval 1005.00 ms, latency 0 intervals, timeout 4000 ms
```
You should see a lot of logs from the different callbacks, stating all the different connection parameters for your connection.

**More on this:**
nRF5340 DK: Note that if you look at the solution for this exercise, you probably put all your configurations into your `prj.conf`. In the solution project, `l3/l3_e2/boards`, you will see the files `nrf5340dk_nrf5340_cpuapp.conf` and `nrf5340dk_nrf5340_cpuapp_ns.conf`. Depending on which target you are building for, either of these files will be included as the config file if you are using the nRF5340 DK. The `prj.conf` file will not be included in the build if a `<BOARD_NAME>.conf` is present in the boards folder.# GATT operations

As we’ve seen, the GATT layer defines services and characteristics, made up of attributes, that are stored in the GATT server. In this lesson we will discuss data exchange in Bluetooth LE which refers to the operations that are executed between the server and the client to learn about attributes and exchange their values in accordance with attributes permissions.

The server can either send data directly to the client or the client can poll the data from the server. But for the client to know what to request from the server, it needs to know what services and characteristics the GATT server offers. The client will therefore perform service discovery at the beginning of the connection, to learn about the services and characteristics of the server, before performing any operations to access them.

**Definition:**
**Service discovery:** The process in which a GATT client discovers the services and characteristics in an attribute table hosted by a GATT server.

## Data access

Recall that the communication here is based on a client-server architecture where the server holds the data and can either send it directly to the client or the client can poll the data from the server. Hence, GATT operations are classified into client-initiated operations and server-initiated operations.

### Client-initiated operations

Client-initiated operations are GATT operations where the client requests data from the GATT server. The client can request to either read or write to an attribute, and in the case of the latter, it can choose whether to receive an acknowledgment from the server.

We will take a closer look at these operations in exercise 1 of this lesson.

*   **Read**
    If a client wishes to read a certain value stored in an attribute on a GATT server, the client sends a read request to the server. To which the server responds by returning the attribute value.

*   **Write**
    If the client wishes to write a certain value to an attribute, it sends a write request and provides data that matches the same format of the target attribute. If the server accepts the write operation, it responds with an acknowledgement.

*   **Write without response**
    If this operation is enabled, a client can write data to an attribute without waiting for an acknowledgment from the server. This is a non-acknowledged write operation that can be used when quick data exchange is needed.

### Server-initiated operations

The other category of GATT operations are server-initiated operations, where the server sends information directly to the client, without receiving a request first. In this case, the server can either notify or indicate.

We will take a closer look at server-initiated operations in exercise 2 of this lesson.

*   **Notify**
    A Notify operation is used by the server to automatically push the value of a certain attribute to the client, without the client asking for it. This, for example, can be used to update the client about a certain sensor reading which has changed recently.
    Notifications require no acknowledgment back from the client.

*   **Indicate**
    Similar to the Notify operation, Indicate will also push the attribute value directly to the client. However, in this case, an acknowledgment from the client is required. Because of the acknowledgement requirement, you can only send one Indication per connection interval, meaning Indications are slower than notifications.

Although these operations are initiated by the server, the client is required to enable them first by subscribing to the characteristic and enabling either notifications or indications. This will be explained more in the next topic when we discuss the client characteristic configuration descriptor.

## Services and characteristics

As discussed in previous topics, the ATT layer defines attributes and how data is exposed between a client and a server. As such, one of the main functions of GATT is the hierarchal structuring of attributes stored in a GATT server into standardized entities (services and characteristics) providing seamless interoperability between different Bluetooth LE devices.

### Attributes

The ATT layer defines how data is stored and accessed in a server’s database. The data is stored in the form of data structures called Attributes. Attributes are the core data units that both the ATT and GATT layers are based on. Attributes hold user data as well as metadata describing the attribute itself, its type, security permissions, etc. Data exchange occurring between ATT servers and clients, or, GATT servers and clients, is in the form of attributes. When discussing only attributes, they are said to be stored in an ATT server. Whereas, as we will see further in this lesson, when we start classifying attributes into services and characteristics, we refer to that data structure as a GATT server.

An attribute consists of 4 blocks of data:

_An attribute structure typically contains:_
*   **Handle:** A 16-bit unique index to a specific attribute in the attribute table, assigned by the stack. An attribute is addressed via its handle. You can think of it as the row number in the attribute table, although handles are not necessarily sequential.
*   **Type (UUID):** Universally unique ID (UUID), which tells us the attribute type. For example, if this attribute declares a characteristic, this will be reflected in its Type field as it will hold a UUID used specifically to indicate declaring a characteristic.
*   **Permissions:** The security level required (encryption and/or authorization) to handle that attribute, in addition to indicating whether it’s a readable and/or writeable attribute.
*   **Value:**
    *   The actual user data (ex: sensor reading) that is stored in the attribute. This field accepts any data type. It can hold a heart rate monitor value (beats per minute), a temperature reading, or even a string.
    *   It can also hold information (metadata) about another attribute, as we will see later in this lesson.

### Universally unique ID (UUID)

A UUID is an abbreviation you will see a lot in the Bluetooth LE world. It is a unique number used to identify attributes and tells us about their significance. UUIDs have two types.

The first type is the SIG-defined 16-bit UUID. For example, the SIG-defined Heart rate service has the UUID `0x180D` and one of its enclosed characteristics, the Heart Rate Measurement characteristic, has the UUID `0x2A37`. The 16-bit UUID is energy and memory efficient, but since it only provides a relatively limited number of unique IDs, there is a need for more UUID to cover all vendors, users, and use cases.

The second type is a 128-bit UUID, sometimes referred to as a vendor-specific UUID. This is the type of UUID you need to use when you are making your own custom services and characteristics. It looks something like this: `4A98-xxxx-1CC4-E7C1-C757-F1267DD021E8` and is called the “base UUID”. The four x’s represent a field where you will insert your own 16-bit IDs for your custom services and characteristics and use them just like a predefined UUID. This way you can store the base UUID once in memory, forget about it, and work with 16-bit IDs as normal.

### Services

Let’s start by examining what constitutes a service and how attributes are hierarchically structured in a given service. As shown in the below figure, attributes are the main building blocks for services. A service definition (commonly referred to as a service) is comprised of multiple attributes arranged in a GATT-specified format which facilitates standardized data exchange between Bluetooth LE devices.

_A service is formed by attributes, including declarations for the service itself and its characteristics._

#### Service declaration attribute

Service definitions always start with a service declaration attribute. This attribute holds metadata about the service, it also indicates the beginning of a service in the sequence of services stored on a GATT server.

_A service declaration attribute structure includes:_
*   **Handle:** A unique identifier for the attribute.
*   **Type (UUID):** `0x2800` (SIG-defined UUID for primary service declaration).
*   **Permissions:** Typically "read only" and no authentication needed.
*   **Value:** The UUID of the service being declared (e.g., `0x180D` for Heart Rate Service).

The Handle is similar to a row number by which the attribute is addressed. The service declaration attribute’s Type field holds the UUID (`0x2800`) which is a unique SIG-defined UUID used only to indicate the beginning of a service.

The Permissions field here indicates “read only” and no authentication needed. This is expected in a service declaration attribute as there is no reason to have a write-permission for it, it only declares the beginning of a service.

Lastly, the Value field holds the UUID of the service being declared. For example, the Heart Rate Service is a SIG-defined service and is referred to by the UUID `0x180D` which is stored in the Value field of the Heart Rate Service-Service declaration attribute.

### Characteristics

Subsequently, a service can have zero or more characteristic definitions (commonly referred to as characteristics). A characteristic is comprised of at least two attributes and optionally more.

_Attributes forming a characteristic typically include a declaration, a value, and optional descriptors._

Similar to a service definition, a characteristic definition starts with a declaration attribute, to indicate the beginning of a characteristic in the sequence of characteristics in a service definition. This is followed by the characteristic value attribute which holds the actual user data. Optionally, a characteristic can also have one or more characteristic descriptor attributes.

*   **Characteristic declaration attribute:** Holds metadata about the Characteristic Value Attribute.
*   **Characteristic value attribute:** Holds the actual user data.
*   **Characteristic descriptor attribute (optional):** Holds more metadata about the characteristic.

#### Characteristic declaration attribute

A characteristic definition starts with a characteristic declaration attribute, to indicate the beginning of a characteristic in the sequence of characteristics in a service definition. The characteristic declaration attribute’s Type field holds the UUID (`0x2803`) used only to declare a characteristic. The declaration attribute has read-only Permissions, ensuring that clients can read the value but not write to it.

_A characteristic declaration attribute structure includes:_
*   **Handle:** A unique identifier for the attribute.
*   **Type (UUID):** `0x2803` (SIG-defined UUID for characteristic declaration).
*   **Permissions:** Typically "read only".
*   **Value:** Contains characteristic properties, value handle, and characteristic UUID.

The Value field holds important information about the characteristic being declared, specifically three separate fields:

1.  **Characteristic properties:** What kind of GATT operations are permitted on this characteristic.
2.  **Characteristic value handle:** The handle (address) of the attribute that contains the user data (value), i.e the characteristic value attribute.
3.  **Characteristic UUID:** The UUID of the characteristic being declared.

#### Characteristic value attribute

After the attribute declaring the characteristic comes the characteristic value attribute. This is where the actual user data is stored. Its Handle and Type are the ones referred to in the Characteristic Declaration Attribute Value field. Naturally, its Value field is where the actual user data is stored. The Permissions field indicates whether the client can read and/or write to this attribute.

_A characteristic value attribute structure includes:_
*   **Handle:** A unique identifier for the attribute.
*   **Type (UUID):** The UUID of the characteristic (e.g., a custom 128-bit UUID).
*   **Permissions:** Read and/or write permissions as defined.
*   **Value:** The actual user data.

#### Characteristic descriptors

The characteristic descriptor attributes are optional. They hold additional metadata about the characteristic, giving the client more information about the nature of the characteristic. There are several kinds of descriptors, but they are generally divided into two categories, GATT-defined and custom.

_A characteristic descriptor attribute structure includes:_
*   **Handle:** A unique identifier for the attribute.
*   **Type (UUID):** The UUID of the descriptor type (e.g., `0x2902` for CCCD).
*   **Permissions:** Read and/or write permissions as defined for the descriptor.
*   **Value:** Data specific to the descriptor type.

Descriptors also allow the client to set permissions for certain server-initiated GATT operations. In this course, we will focus on the GATT-defined Client Characteristic Configuration Descriptor (CCCD) as it is the most commonly used.

##### Client characteristic configuration descriptor (CCCD)

The Client characteristic configuration descriptor (CCCD) is a specific type of characteristic descriptor that is necessary when the characteristic supports server-initiated operations (i.e Notify and Indicate). This is a writable descriptor that allows the GATT client to enable and disable notifications or indications for that characteristic. The GATT client can subscribe to the characteristic that it wishes to receive updates about, by enabling either Indications or Notifications in the CCCD of that specific characteristic.

For example, in the Heart Rate Service, there is a characteristic called the Heart Rate Measurement. The GATT client (your mobile phone for instance) can use the CCCD of this characteristic to receive updates about this characteristic. So it subscribes to the Heart Rate Measurement characteristic by enabling either Indications or Notifications in the CCCD of said characteristic. This means the GATT server (most likely a heart rate sensor device) will push these measurements to your phone, without your phone having to poll for these measurements.

The CCCD attribute’s format is as pictured below. The UUID for CCCDs is `0x2902`. A CCCD must always be readable and writable. Descriptors with the Type CCCD only have 2 bits in their Value field. The first bit signals whether Notifications are enabled, and the second bit is for Indications.

_A Client Characteristic Configuration Descriptor (CCCD) attribute structure includes:_
*   **Handle:** A unique identifier for the attribute.
*   **Type (UUID):** `0x2902` (SIG-defined UUID for CCCD).
*   **Permissions:** Must be readable and writable.
*   **Value:** A 2-bit field where bit 0 enables/disables notifications, and bit 1 enables/disables indications. (e.g., `0x0001` for Notify, `0x0002` for Indicate).

We will take a closer look at how to do this in exercise 2 of this lesson.

## Attribute table

To best visualize how attributes are stored in a GATT server, let’s examine an example attribute table. An attribute table is how attributes are stored in the GATT server. The attribute table below is derived from a custom service that we will create in exercise 2 of this lesson.

**my_lbs attribute table**

| Description                                    | Handle | UUID                                         | Attribute Permissions | Attribute Value                                                                                                                                            |
| :--------------------------------------------- | :----- | :------------------------------------------- | :-------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **my_lbs Service Declaration**                 | 0x0001 | `0x2800` (Primary Service)                   | Read                  | `00001523-1212-efde-1523-785feabcd123` (UUID of my_lbs service)                                                                                             |
| Button Characteristic Declaration              | 0x0002 | `0x2803` (Characteristic)                    | Read                  | Properties: Read or Indicate <br> Handle of value: 0x0003 <br> UUID: `00001524-1212-efde-1523-785feabcd123` (Button Characteristic UUID)                  |
| Button Characteristic Value Declaration        | 0x0003 | `00001524-1212-efde-1523-785feabcd123`        | Read                  | User data: (e.g., `0x01` for pressed, `0x00` for released, image shows example `0x20002689` but text implies boolean)                                         |
| Button Descriptor Declaration (CCCD)           | 0x0004 | `0x2902` (Client Characteristic Configuration) | Read & write          | Indicate: `0x02` (Indications enabled)                                                                                                                       |
| LED Characteristic Declaration                 | 0x0005 | `0x2803` (Characteristic)                    | Read                  | Properties: Write <br> Handle of value: 0x0006 <br> UUID: `00001525-1212-efde-1523-785feabcd123` (LED Characteristic UUID)                                |
| LED Characteristic Value Declaration           | 0x0006 | `00001525-1212-efde-1523-785feabcd123`        | Write                 | User data (e.g., `0x01` for ON, `0x00` for OFF)                                                                                                            |
| MySensor Characteristic Declaration            | 0x0007 | `0x2803` (Characteristic)                    | Read                  | Properties: Notify <br> Handle of value: 0x0008 <br> UUID: `00001526-1212-efde-1523-785feabcd123` (MySensor Characteristic UUID)                        |
| MySensor Characteristic Value Declaration      | 0x0008 | `00001526-1212-efde-1523-785feabcd123`        | None (Value is Notified) | User data (e.g., sensor reading)                                                                                                                             |
| MySensor Descriptor Declaration (CCCD)         | 0x0009 | `0x2902` (Client Characteristic Configuration) | Read & write          | Notify: `0x01` (Notifications enabled)                                                                                                                       |

This attribute table depicts a custom service called “my_lbs”. The my_lbs service holds three characteristics:

1.  Button Characteristic
2.  LED Characteristic
3.  MySensor Characteristic

### Service declaration

The first line in the table declares this service with a service declaration attribute. As previously discussed, the Type field in a declaration attribute holds a unique SIG-defined value, and for service declarations, the UUID is `0x2800`. There is no reason to write to a declaration attribute, therefore its permissions are always Read-only. Lastly, the value field of the service declaration attribute holds the UUID of the service it’s declaring.
_Corresponds to Handle 0x0001 in the table above._

### Button characteristic

The Button characteristic is defined first. The Button characteristic is first declared with the Button Characteristic Declaration. The Type field of a characteristic declaration attribute is always `0x2803` to declare a characteristic and the permissions are always Read-only. The Value field holds the handle of the value attribute, properties, and the UUID of the characteristic it’s declaring.

Then comes the button characteristic value attribute which holds the actual user data, in this case, whether the button is pushed or not.

Lastly, since the button characteristic supports the Indicate operation, there is a CCCD to enable indications for the Button characteristic. The CCCD will always have the UUID `0x2902` and the permission to Read and write. In this specific table, we can see that the Indicate bit-field has been enabled. Notice that the CCCD isn’t referenced in the characteristic declaration like the value declaration is, but can be recognized by the distinct UUID.

Even though it is not referenced in the characteristic declaration, the central knows which characteristic it belongs to based on the handle, because it is listed “under” the characteristic declaration. All items under the characteristic declaration belong to that specific characteristic until there is a new characteristic declaration (UUID `0x2803`) in the list.
_Corresponds to Handles 0x0002 through 0x0004 in the table above._

### LED characteristic

After this comes the LED characteristic, which is very similar to the button characteristic. Notice that this characteristic only supports the Write operation, and therefore does not have a CCCD. It has only 2 attributes, declaration and value.
_Corresponds to Handles 0x0005 and 0x0006 in the table above._

### MySensor characteristic

Lastly, the definition of the MySensor characteristic, which only supports the Notify operation. Notice how the bitfield for the Notify operation has been enabled in the CCCD of the MySensor characteristic.
_Corresponds to Handles 0x0007 through 0x0009 in the table above._

## Exercise 1: Creating a custom service and characteristics

In this exercise, we will learn how to create our own custom service and characteristics. We will practice using the GATT API in nRF Connect SDK, which is again based on Zephyr RTOS, to create and add services and characteristics to our board’s GATT table.

For educational purposes, we will implement our own custom LED Button Service (LBS), which will be called `my_lbs` to separate it from the actual implementation of LBS in nRF Connect SDK.

LBS is a custom service created by Nordic with two characteristics that allow you to control the LEDs and monitor the state of the buttons on your Nordic board.

In this exercise, we will focus on the client-initiated GATT operations Read and Write. In the next exercise, we will add the server-initiated Notify operation.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l4/l4_e1`.

**1. Define the 128-bit UUIDs for the GATT service and its characteristics.**

Add the following lines to the file `my_lbs.h`.
```c
#define BT_UUID_LBS_VAL \
	BT_UUID_128_ENCODE(0x00001523, 0x1212, 0xefde, 0x1523, 0x785feabcd123)

/** @brief Button Characteristic UUID. */
#define BT_UUID_LBS_BUTTON_VAL \
	BT_UUID_128_ENCODE(0x00001524, 0x1212, 0xefde, 0x1523, 0x785feabcd123)

/** @brief LED Characteristic UUID. */
#define BT_UUID_LBS_LED_VAL \
	BT_UUID_128_ENCODE(0x00001525, 0x1212, 0xefde, 0x1523, 0x785feabcd123)


#define BT_UUID_LBS           BT_UUID_DECLARE_128(BT_UUID_LBS_VAL)
#define BT_UUID_LBS_BUTTON    BT_UUID_DECLARE_128(BT_UUID_LBS_BUTTON_VAL)
#define BT_UUID_LBS_LED       BT_UUID_DECLARE_128(BT_UUID_LBS_LED_VAL)
```
Notice how the base UUID used for the service is `0xXXXXXXXX, 0x1212, 0xefde, 0x1523, 0x785feabcd123` and how the first part `0xXXXXXXXX` is incremented by one for each attribute.

As we discussed earlier, the UUID is intended to represent the type of an attribute. The GATT client uses the UUID to know how to treat the value data. We will see later that nRF Connect for Mobile recognizes these UUIDs “types” and therefore presents us with a custom GUI to interact with it.

> **Note**
> Notice that in the header file `my_lbs.h`, there is a definition of the struct `my_lbs_cb` which has the two members `led_cb` and `button_cb`.
>
> The purpose of this structure is to facilitate decoupling of the code responsible for controlling the LEDs and monitoring the buttons (in our case `main.c`) from the Bluetooth LE connectivity code (`my_lbs.c`). These two members are simply function pointers to allow storing two functions in your application code to be triggered anytime the button characteristic is read, or the LED characteristic is written and provide/update the data needed. The function `my_lbs_init()` does the actual assigning of these pointers from `main.c` to `my_lbs.c`.

**2. Create and add the service to the Bluetooth LE stack.**

Now we will statically add the service to the attributes table of our board (the GATT server) using the `BT_GATT_SERVICE_DEFINE()` macros to statically create and add a service.

Add the following code in `my_lbs.c`:
```c
BT_GATT_SERVICE_DEFINE(my_lbs_svc,
    BT_GATT_PRIMARY_SERVICE(BT_UUID_LBS),
    /* STEP 3 - Create and add the Button characteristic */

    /* STEP 4 - Create and add the LED characteristic. */
);
```
The above code creates and adds an empty primary service to the attribute table and assigns it the UUID defined in `BT_UUID_LBS`.

**3. Create and add the custom Button characteristic.**

We will use the `BT_GATT_CHARACTERISTIC()` macro to statically create and add characteristics inside the service.
The `BT_GATT_CHARACTERISTIC()` API takes the following parameters:
1.  Characteristic UUID (`_uuid`)
2.  Characteristic Properties (`_props`)
3.  Attribute Permissions (`_perm`)
4.  Read callback function (`_read`)
5.  Write callback function (`_write`)
6.  User data pointer (`_user_data`)

The first parameter to add is the UUID of the characteristic, `BT_UUID_LBS_BUTTON`, defined in step 1. Then the second and third parameters are the attribute properties and attribute permissions for the characteristic. We are only adding the Read operation for now, so we will set them to `BT_GATT_CHRC_READ` and `BT_GATT_PERM_READ` respectively.

The fourth parameter is the read callback. This is a callback function that is triggered whenever someone tries to read the Button characteristic. We will call this `read_button` and define it in a later step.

The fifth parameter will be set to `NULL` as we are not supporting the Write operation on the Button characteristic.

Lastly, we will pass the user data `button_state`, which is a boolean (`0x01`, `0x00`) representing the button state (Button pressed or Button released). Note that the user data is optional, but we will use it in our LBS implementation.

Add the following code inside the service definition:
```c
    BT_GATT_CHARACTERISTIC(BT_UUID_LBS_BUTTON,
                           BT_GATT_CHRC_READ,
                           BT_GATT_PERM_READ, read_button, NULL,
                           &button_state),
```

**4. Create and add the custom LED characteristic.**

This step is similar to step 3. The first parameter to add is the UUID of the characteristic, `BT_UUID_LBS_LED`. The second and third parameters are the attribute properties and attribute permission, in the case of the LED characteristic, we want to support the Write operation, so we will pass `BT_GATT_CHRC_WRITE` and `BT_GATT_PERM_WRITE` respectively.

In this case, the fourth parameter is set to `NULL`, as the LED characteristic will not support the Read operation.

The write callback function, which is triggered whenever someone tries to write to the LED characteristic, is set to `write_led` and will be defined in step 6. No user data is set in the LED characteristic since we will get this value from the GATT client (the central device).

Add the following code inside the service definition:
```c
    BT_GATT_CHARACTERISTIC(BT_UUID_LBS_LED,
                           BT_GATT_CHRC_WRITE,
                           BT_GATT_PERM_WRITE,
                           NULL, write_led, NULL),
```

**5. Implement the read callback function `read_button()` of the Button characteristic.**

The read callback function is triggered when a request to read the Button characteristic is received. The read callback function must have the `bt_gatt_attr_read_func_t` function signature:
`ssize_t (*bt_gatt_attr_read_func_t)(struct bt_conn *conn, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset)`

We want the read callback function to call the registered application callback function to read the current value of the button (pressed or released), then call the function `bt_gatt_attr_read()` to send the value to the GATT client (the central device).

The `bt_gatt_attr_read()` takes the following parameters: `conn`, `attr`, `buf`, `buf_len`, `offset`, `value`, `value_len`.

For the `conn`, `attr`, `buf`, `buf_len`, and `offset`, we will simply forward the values passed to us from the stack. While for `value` and `value_len` we will rely on the application callback function to update it.

Add the following code in `my_lbs.c`:
```c
static ssize_t read_button(struct bt_conn *conn,
                          const struct bt_gatt_attr *attr,
                          void *buf,
                          uint16_t len,
                          uint16_t offset)
{
	//get a pointer to button_state which is passed in the BT_GATT_CHARACTERISTIC() and stored in attr->user_data
	const char *value = attr->user_data;

	LOG_DBG("Attribute read, handle: %u, conn: %p", attr->handle,
		(void *)conn);

	if (lbs_cb.button_cb) {
		// Call the application callback function to update the get the current value of the button
		button_state = lbs_cb.button_cb(); // Assuming button_state is a global/static bool
		return bt_gatt_attr_read(conn, attr, buf, len, offset, &button_state, // Pass address of button_state
					 sizeof(button_state)); // Use sizeof(button_state)
	}

	return 0;
}
```

**6. Implement the write callback function `write_led()` of the LED characteristic.**

The write callback function is triggered when a request to write to the LED characteristic is received. The write callback function must have the `bt_gatt_attr_write_func_t` function signature:
`ssize_t (*bt_gatt_attr_write_func_t)(struct bt_conn *conn, const struct bt_gatt_attr *attr, const void *buf, uint16_t len, uint16_t offset, uint8_t flags)`

We want the write callback function to read the value received from the central device, stored in `buf`, and then call the registered application callback function to update the state of the LED.

Add the following code in `my_lbs.c`:
```c
static ssize_t write_led(struct bt_conn *conn,
                         const struct bt_gatt_attr *attr,
                         const void *buf,
                         uint16_t len, uint16_t offset, uint8_t flags)
{
	LOG_DBG("Attribute write, handle: %u, conn: %p", attr->handle,
		(void *)conn);

	if (len != 1U) {
		LOG_DBG("Write led: Incorrect data length");
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
	}

	if (offset != 0) {
		LOG_DBG("Write led: Incorrect data offset");
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}

	if (lbs_cb.led_cb) {
		//Read the received value
		uint8_t val = *((uint8_t *)buf);

		if (val == 0x00 || val == 0x01) {
			//Call the application callback function to update the LED state
			lbs_cb.led_cb(val ? true : false);
		} else {
			LOG_DBG("Write led: Incorrect value");
			return BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED);
		}
	}

	return len;
}
```

**7. Include the header file of the customer service `my_lbs.h`**

Now that we are done defining our custom LBS service, we can add it to the main application code.
Add the following line in `main.c`:
```c
#include "my_lbs.h"
```

**8. Controlling the LED.**

8.1 Specify controlling LED3 on the board.
Add the following line in `main.c`:
```c
#define USER_LED                DK_LED3
```

8.2 Define the application callback function for controlling the LED.
We will simply rely on the Buttons and LED library and call `dk_set_led()` to set the state of the LED. This function will be called by the write callback function of the LED characteristic, `write_led()`, and it will pass either `True` or `False`.
Add the following code in `main.c`:
```c
static void app_led_cb(bool led_state)
{
	dk_set_led(USER_LED, led_state);
}
```

**9. Monitoring the button.**

9.1 Specify monitoring Button 1 on the board.
Add the following line in `main.c`:
```c
#define USER_BUTTON             DK_BTN1_MSK
```

9.2 Define the application callback function for reading the state of the button.
This function will simply return the global variable `app_button_state` to the caller (the read callback function of the Button characteristic). Since `app_button_state` is updated in the `button_changed()` function already defined in `main.c` that is called whenever a button is pressed, this variable will represent the state of the button.
Add the following lines in `main.c`:
```c
// Ensure app_button_state is declared, e.g., static bool app_button_state = false;
static bool app_button_cb(void)
{
	return app_button_state;
}
```

**10. Declare a variable `app_callbacks` of type `my_lbs_cb`**

Declare the variable of type `my_lbs_cb` and initiate its members to the application callback functions `app_led_cb` and `app_button_cb`.
Add the following code in `main.c`:
```c
static struct my_lbs_cb app_callbacks = {
	.led_cb    = app_led_cb,
	.button_cb = app_button_cb,
};
```

**11. Pass the application callback functions stored in `app_callbacks` to our custom LBS service.**

This is done by passing `app_callbacks` to `my_lbs_init()`, a function already defined in `my_lbs.c` to register application callbacks for both the LED and the Button characteristics.
Add the following code in `main.c` (ensure `err` is declared):
```c
// int err; // if not already declared in main()
err = my_lbs_init(&app_callbacks);
if (err) {
	printk("Failed to init LBS (err:%d)\n", err);
	return -1; // or handle error appropriately
}
```

**12. Build and flash the application on your board.**

LED1 (LED0 on the nRF54L15 DK) on your board should be blinking, indicating that your board is advertising.
> **Note**
> On the nRF54L15 DK, the board’s LEDs and Buttons are labeled with PCB labels (PCB silkscreen) that start with 0 (LED0-LED3) and (BUTTON0-BUTTON3). In previous-generation development kits, the indexing starts with 1 (LED1-LED4).

**13. Connect to your board using your smartphone.**

Open nRF Connect for Mobile on your smartphone, and connect to your device named “MY_LBS1“, in the Scanner tab.
_Description: nRF Connect for Mobile screenshot showing the "Nordic LED Button Service" with "Button" (Read) and "LED" (Write) characteristics._

Here we can see our LBS service, and nRF Connect for Mobile recognizes the UUID for the service and its characteristics and labels the service as “Nordic LED Button Service” and its characteristics as “Button” and “LED”. Also, notice that the Button characteristic currently supports only the GATT read operation, while the LED characteristic supports the GATT write operation.

**14. Control the LED**

In nRF Connect for Mobile, press on the arrow next to the LED characteristic to write to it.
_Description: nRF Connect for Mobile screenshot highlighting the write arrow for the LED characteristic._

A pop-up window will appear, allowing you to either turn on or turn off the LED on the board.
_Description: nRF Connect for Mobile pop-up for writing to LED characteristic, with ON/OFF options._

Select ON and then SEND to turn LED3 on. Then select the arrow again, and select OFF to turn off LED3 (LED2 on nRF54L15 DK).

**15. Read the button status.**

Press and hold button 1 (button 0 on the nRF54L15 DK) on your board while simultaneously pressing the arrow next to the button characteristic to read it. You should see that the value is now updated to the Button pressed.

In the next exercise, we will add the Notify operation to the Button characteristic so the button status will be updated without the need for us to manually poll read.
> **Note**
> Although the values sent are simply `0x00` and `0x01`, nRF Connect for Mobile presents these values as Button released and Button pressed for better visualization since it recognizes the UUID for the Button characteristic.

## Exercise 2: Adding notification and indication support

In this exercise, we will add support for the GATT operations Notify and Indicate. Recall that these operations are server-initiated, but the GATT client must subscribe to the desired data to receive the messages.

The exercise is divided into two parts.

First, we will add support for the Indicate operation to the Button characteristic and then subscribe to the Button characteristic from nRF Connect for Mobile to be notified whenever the button is pushed.

In the second part, we will add another custom characteristic to our service that will only support notifications. We will call this characteristic MYSENSOR, and use it to periodically send simulated sensor data to your phone. This is a very relevant use-case, for example, if your board has a sensor that collects some data that you want to periodically transmit to a central device.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l4/l4_e2`.

**1. Modify the Button characteristic declaration to support indication.**

Modify the declaration of the Button characteristic to pass the `BT_GATT_CHRC_INDICATE` attribute property, as well as the read property. Notice how we use the bitwise or operator `|` to support both read and indication.
Change the following code in `my_lbs.c`:
```c
    BT_GATT_CHARACTERISTIC(BT_UUID_LBS_BUTTON,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_INDICATE,
                           BT_GATT_PERM_READ, read_button, NULL,
                           &button_state),
```

**2. Create and add the Client Characteristic Configuration Descriptor.**

Since we are now using indication, we need to have a Client Characteristic Configuration Descriptor to enable devices acting as GATT clients (for example, nRF Connect for Mobile) to subscribe to this characteristic.

We will use the macro `BT_GATT_CCC()` to create and add the Client Characteristic Configuration Descriptor. Its signature is `BT_GATT_CCC(cfg_changed, perm)`.
The first parameter is the configuration change callback function that we will call `mylbsbc_ccc_cfg_changed` and implement in the next step, and the second parameter is the access permission for the descriptor which we will grant both read and write permissions.

Add the following code (right below the Button Characteristic definition in `my_lbs.c`):
```c
    BT_GATT_CCC(mylbsbc_ccc_cfg_changed,
                BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
```
This code is added right below the Buttons Characteristic definition. The location of where to place this definition is important, as discussed in the Attribute table topic.

**3. Implement the configuration change callback function.**

This function is called when a GATT client enables or disables indication. The callback function must have the signature as shown in the code below.
We want this callback function to update the boolean `indicate_enabled` to true if the client (your phone) enables indications or false if the client disables indications.
Add the following code in `my_lbs.c` (ensure `indicate_enabled` is declared, e.g., `static bool indicate_enabled = false;`):
```c
static void mylbsbc_ccc_cfg_changed(const struct bt_gatt_attr *attr,
                                  uint16_t value)
{
	indicate_enabled = (value == BT_GATT_CCC_INDICATE);
}
```

**4. Define an indication parameter**

In order to use the Indicate operation, we need to define a variable of type `struct bt_gatt_indicate_params` to hold the variable that you want to send out and the characteristic that you want to associate the indication with.
Add the following line in `my_lbs.c`:
```c
static struct bt_gatt_indicate_params ind_params;
```
We will populate the fields of this struct variable in the next step.

**5. Define the function to send indications.**

This is the function that your application code can call to send data to subscribed clients whenever it needs to.
In this function, we will use the GATT API function `bt_gatt_indicate()` to do the work of sending indications.
The `bt_gatt_indicate()` function takes a connection pointer (`conn`, `NULL` for all subscribed) and a pointer to `bt_gatt_indicate_params`.

Before calling `bt_gatt_indicate()`, we need to check if indication is enabled (`indicate_enabled` is true or false). If `indicate_enabled` is false, we will simply return and not send indications.

5.1 Add the following function definition in `my_lbs.c`:
```c
// Ensure button_state is accessible if this function needs it directly,
// or it's passed as a parameter.
// Assuming indicate_cb is defined:
// static void indicate_cb(struct bt_conn *conn, struct bt_gatt_indicate_params *params, uint8_t err) { /* Log indication status */ }

int my_lbs_send_button_state_indicate(bool current_button_state) // Changed to accept current state
{
	if (!indicate_enabled) {
		return -EACCES;
	}

	/* STEP 5.2 - Populate the indication */
    // Placeholder for next step's code
    return 0; // Placeholder
}
```

5.2 If indications are enabled, populate `ind_params`.
The structure `ind_params` is of type `bt_gatt_indicate_params` which has several members, some of which are mandatory to fill and some that are optional.
The first two members are `uuid` (optional, can be `NULL` if `attr` is provided) and `attr` (pointer to the characteristic value attribute).
_Description: The `bt_gatt_indicate_params` struct has members like `uuid`, `attr`, `func`, `destroy`, `data`, `len`._

We need to provide either the UUID or a pointer to the attribute of the characteristic that we want to have Indicate support. In this case, we will be using the latter.
Remember as we discussed before, that a characteristic will have at least two attributes, the characteristic declaration attribute and the characteristic value attribute. So we need to provide a pointer to either the Button characteristic declaration or the Button characteristic value.

_Description: An example attribute table for "My LBS" service is shown, with indices for attributes: `my_lbs_svc.attrs[0]`, `my_lbs_svc.attrs[1]` (Button Characteristic Declaration), `my_lbs_svc.attrs[2]` (Button Characteristic Value)._
> **Note**
> To see your own attributes table, you need to watch the variables `my_lbs_svc.attrs[i]` for every attribute in the table while debugging the application.
> In the Watch window in the Debug panel, select the plus icon to Add Expression and type in the fields you want to watch, `my_lbs_svc`, `my_lbs_svc.attrs[0]`, `my_lbs_svc.attrs[1]`, etc…

So we can pass either the Button characteristic declaration in index 1 (`&my_lbs_svc.attrs[1]`) or the Button characteristic value in index 2 (`&my_lbs_svc.attrs[2]`). We should pass the characteristic *value* attribute.

The optional member `func` allows you to register a function when the remote device acknowledges an indication. We will set it to `indicate_cb` which prints it to the debug log.
The optional member `destroy` allows you to register a function when indication ends, which we will set to `NULL`.
For the last two parameters, the Indicate Value data and its length, we need to specify the data we want to send out and its size. Here, we will simply pass the `button_state` and its size.

Add the following lines to the function definition (inside the `if (indicate_enabled)` block):
```c
    // This state needs to be the *actual current* button state.
    // It's better to update a global/static button_state and use that,
    // or pass the current state to this function.
    // For this example, assuming 'current_button_state' is the up-to-date value.
    // static bool global_button_state; // if used globally
    // global_button_state = current_button_state;

	ind_params.attr = &my_lbs_svc.attrs[2]; // Index of Button Characteristic Value
	ind_params.func = indicate_cb;         // Make sure indicate_cb is defined
	ind_params.destroy = NULL;
	ind_params.data = &current_button_state; // Use the passed current state
	ind_params.len = sizeof(current_button_state);
	return bt_gatt_indicate(NULL, &ind_params); // NULL for conn sends to all subscribed & connected
```

**6. Send indication on a button press.**

Now we want the GATT server to send the indication upon a button press. We will trigger indication in the `button_changed()` function so that every time button 1 is pressed, we will send its status as indication.
Add the following line in `main.c` inside `button_changed()` (ensure `user_button_state` reflects the current state):
```c
    // Inside button_changed() in main.c, after determining user_button_state
    // bool user_button_state = (button_state & USER_BUTTON) ? true : false;
    my_lbs_send_button_state_indicate(user_button_state);
```
Note that we are still supporting the Read operation that we did in the previous exercise, so the Button characteristic now supports both read and indication.

**7. Build and flash the application on your board.**

LED1 on your board should be blinking, indicating that your board is advertising.

**8. Connect to your board using your smartphone.**

Open nRF Connect for Mobile on your smartphone, and connect to your device, now named “MY_LBS2“, in the Scanner tab.
Notice how the Button characteristic now includes support for the GATT indicate operation. Also, notice the symbol consisting of two arrows. This allows your smartphone, acting as a GATT client, to subscribe to Button characteristic indication.
_Description: nRF Connect for Mobile screenshot showing "MY_LBS2" with the Button characteristic now showing indicate capability (double arrows icon)._

**9. Subscribe to the Button characteristic indication.**

Press on the two arrows symbol to subscribe to the Button characteristic indication.

**10. Press Button 1 on your board, and notice how indication is sent by the board as soon as the button is pressed or released.**

With this, we have covered how to create a custom Bluetooth LE service from scratch. It’s worth noting that the nRF Connect SDK comes with the LBS service, among many others (from nRF Connect SDK and Zephyr RTOS ) that you can use out-of-the-box, and you don’t have to implement it from scratch as we did in this exercise and the past exercise. We only did this for learning purposes.

You can easily use the built-in LBS service in nRF Connect SDK by enabling the Kconfig symbol `CONFIG_BT_LBS` in `prj.conf` and registering your application callback functions to read the button status and update the LEDs.

---
In this part of the exercise, we will add another custom characteristic that supports only notifications. We will call this characteristic MYSENSOR, and use it to periodically stream data over Bluetooth LE.

**11. Add the UUID for the MYSENSOR characteristic**

11.1 Assign a UUID to the new characteristic. We will use the base UUID for the LBS service `0x00001526, 0x1212, 0xefde, 0x1523, 0x785feabcd123` where the first portion is simply incremented from the last characteristic.
> **Note**
> You can also generate your own UUID using this website or by using Python or similar scripting languages.

Add the following code in `my_lbs.h`:
```c
/** @brief MySensor Characteristic UUID. */ // Corrected comment
#define BT_UUID_LBS_MYSENSOR_VAL \
	BT_UUID_128_ENCODE(0x00001526, 0x1212, 0xefde, 0x1523, 0x785feabcd123)
```

11.2 Convert the array to a generic UUID by using the macro `BT_UUID_DECLARE_128()`.
Add the following line in `my_lbs.h`:
```c
#define BT_UUID_LBS_MYSENSOR       BT_UUID_DECLARE_128(BT_UUID_LBS_MYSENSOR_VAL)
```

**12. Create and add the MYSENSOR characteristic and its Client Characteristic Configuration Descriptor.**

We are only supporting the GATT Notify operation.
Add the following code in `my_lbs.c` in the service declaration (after the LED characteristic or Button characteristic with its CCCD).
```c
    BT_GATT_CHARACTERISTIC(BT_UUID_LBS_MYSENSOR,
                           BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_NONE, NULL, NULL, // Read/Write perms are NONE for notify-only value
                           NULL), // No user_data pointer needed if value is sent dynamically

    BT_GATT_CCC(mylbsbc_ccc_mysensor_cfg_changed,
                BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
```

**13. Define the configuration change callback function to detect enabling/disabling notifications for the MYSENSOR characteristic.**

In this function, we will update the boolean `notify_mysensor_enabled` to true if the client (the remote device) enables notification or false if the client disables notification on the MYSENSOR characteristic.
Add the following code in `my_lbs.c` (ensure `notify_mysensor_enabled` is declared, e.g., `static bool notify_mysensor_enabled = false;`):
```c
static void mylbsbc_ccc_mysensor_cfg_changed(const struct bt_gatt_attr *attr,
                                          uint16_t value)
{
	notify_mysensor_enabled = (value == BT_GATT_CCC_NOTIFY);
}
```

**14. Define the function `my_lbs_send_sensor_notify()` to send notifications for the MYSENSOR characteristic.**

This is the function that your application code can call to send data to subscribed clients whenever it needs to.
In this function, we will use the GATT API function `bt_gatt_notify()` to do the work of sending notifications.
The `bt_gatt_notify()` function takes `conn` (or `NULL`), `attr` (pointer to characteristic value attribute), `data`, and `len`.

As we discussed earlier, we need to provide a pointer to either the MYSENSOR characteristic declaration or the MYSENSOR characteristic value. For `bt_gatt_notify`, we point to the characteristic *value* attribute. From the table image, if MYSENSOR characteristic declaration is at index `N`, its value is at `N+1`. Let's assume MYSENSOR characteristic declaration is at `attrs[6]`, then its value is at `attrs[7]`.

And we need to specify the data we want to send out and its size. This time we are sending 4 bytes (or 32 bits, the size of the `uint32_t` type) to represent the sensor reading. You can send any data type of your preference over Bluetooth LE.

Before calling `bt_gatt_notify()`, we need to check if notification is enabled on the MYSENSOR characteristics, meaning a client has subscribed to it. This is done by simply checking the value of the boolean variable `notify_mysensor_enabled`. If it is not enabled, we will return and do nothing.
Add the following code in `my_lbs.c`:
```c
int my_lbs_send_sensor_notify(uint32_t sensor_value)
{
	if (!notify_mysensor_enabled) {
		return -EACCES;
	}
    // Assuming MYSENSOR characteristic value attribute is at index 7
    // (Service Decl[0], Btn Decl[1], Btn Val[2], Btn CCCD[3], LED Decl[4], LED Val[5], MySensor Decl[6], MySensor Val[7], MySensor CCCD[8])
    // The value attribute for MYSENSOR would be my_lbs_svc.attrs[7] based on the table structure provided.
	return bt_gatt_notify(NULL, &my_lbs_svc.attrs[7], 
			              &sensor_value,
			              sizeof(sensor_value));
}
```

**15. Define the data you want to stream over Bluetooth LE**

We will declare a `uint32_t` (4 bytes) to hold the simulated sensor readings and assign it an initial value of 100.
Add the following line in `main.c`:
```c
static uint32_t app_sensor_value = 100;
```

**16. Define a function `simulate_data()` to simulate the data.**

Just for the sake of demonstration and to visually see the change of data on the remote device, we will include a function that increments the `app_sensor_value` sent over Bluetooth LE by 1 each time. `app_sensor_value` will start from 100 and get incremented by one on every notification push; it will roll back to 100 once the value reaches 200.
In a real application, we would normally call a sensor API to get actual data.
Add the following code to `main.c`:
```c
static void simulate_data(void)
{
	app_sensor_value++;
	if (app_sensor_value == 200) {
		app_sensor_value = 100;
	}
}
```

**17. Define the interval at which you want to send data at (streaming interval).**

We will set this to 500 ms. Typically, you must set this value to meet your application’s needs.
Add the following code in `main.c`:
```c
#define NOTIFY_INTERVAL         500
```

**18. Create a thread to periodically send data**

The nRF Connect SDK, which is based on Zephyr RTOS, has many options to schedule tasks periodically. One option is to create a separate thread, as covered in the nRF Connect SDK Fundamentals course – Lesson 7.
We will create a thread dedicated to sending notifications periodically.

18.1 Define the thread function
In this function, we will call `simulate_data()` to increment the simulated data sensor by one, send it to the remote device as Bluetooth LE notification, and sleep for `NOTIFY_INTERVAL`.
Add the following code in `main.c`:
```c
void send_data_thread(void)
{
	while(1){
		/* Simulate data */
		simulate_data();
		/* Send notification, the function sends notifications only if a client is subscribed */
		my_lbs_send_sensor_notify(app_sensor_value);

		k_sleep(K_MSEC(NOTIFY_INTERVAL));
	}
}
```

18.2. Define and initialize the thread to periodically send the data.
Add the following line in `main.c` (ensure `STACKSIZE` and `PRIORITY` are defined, e.g., `#define STACKSIZE 1024`, `#define PRIORITY 7`):
```c
K_THREAD_DEFINE(send_data_thread_id, STACKSIZE, send_data_thread, NULL, NULL,
                NULL, PRIORITY, 0, 0);
```

**19. Build and flash the application on your board, and connect to it using your smartphone.**

**20. Subscribe to the MYSENSOR characteristic**

The MYSENSOR characteristic is shown as Unknown Characteristic as the nRF Connect for Mobile has no registered name for the new UUID chosen for the MYSENSOR characteristic.
> **Note**
> (In Android) You can add a name to it in nRF Connect for Mobile by pressing the MYSENSOR characteristic and clicking on the pen symbol at the top to assign it a name.

Subscribe to the characteristic and notice how data is received periodically from your board approximately twice a second (NOTIFY_INTERVAL was set to 500ms).

## Exercise 3: Sending data between a UART and a Bluetooth LE connection

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

This exercise will focus on Nordic UART Service (NUS). NUS is quite a popular and versatile custom GATT service. The service emulates a serial port over Bluetooth LE, which allows you to send any sort of data back and forth between a UART connection (or a virtual serial port emulated over USB) and a Bluetooth LE connection.

_Diagram illustrating NUS: UART (PC) <-> Board (NUS Peripheral) <-> Bluetooth LE (Central/Phone)_

The service has two characteristics:
*   **RX Characteristic (Write, Write w/o response):** For sending data *to* the board
*   **TX Characteristic (Notify):** For receiving data *from* the board

When a Bluetooth LE connection is established between a peripheral and a central, NUS forwards any data received on the RX pin of the UART0 peripheral to the Bluetooth LE central as notifications through the TX Characteristic. Any data sent from the Bluetooth LE central through the RX Characteristic is sent out of the UART0 peripheral’s TX pin.

Remember that on Nordic DKs, the UART0 peripheral is typically gated through the SEGGER debugger/programmer chip (aka: interface MCU) to a USB CDC virtual serial port that you can connect directly to your PC.
> **Note**
> The code provided in this exercise uses NUS to forward/receive data to/from the UART0 peripheral. You could easily modify the exercise to use NUS with UART1 or other peripherals.

In this exercise, we will learn how to use NUS to exchange data over Bluetooth LE between your PC and your smartphone or tablet running nRF Connect for Mobile.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l4/l4_e3`.

**1. Include NUS in your application.**

Add the following line to your `prj.conf` file:
```kconfig
CONFIG_BT_NUS=y
```
Enabling this Kconfig will make the build system include the `nus.c` and the `nus.h` files. Since `nus.c` already includes the static service declaration and its characteristics, including the source files will by itself add NUS to the attribute table of your application.

In the application code (`main.c`), we will mainly need to do the following tasks:
*   Initialize the UART peripheral.
*   Define and register an application callback function to forward the data received from a Bluetooth LE connection to UART.
*   Call a function to send data received from UART to a Bluetooth LE connection.

We will first spend some time examining the NUS service implementation.

**2. Examine the NUS service declaration**

This is declared in `nus.c`, (found in `<install_path>\nrf\subsys\bluetooth\services\nus.c`). We will not modify the source files of the NUS service.
The declaration statically creates and adds the service with the UUID `BT_UUID_NUS_SERVICE` (defined in `nus.h`). and its two characteristics, the RX Characteristic and TX Characteristic.

_The NUS service declaration includes a primary service, an RX characteristic (for writing data to the device), and a TX characteristic (for notifying data from the device)._

Notice the presence of the conditional compilation flag `CONFIG_BT_NUS_AUTHEN`. If enabled, it will do the following to the static configurations of the characteristics of the NUS service:
*   Change the characteristic access permission of the TX Characteristic from `BT_GATT_PERM_READ` to `BT_GATT_PERM_READ_AUTHEN` (requires authentication & encryption).
*   Change the characteristic access permission of the Client Characteristic Configuration Descriptor of the TX Characteristic from `BT_GATT_PERM_READ | BT_GATT_PERM_WRITE` to `BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_WRITE_AUTHEN` (requires authentication & encryption).
*   Change the characteristic access permission of the RX Characteristic from `BT_GATT_PERM_READ | BT_GATT_PERM_WRITE` to `BT_GATT_PERM_READ_AUTHEN | BT_GATT_PERM_WRITE_AUTHEN` (requires authentication & encryption).

Authenticated connections and encryption will be the focus of the next lesson; therefore, we will disable the `CONFIG_BT_NUS_AUTHEN` flag in this lesson.
Also, notice that for the write callback of the RX Characteristic, we are registering the function `on_receive()`. This function is called every time the Bluetooth central device writes data to the RX Characteristic. We will dissect it in the next step.

**3. Examine the write callback function of the RX Characteristic**

Let’s examine the write callback function of the RX Characteristic `on_receive()` in `nus.c`. The function calls the application callback function and passes it three parameters. The connection handle (in case multiconnection is used), the data received over Bluetooth LE, and its size.
_The `on_receive` function in `nus.c` essentially acts as a bridge, calling a user-registered callback (`cb->received`) with the connection, data, and length when data is written to the NUS RX characteristic._

**4. Examine the `bt_nus_init()` which is also defined in `nus.c`**

This function and the structure `bt_nus_cb` (defined in `nus.h`) have a similar intent to the `my_lbs_init()` we saw in Exercise 1. The purpose of `bt_nus_init()` and the `bt_nus_cb` struct is to facilitate decoupling of the code responsible for actually reading/writing to the UART peripheral (application code, i.e `main.c`) from the Bluetooth LE connectivity code (`nus.c`). Code decoupling adds a bit of complexity, but it does make the code way easier to maintain and scale.
_The `bt_nus_init` function takes a pointer to a `bt_nus_cb` struct, which contains function pointers for application-defined callbacks related to NUS operations._

Later, we will call this function in `main.c` and pass it a pointer to our application callback functions. Notice that the `bt_nus_init()` function can register three application callback functions:
*   **Data received callback (Mandatory).** The data has been received as a write request on the RX Characteristic, so the application callback function must do the action needed to forward the data to the UART peripheral.
*   **Data sent callback (Optional).** This function pointer can allow you to register an application callback function to be triggered when data has been sent as a notification to the TX Characteristic. We will not use it in this exercise.
*   **Send state callback (Optional).** This function pointer can allow you to register an application callback function to be triggered when a remote Bluetooth LE device subscribes or unsubscribes to the TX Characteristic notifications. We will not use it in this exercise.

**5. Examine the function responsible for sending notifications**

The last function we will examine in `nus.c`, is the function responsible for sending notifications over a Bluetooth LE connection `bt_nus_send()`. We will call `bt_nus_send()` from the application code (`main.c`) to forward the data received from the UART to a remote device over a Bluetooth LE connection.
Unlike in LBS, where we supported a single Bluetooth LE connection, NUS can support simultaneous connections. Therefore, the implementation of sending notifications is slightly different.
We will check the connection parameter `conn` (of type `struct bt_conn`) if it equals `NULL`, we will send notifications to all connected devices. On the other hand, if a specific connection is passed to the `bt_nus_send()` function, we will manually check if notification is enabled by the client on that connection and then send notification to that particular client.
_The `bt_nus_send` function handles sending data via NUS TX characteristic notifications. If `conn` is `NULL`, it iterates through all connections; otherwise, it sends to the specified connection, checking subscription status._

With this, we have a good understanding of the implementation of Nordic UART Service. In the next steps, we will cover how to use it in an application code.

**6. Declare two FIFO data structures**

Declare two FIFOs data structures and the FIFO data item to hold the following:
*   The data received from the UART peripheral, and we want to send over a Bluetooth LE connection (`fifo_uart_rx_data`).
*   The data was received from a Bluetooth LE connection, and we want to send over UART (`fifo_uart_tx_data`).

6.1 Declare the FIFOs
Add the following code in `main.c`:
```c
static K_FIFO_DEFINE(fifo_uart_tx_data);
static K_FIFO_DEFINE(fifo_uart_rx_data);
```

6.2 Declare the struct of the data item of the FIFOs
Add the following code in `main.c` (ensure `UART_BUF_SIZE` is defined, e.g., from `CONFIG_BT_NUS_UART_BUFFER_SIZE` or a local define):
```c
// Assuming UART_BUF_SIZE is defined, e.g., #define UART_BUF_SIZE CONFIG_BT_NUS_UART_BUFFER_SIZE
struct uart_data_t {
	void *fifo_reserved; // Must be first element
	uint8_t data[UART_BUF_SIZE];
	uint16_t len;
};
```
Notice that the 1st word is reserved for use by FIFO as required by the FIFO implementation. The second member of the structure, which will hold the actual data, is an array of bytes of size `CONFIG_BT_NUS_UART_BUFFER_SIZE`. It is user configurable. The default size is 40 bytes.

**7. Initialize the UART peripheral**

Setting up the UART peripheral driver, using its asynchronous API, and assigning an application callback function is covered thoroughly in the nRF Connect SDK Fundamentals course – Lesson 5. Feel free to revisit the Lesson in the nRF Connect SDK Fundamentals course to refresh the information if needed.
Add the call to `uart_init()` in `main()` as shown below (ensure `uart_init()` is defined and `err`, `error()` are available):
```c
// int err; // if not already declared in main()
// void error(void) { /* Handle error, e.g., loop forever */ }
err = uart_init();
if (err) {
	error();
}
```

**8. Forward the data received from a Bluetooth LE connection to the UART peripheral.**

8.1 Create a variable of type `bt_nus_cb` and initialize it.
This variable will hold the application callback functions for the NUS service.
Add the following code in `main.c` (ensure `bt_receive_cb` is declared/defined):
```c
// Forward declaration or definition of bt_receive_cb
// static void bt_receive_cb(struct bt_conn *conn, const uint8_t *const data, uint16_t len);
static struct bt_nus_cb nus_cb = {
	.received = bt_receive_cb,
};
```
We will set the data received callback to `bt_receive_cb`, which is covered in a following step.

8.2 Pass your application callback functions stored in `nus_cb` to the NUS service by calling `bt_nus_init()`
Add the following code in `main()`:
```c
// int err; // if not already declared
err = bt_nus_init(&nus_cb);
if (err) {
	LOG_ERR("Failed to initialize UART service (err: %d)", err);
	return 0; // or handle error appropriately
}
```

8.3 The `bt_receive_cb()` function will be called by NUS when data has been received as a write request on the RX Characteristic. The data received from a Bluetooth LE connection will be available through the pointer `data` with the length `len`. We will call the UART peripheral function `uart_tx` to forward the data received over Bluetooth LE to the UART peripheral.
Add the following code inside `bt_receive_cb()` function (this part implies `bt_receive_cb` allocates `tx` and puts it in a FIFO if `uart_tx` fails immediately, which is a common pattern for handling backpressure):
```c
// Inside bt_receive_cb(struct bt_conn *conn, const uint8_t *const data, uint16_t len)
// This example assumes 'tx' is a struct uart_data_t * allocated and populated with 'data' and 'len'.
// A more direct approach might be:
// err = uart_tx(uart_dev, data, len, SYS_FOREVER_MS);
// if (err) { /* handle error, maybe put into a TX FIFO for later retry */ }

// The provided snippet implies a FIFO is used if immediate tx fails:
// struct uart_data_t *tx = k_malloc(sizeof(*tx) + len); /* Simplified allocation example */
// if (tx) {
//    memcpy(tx->data, data, len);
//    tx->len = len;
//    err = uart_tx(uart, tx->data, tx->len, SYS_FOREVER_MS); // uart is the device struct pointer
//    if (err) {
//        k_fifo_put(&fifo_uart_tx_data, tx);
//    } else {
//        k_free(tx);
//    }
// }
// The original text is:
// err = uart_tx(uart, tx->data, tx->len, SYS_FOREVER_MS);
// if (err) {
//     k_fifo_put(&fifo_uart_tx_data, tx);
// }
// This assumes 'tx' is already a `struct uart_data_t *` properly populated.
// Let's assume `tx` is correctly prepared before this snippet.
		err = uart_tx(uart, tx->data, tx->len, SYS_FOREVER_MS); // `uart` should be your UART device instance
		if (err) {
			k_fifo_put(&fifo_uart_tx_data, tx);
		}
```
In case there is an ongoing transfer already or an error, we will put the data in the `fifo_uart_tx_data` and try to send it again inside the `uart_cb` UART callback.

**9. Receiving data from the UART peripheral and sending it to a Bluetooth LE connection.**

9.1 Push the data received from the UART peripheral into the `fifo_uart_rx_data` FIFO.
On the `UART_RX_BUF_RELEASED` event in the `uart_cb` callback function of the UART peripheral, we will put the data received from UART into the FIFO by calling `k_fifo_put()`. The `UART_RX_BUF_RELEASED` event is triggered when the buffer is no longer used by UART driver.
Add the following line inside the UART callback function in the `UART_RX_BUF_RELEASED` event:
```c
// case UART_RX_BUF_RELEASED:
//    struct uart_data_t *buf = CONTAINER_OF(evt->data.rx_buf.buf, struct uart_data_t, data);
//    // This assumes `buf` is correctly retrieved. The original text just shows:
    k_fifo_put(&fifo_uart_rx_data, buf); // `buf` should be `struct uart_data_t *`
```

9.2 Create a dedicated thread for sending the data over Bluetooth LE.
We will create a thread and associate it with the function `ble_write_thread()` which we will develop in the next step. The thread is assigned the stack `STACKSIZE` (1024 by default), and the priority `PRIORITY` (7 by default).
Add the following line of code in `main.c`:
```c
// Ensure STACKSIZE and PRIORITY are defined.
// Forward declare ble_write_thread if defined later.
K_THREAD_DEFINE(ble_write_thread_id, STACKSIZE, ble_write_thread, NULL, NULL,
                NULL, PRIORITY, 0, 0);
```

9.3 Define the thread function
```c
// Ensure ble_init_ok semaphore is defined and initialized.
// k_sem ble_init_ok;
// k_sem_init(&ble_init_ok, 0, 1); /* In main before starting BLE */
// k_sem_give(&ble_init_ok);      /* After bt_enable completes */

void ble_write_thread(void)
{
	/* Don't go any further until BLE is initialized */
	k_sem_take(&ble_init_ok, K_FOREVER);
	struct uart_data_t nus_data = { // Temporary buffer to accumulate data for sending
		.len = 0,
	};

	for (;;) {
		/* Wait indefinitely for data to be sent over bluetooth */
		struct uart_data_t *buf = k_fifo_get(&fifo_uart_rx_data,
						     K_FOREVER);

		// This logic attempts to send data in chunks up to nus_data.data size
		// or until a newline/carriage return is found.
		int plen = MIN(sizeof(nus_data.data) - nus_data.len, buf->len);
		int loc = 0;

		while (plen > 0) {
			memcpy(&nus_data.data[nus_data.len], &buf->data[loc], plen);
			nus_data.len += plen;
			loc += plen;

			if (nus_data.len >= sizeof(nus_data.data) ||
			   (nus_data.data[nus_data.len - 1] == '\n') ||
			   (nus_data.data[nus_data.len - 1] == '\r')) {
				if (bt_nus_send(NULL, nus_data.data, nus_data.len)) {
					LOG_WRN("Failed to send data over BLE connection");
				}
				nus_data.len = 0; // Reset buffer
			}
			// Prepare for next chunk from the same buf if any left
			plen = MIN(sizeof(nus_data.data) - nus_data.len, buf->len - loc);
		}
		k_free(buf); // Assuming buf was allocated with k_malloc for the FIFO
	}
}
```
In this thread, we have an infinite loop where we call `k_fifo_get()` to get the data from the FIFO. We will send the data to connected Bluetooth LE device(s) as notification by calling the NUS function `bt_nus_send()`.
Notice that we passed `K_FOREVER` as the second parameter for `k_fifo_get()`. This means the thread will be scheduled out if there is no data in the FIFO. Once the UART peripheral callback function `uart_cb` puts data in the FIFO, the thread will be scheduled back for execution.
Also, notice that the thread will only start after the Bluetooth LE stack has been initialized through the use of the semaphore: `k_sem_take(&ble_init_ok, K_FOREVER)`.

**10. (Only for nRF54L15 DK) Set ZMS as the storage backend.**
Add to `prj.conf`:
```kconfig
CONFIG_ZMS=y
```

**10. Build and flash the application on your board.** *(Renumbered due to DK specific step)*

You should notice that LED1 on your board is blinking now, indicating that your board is advertising.

### Testing

**11. Open a terminal to view the log output from the application**

Just like we have done in previous exercises, connect to the COM port of your DK in VS Code by expanding your device under Connected Devices and selecting the COM port for the device. Note on some development kits; there might be more than one COM port. Use the one that you see the `Starting Nordic UART service example` log on.
Your log should look like below:
```
*** Booting nRF Connect SDK ***
Starting Nordic UART service example
```
If you don’t see that log on the terminal, since it only prints on bootup once, you can press the reset button on the board to see it.

**12. Connect to your device via your smartphone.**

Open nRF Connect for Mobile on your smartphone. In the Scanner tab, locate the device, now named “Nordic_UART_Service” and connect to it, as done in the previous exercises.

**13. Send data from your phone to the board.**

In nRF Connect for Mobile, press on the arrow next to the RX Characteristic. You will be prompted with a small window.
Type a message in the Write value box, select the type of operation: Request (write with response) or Command (write with no response), and press SEND.
_Description: nRF Connect for Mobile screenshot showing the dialog to write a value to the NUS RX characteristic._

The message will be forwarded to the UART peripheral and should appear in your PC's terminal connected to the DK:
```
*** Booting nRF Connect SDK ***
Starting Nordic UART service example
Hello from phone!
```

**14. Send data from your PC to your phone through the board.**

14.1 In nRF Connect for mobile, subscribe to the TX Characteristic by pressing on the icon next to the TX Characteristic (usually three downward arrows).

14.2 In your PC's terminal application (e.g., VS Code terminal connected to the DK's COM port), type a message to send to the remote device (for example `Hello from PC!`) and hit enter (to send an end-of-line and carriage return).
> **Important**
> Please note that the data you type will not be visible in the terminal since most terminals are in char mode by default (local echo might be off). Once you hit enter on your keyboard, you will be able to see the data on the Smartphone/Tablet side using nRF Connect for Mobile.

The message will be forwarded from the UART peripheral through the Bluetooth LE connection to the central device running nRF Connect for Mobile and show up there.
_Description: nRF Connect for Mobile screenshot showing "Hello from PC!" received on the NUS TX characteristic._

> **Note**
> The default Maximum Transmission Unit (MTU) set in the nRF Connect SDK Bluetooth stack is 23 bytes. It means you can’t send more data than can fit in the ATT MTU in one notification push. If you want to send more data in a single go, you need to increase this value; longer ATT payloads can be achieved, increasing the ATT throughput. This was covered in Lesson 3 – Exercise 2. Also, more details are available [here](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/zephyr/connectivity/bluetooth/bluetooth-mtu-update.html) (or similar official documentation link).# Pairing process

The most common practice of protecting wireless communication is to encrypt the connection, which converts the data being sent into a form that can only be read by those with the permission to do so.

To encrypt the link, both peers need to have the same keys. The process of generating, distributing, and authenticating these keys for encryption is referred to as the pairing process.

The pairing process requires the devices to repeat the process every time they want to encrypt the link again. In addition to “pairing”, the term “bonding” is used when the peers store the encryption key so they can re-encrypt the link in future connections with the same peer. During bonding, they can also exchange and store identity keys so they can recognize each other for future connections through the random resolvable private address.

**Definition:**
**Pairing:** The process of generating, distributing, and authenticating keys for encryption purposes.
**Bonding:** The process of pairing followed by distribution of keys used to encrypt the link in future reconnections.

Bluetooth LE defines 3 phases in the encryption process.

_Diagram showing the three phases of pairing: Phase 1 (Pairing Feature Exchange), Phase 2 (Authentication and Key Generation), Phase 3 (Transport Specific Key Distribution)._

## Phase 1: Initiate pairing

To initiate the pairing and, in some cases, the bonding process, the central needs to send a Pairing Request and the peripheral responds with a Pairing Response. In this phase, the two devices exchange their pairing features, that will be used to determine what pairing method they will use in phase 2 and what keys are distributed in phase 3.

Most importantly, the peers exchange their I/O (input/output) capabilities, selected from one of the following:

*   **DisplayOnly:** The peer only has a display
*   **DisplayYesNo:** The peer has a display and the option to select “yes” or “no”
*   **KeyboardOnly:** The peer has keyboard only
*   **NoInputNoOutput:** The peer has no input and no output capabilities
*   **KeyboardDisplay:** The peer has keyboard and display capabilities

In addition, they exchange what security features they support, whether or not bonding is requested, and more.

> **Note**
> Only the central can send a Pairing Request. The peripheral, however, can send a Security Request which can trigger a Pairing Request from the central, but it’s not a common practice.

## Phase 2: Perform pairing

In phase 2, the keys used to encrypt the connection are generated. The pairing method used here depends on the information exchanged in phase 1.

In LE Legacy pairing, the peers exchange a Temporary Key (TK) used to generate a Short Term Key (STK) that is then used to encrypt the link. However, since the STK can easily be cracked, Bluetooth v4.2 introduced something called Bluetooth LE Secure Connections. In LE Secure Connections, the devices generate and exchange a more secure type of key, and use it to generate a single Long Term Key (LTK) used to encrypt the connection. See Legacy pairing vs LE Secure Connections later in this lesson for more information on the difference between these two security methods.

Legacy pairing defines three different methods to exchange the TK, called pairing methods. LE Secure Connections supports these three pairing methods but also a fourth (numeric comparison) that is not supported in Legacy pairing. The security of the pairing process depends on which pairing method is used in this phase.

### Pairing methods

*   **Just Works:** Both peers generate the STK based on information exchanged in plain text, and the user is just asked to accept the connection. This method is unauthenticated.
*   **Passkey Entry:** 6-digit number is displayed on one device, and needs to be typed in on the other device. The I/O capabilities of the devices determine which one displays the number and which one inputs it.
*   **Out of Band (OOB):** The encryption keys are exchanged by some other means than Bluetooth LE, for example by using NFC.
*   **Numeric Comparison (LE Secure Connections only):** Both devices display a 6-digit number and the user selects “yes” or “no” to confirm the display.

Which pairing method to use is decided based on the OOB flag, the Man-In-The-Middle (MITM) flag, and the I/O capabilities of the peers, exchanged during phase 1.

The OOB and MITM flags first determine whether to use the OOB pairing method directly or determine the pairing method based on the I/O capabilities.

_Diagram illustrating how OOB and MITM flags on Initiator and Responder determine the pairing method selection process (e.g., Use OOB, Check MITM, Use I/O capabilities, Just Works)._

**Rules for using OOB and MITM flags (based on the provided image):**

| Responder OOB | Responder MITM | Initiator OOB | Initiator MITM | Resulting Action                               |
| :------------ | :------------- | :------------ | :------------- | :--------------------------------------------- |
| Set           | *Any*          | Set           | *Any*          | Use OOB                                        |
| Set           | *Any*          | Not Set       | *Any*          | Use OOB (LE Secure Connections)                |
| Not Set       | *Any*          | Set           | *Any*          | Use OOB (LE Secure Connections)                |
| Not Set       | Set            | Not Set       | Set            | Check MITM (then likely Use I/O capabilities)  |
| Not Set       | Set            | Not Set       | Not Set        | Check MITM (then likely Use I/O capabilities)  |
| Not Set       | Not Set        | Not Set       | Set            | Check MITM (then likely Use I/O capabilities)  |
| Not Set       | Not Set        | Not Set       | Not Set        | Just Works (if no I/O capabilities lead to other methods) / Use I/O capabilities |

Notice that in LE Secure Connections, only one of the peers needs to have the OOB flag set, for this pairing method to be used.

Depending on the OOB and MITM flags, the I/O capabilities of the peers might be used to determine the pairing method. In this case, the following table is used.

_Diagram showing a table that maps Initiator I/O capabilities (Display only, Display Yes No, Keyboard, No Input No Output, Keyboard Display) against Responder I/O capabilities to determine the pairing method (Just Works, Passkey Entry, Numeric Comparison)._

**Mapping of I/O capabilities to key generation method (based on the provided image):**

| Initiator I/O     | Responder I/O     | Pairing Method                                     |
| :---------------- | :---------------- | :------------------------------------------------- |
| Display only      | Display only      | Just Works                                         |
| Display only      | Display Yes No    | Just Works                                         |
| Display only      | Keyboard          | Passkey Entry                                      |
| Display only      | No Input No Output| Just Works                                         |
| Display only      | Keyboard Display  | Passkey Entry                                      |
| Display Yes No    | Display only      | Just Works                                         |
| Display Yes No    | Display Yes No    | Just Works / Numeric Comparison (LE Secure Conn.)    |
| Display Yes No    | Keyboard          | Passkey Entry                                      |
| Display Yes No    | No Input No Output| Just Works                                         |
| Display Yes No    | Keyboard Display  | Passkey Entry / Numeric Comparison (LE Secure Conn.) |
| Keyboard          | Display only      | Passkey Entry                                      |
| Keyboard          | Display Yes No    | Passkey Entry                                      |
| Keyboard          | Keyboard          | Passkey Entry                                      |
| Keyboard          | No Input No Output| Just Works                                         |
| Keyboard          | Keyboard Display  | Passkey Entry                                      |
| No Input No Output| Display only      | Just Works                                         |
| No Input No Output| Display Yes No    | Just Works                                         |
| No Input No Output| Keyboard          | Just Works                                         |
| No Input No Output| No Input No Output| Just Works                                         |
| No Input No Output| Keyboard Display  | Just Works                                         |
| Keyboard Display  | Display only      | Passkey Entry                                      |
| Keyboard Display  | Display Yes No    | Passkey Entry / Numeric Comparison (LE Secure Conn.) |
| Keyboard Display  | Keyboard          | Passkey Entry                                      |
| Keyboard Display  | No Input No Output| Just Works                                         |
| Keyboard Display  | Keyboard Display  | Passkey Entry / Numeric Comparison (LE Secure Conn.) |

The key generated at this phase will be used to encrypt the link after phase 2. If you are only doing pairing, not bonding, then only these 2 phases will be performed and the peers will skip phase 3.

## Phase 3: Key distribution

In this phase, the Long Term Key (LTK) is used to distribute the rest of the keys. In legacy pairing, the LTK is also generated in this phase (in LE Secure Connections, the LTK is generated in phase 2). Other keys are also generated and exchanged in this phase, to identify the peers the next time they re-connect and to be able to re-encrypt the link using the same LTK.

## Legacy pairing vs LE Secure Connections

### Legacy pairing

Prior to Bluetooth v4.2, legacy pairing was the only method of pairing available in Bluetooth LE. It is quite simple and exposes a risk because the Short Term Key (STK) used to encrypt the link can easily be cracked.

When using Just Works in Legacy pairing, the TK is set to 0, which offers no protection in terms of eavesdropping or Man-In-The-Middle (MITM). An attacker can easily brute force the STK and eavesdrop the connection, and there is also no way of verifying the devices.

Using Passkey entry is a bit better, as the TK is now a 6-digit number that is passed between the devices by the user. For example, one of the devices displays the number on its screen, and the user inputs this number on the other devices using a keyboard. Unfortunately, an attacker can easily sniff the values being exchanged, and it is then very easy to figure out the STK and decrypt the connection. Even if it isn’t able to determine the TK directly, the key can easily be cracked by trying all the 999999 combinations.

In Out of Band pairing, the TK is exchanged by some other means than Bluetooth LE, for example, by using NFC. This method supports using a TK as big as 128 bits, which increases the security of the connection. The security of the OOB channel used during the exchange also determines the protection of the Bluetooth LE connection. If the OOB channel is protected from eavesdropping and MITM attacks, so is the Bluetooth LE link.

Legacy pairing is not recommended by the Bluetooth SIG, but if you must use it, use OOB pairing. Out of Band authentication is the sole method that can be considered secure when pairing with legacy pairing.

### LE Secure Connections

For this reason, LE Secure Connections was introduced in Bluetooth v4.2. Instead of using a TK and STK, LE Secure Connections uses Elliptic-Curve Diffie-Hellman (ECDH) cryptography to generate a public-private key pair. The devices exchange their public keys. They will use one of the four pairing methods (Just Works, Passkey entry, OOB or Numeric Comparison) to verify the authenticity of the peer device and generate the LTK based on the Diffie-Hellman key and authentication data.

Although Just Works is more secure when using LE Secure Connections. it still does not offer authentication and is therefore not recommended as a pairing method. The Passkey entry pairing method now uses the passkey, along with the ECDH public key and a 128-bit arbitrary number to authenticate the connection. This means it is much more secure than described in legacy pairing. Using OOB pairing is still a recommended option, as it provides protections as long as the OOB channel is secure, just like in legacy pairing.

Additionally, a new pairing method called Numeric Comparison was introduced with this feature. Although it follows the same procedure as the Just Works pairing method, it adds another step at the end to protect against MITM attacks by having the user perform a manual check based on values displayed on both peers.

The only data exchanged between the peers is the public keys. The use of the ECDH public key cryptography makes it extremely difficult to crack the LTK, and is a significant improvement compared to legacy pairing.

> **Note**
> Even though LE Secure Connections is supported by most devices, there are still some Bluetooth LE products that only support Legacy pairing. Therefore, it is a good idea to enable support for Legacy pairing in addition to LE Secure Connections to achieve better interoperability in your application.

## Security modes

### Security concerns

There isn’t a simple answer to the question “How secure is Bluetooth LE?” It depends heavily on how the pairing process is executed and what I/O capabilities the peer devices have.

There are 3 common types of attacks that Bluetooth LE security must cope with:

1.  **Identity tracking**
2.  **Passive eavesdropping (sniffing)**
3.  **Active eavesdropping (Man-in-the-middle, or MITM)**

Identity tracking exploits the Bluetooth address to track a device. Protecting against such attacks requires privacy protection. This can be done by using a resolvable private address that changes randomly, where only the bonded/trusted devices can resolve the private address. The IRK (Identity resolving key) is used to generate and resolve the private address.

Passive eavesdropping allows an attacker to listen to data being transmitted between devices. This can be protected against by encrypting the communication between the peers. The challenge here is how the peer devices generate and/or exchange the keys to encrypt the connection securely. This was the main drawback that made Bluetooth LE legacy pairing vulnerable, and created the need for LE Secure Connections.

In an active eavesdropping (or man-in-the-middle) attack the attacker impersonates two legitimate devices to fool them into connecting to it. To prevent against this, we need to be sure that the device we are communicating with is in fact the device we want to talk to and not an unauthenticated device.

### Security levels

Bluetooth LE defines 4 security levels in security mode 1:

*   **Level 1:** No security (open text, meaning no authentication and no encryption)
*   **Level 2:** Encryption with unauthenticated pairing
*   **Level 3:** Authenticated pairing with encryption
*   **Level 4:** Authenticated LE Secure Connections pairing with encryption

Each connection starts at security level 1, and then upgraded to a higher security level depending on which pairing method is used.

Using Just Works, either with Legacy Pairing or LE Secure Connections, will bring the connection to security level 2. This method does not protect against MITM attacks, since the link is just encrypted, and not authenticated. To protect against MITM, the connection needs to be at security level 3 or higher. This can be achieved by using either Passkey Entry or OOB pairing method with Legacy pairing, both of which provide authentication bringing security to level 3.

The connection can only get security level 4 if both peers support LE Secure Connections and either Passkey Entry, Numeric Comparison, or OOB authentication method is used.

The Permissions field of a characteristic determines not only whether the attribute is readable and/or writeable, but also the security level required of that connection for the attribute to be accessible. For instance, if a link is encrypted with security level 2, unauthenticated encryption, the peer will not be able to access any characteristic that requires authenticated security of level 3 or 4.

This way, we can configure our attribute table so that the data can only be exchanged when the link is encrypted with a certain level of security.

**More on this:**
Bluetooth LE has a total of 3 security modes. Security mode 2 uses data signing for security and is rarely used. Security mode 3 pertains to isochronous broadcast which is used with Bluetooth LE Audio and is fairly new. This course only focuses on security mode 1.

## Filter Accept List

Filter Accept List, formerly known as Whitelisting, is a way of limiting access to a list of devices in both advertising and scanning.

When used in advertising, only the devices in the Filter Accept List can send a connection request to establish a connection or send a scan request to get the scan response from the advertiser. If a device not on the list sends these requests, the advertiser will ignore the request.

When used in scanning, only the advertising and scan response packet from the devices in the list will be scanned and reported to the application. The scanner will filter out any packet from other advertisers.

By using the peer’s address and the identity keys distributed at phase 3 of the pairing process, we can build the Filter Accept List to only allow a bonded and authorized device to connect to the device. You can decide if a new device can join this list or not by adding a “pairing mode” which temporarily turns off the Filter Accept List and can turn it back on after the pairing is finished. In exercise 2 of this chapter we will have a look at the implementation of this mechanism.

## Exercise 1: Add pairing support to a Bluetooth LE application

In this exercise, we will start with a version of the Bluetooth Peripheral LBS sample that does not have any security support. This is similar to the application we created in Lesson 4 Exercises 1 and 2, where we created our own custom LED Button Service. All characteristics of the service are open and anyone can read and write to them without any encryption. This also means anyone with a sniffer can follow the connection and read the exchanged data.

We will start by adding the encryption requirement to a LED characteristic’s write permission. Then, we will add pairing support to the application and practice encrypting the link to be able to write to the LED characteristic.

The second part of the exercise focuses on increasing the security level to have man-in-the-middle protection, i.e security level 3 and 4. We will add a display callback to display the passkey in the log output so that we can see the passkey and enter the key to the phone. This way, the end user can ensure that they are pairing to the correct device.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l5/l5_e1`.
This is a slightly modified version of the Peripheral LBS sample in nRF Connect SDK. `lbs.c` and `lbs.h` have been moved from the original SDK folder into the applications `src` folder.

**1. Add a security requirement to the LED characteristic**

1.1 Change the LED characteristic permission to require encryption.
In the declaration of the LED characteristic, add encryption requirement by changing `BT_GATT_PERM_WRITE` to `BT_GATT_PERM_WRITE_ENCRYPT`.
This will change the security level requirement from level 1 (no security) to level 2 (unauthenticated encryption) as covered in Security Models topic earlier.
Change the following code in `lbs.c`:
```c
BT_GATT_CHARACTERISTIC(BT_UUID_LBS_LED,
                       BT_GATT_CHRC_WRITE,
                       BT_GATT_PERM_WRITE_ENCRYPT, // Changed from BT_GATT_PERM_WRITE
                       NULL, write_led, NULL),
```

**2. Build and flash the application to the board.**

**3. Try to write to the LED characteristic.**

In nRF Connect for Mobile, connect to the device `Nordic_LBS`. Try to write to the LED characteristic to turn it on, as we have done in previous exercises. Notice that the LED3 (LED2 on nRF54L15 DK) on the board does not react. This is because the characteristic now requires encryption, but the firmware does not have pairing support. The phone may terminate the connection because of this.
Let’s add pairing support to the firmware.

**4. Add the Security Management Protocol layer to the Bluetooth LE stack.**

The Kconfig symbol `CONFIG_BT_SMP` will add the Security manager Protocol to the Bluetooth LE stack, which is the layer that makes it possible to pair devices over Bluetooth LE.
Add the following line to the `prj.conf` file:
```kconfig
CONFIG_BT_SMP=y
```

**5. Add a callback function for when the security level of the connection has changed.**

Recall the connection callback structure `struct bt_conn_cb` that we used in the previous exercises. Let’s add a callback for the `security_changed` event as well.

5.1 Add the `security_changed` member to the callback structure.
Add the following line in `main.c` (inside `connection_callbacks` struct initialization):
```c
    .security_changed = on_security_changed,
```

5.2 Define the callback function `on_security_changed()`.
We want this callback function to display the current security level of the connection and inform if the link has been encrypted successfully or not.
Add the following code in `main.c` (ensure `on_security_changed` is declared if defined after `connection_callbacks`):
```c
static void on_security_changed(struct bt_conn *conn, bt_security_t level,
                                enum bt_security_err err)
{
	char addr[BT_ADDR_LE_STR_LEN];

	bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));

	if (!err) {
		LOG_INF("Security changed: %s level %u", addr, level); // Corrected newline
	} else {
		LOG_WRN("Security failed: %s level %u err %d", addr, level, // Corrected newline and log level
			err);
	}
}
```

**6. Build and flash the application to the board.**

Open up a terminal to see the log output from the application, which we will need to get the passkey.
Just like in previous exercises, you can go to Visual Studio Code and select the COM port for the device.

**7. Try to write to the LED characteristic.**

In nRF Connect for Mobile, connect to the device `Nordic_LBS`. Try to write to the LED characteristic to turn it on.
Verify that a pairing pop-up appears after you click Write. What happens here is that the phone automatically sends a pairing request after it get rejected when it try to write to the characteristic due to insufficient authentication.
Select Pair to accept the pairing and the LED characteristic should now be possible to control. The Bluetooth LE link is now encrypted.
In the log, you should see the security level updated to level 2 in the UART log:
```
*** Booting nRF Connect SDK ***
Starting Lesson 5 - Exercise 1
Bluetooth initialized
Advertising successfully started
Connected
Security changed 7B:9E:28:DB:38:7A (random) level 2
```

**8. Change the LED characteristic permission to require pairing with authentication**

In the declaration of the LED characteristic, add the authentication requirement by changing `BT_GATT_PERM_WRITE_ENCRYPT` to `BT_GATT_PERM_WRITE_AUTHEN`.
Change the following code in `lbs.c`:
```c
BT_GATT_CHARACTERISTIC(BT_UUID_LBS_LED,
                       BT_GATT_CHRC_WRITE,
                       BT_GATT_PERM_WRITE_AUTHEN, // Changed from BT_GATT_PERM_WRITE_ENCRYPT
                       NULL, write_led, NULL),
```
This will increase the security level of the write permission of this characteristic from level 2 to level 3 or 4, depending in whether you are using legacy pairing or LE Secure Connections.
At this stage, even though you would still be able to pair with the board, the phone wouldn’t be able to control the LED. This is because the security level of the application doesn’t meet the requirement of the characteristic permission.

**9. Define authentication callback functions**

We have the authenticated pairing callback structure `struct bt_conn_auth_cb` with numerous members. In our case, we will only add two.

9.1 Define the callback function `auth_passkey_display`.
Let’s define a function for the `passkey_display` event, which has the signature: `void (*passkey_display)(struct bt_conn *conn, unsigned int passkey);`
This will print the passkey needed for the central (your phone) to pair with the peripheral (the board).
Add the following code in `main.c`:
```c
static void auth_passkey_display(struct bt_conn *conn, unsigned int passkey)
{
	char addr[BT_ADDR_LE_STR_LEN];
	bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));
	LOG_INF("Passkey for %s: %06u", addr, passkey); // Corrected newline
}
```

9.2 Define the callback function `auth_cancel`.
Let’s define a function for the `cancel` event, which has the signature: `void (*cancel)(struct bt_conn *conn);`
This will let us know when the pairing has been cancelled.
Add the following code in `main.c`:
```c
static void auth_cancel(struct bt_conn *conn)
{
	char addr[BT_ADDR_LE_STR_LEN];
	bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));
	LOG_WRN("Pairing cancelled: %s", addr); // Corrected newline and log level
}
```

9.3 Declare the authenticated pairing callback structure `struct bt_conn_auth_cb`.
Let’s now declare the callback structure with the two member functions that we created in the previous steps.
Add the following code to `main.c` (ensure callbacks are declared/defined before this):
```c
static struct bt_conn_auth_cb conn_auth_callbacks = {
	.passkey_display = auth_passkey_display,
	.cancel = auth_cancel,
};
```

**10. Register the authentication callbacks.**

Add the following code in `main.c` (ensure `err` is declared):
```c
// int err; // if not already declared
err = bt_conn_auth_cb_register(&conn_auth_callbacks);
if (err) {
	LOG_ERR("Failed to register authorization callbacks."); // Corrected newline
	return -1; // or handle error
}
```
The application now fulfills the requirements of pairing with MITM authentication needed for security level 3 or level 4.

**11. Build and flash the application on the board.**

11.1 Make sure you select Erase And Flash To Board, to remove the previous bonding information.
_Description: IDE option "Erase And Flash To Board" highlighted._

11.2 Remove the bond information from your phone.
On the phone, you would need to remove the bond information of the device as well.
_Description: Android Bluetooth settings showing "Unpair" option for a device._

**12. Use your phone to connect the device and prompt the pairing request by writing to the LED characteristic.**

As we have done previously, use nRF Connect for Mobile to connect to the device. Then try to write to the LED characteristic and the pairing pop-up window should appear, now with a PIN request.
The passkey, a 6-digit randomly generated number, will be in the log output from the device. You will need to type this passkey to the pop-up window on the phone.
In the log output below, the passkey is `043166`.
```
*** Booting nRF Connect SDK ***
Starting Lesson 5 - Exercise 1
Bluetooth initialized
Advertising successfully started
Connected
Passkey for 48:18:67:01:CC:A8 (random): 043166
```
If you enter the passkey correctly, the phone and the device will pair successfully and you will be able to control the LED.
Verify in the log output that you now have security level 3 (for legacy pairing) or 4 (for LE Secure Connections).
```
Connected
Passkey for 48:18:67:01:CC:A8 (random): 043166
Security changed 48:18:67:01:CC:A8 (random) level 4
```

## Exercise 2: Implement bonding and a Filter Accept List

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In this exercise, we will add storing keys to the application. Then we will use the stored keys to limit the access to only devices previously paired with the peripheral (your board). This is called an Filter Accept List. The peripheral processes only the connection requests from devices in the Filter Accept List. Requests from other devices will be ignored. This makes our device exclusively available to bonded devices.

### Exercise steps

In the GitHub repository for this course, go to the base code for this exercise, found in `l5/l5_e2`.

**1. Add bonding support to the application**

While walking through exercise 1, you may have noticed that if you disconnected your phone from the peripheral and then reconnected, you could re-encrypt the link without pairing again. But if we reset the device and tried to reconnect, we needed to pair again. This is because bonding is supported in SMP by default (through `CONFIG_BT_BONDABLE`).
However, key storing and restoring requires writing data to flash and restoring it from flash. So you will need to include the Bluetooth setting which handles flash, in your application, to be able to store and restore the bond information to flash, through `CONFIG_BT_SETTINGS`.

1.1 Add setting support in your application to store data in flash.
Enable `CONFIG_BT_SETTINGS`, and its dependency `CONFIG_SETTINGS`, to make sure the Bluetooth stack takes care of storing (and restoring) the pairing keys.
Add the following lines to the `prj.conf` file:
```kconfig
# For All other DKs (and generally needed)
CONFIG_SETTINGS=y
CONFIG_BT_SETTINGS=y
CONFIG_FLASH=y
CONFIG_FLASH_PAGE_LAYOUT=y
CONFIG_FLASH_MAP=y
CONFIG_NVS=y
```
_(Note: For nRF54L15 DK, specific configurations might apply if it uses a different flash/NVS setup, but these are generally required for settings persistence.)_

1.2 Include the header file in `main.c`:
```c
#include <zephyr/settings/settings.h>
```

1.3 Call `settings_load()` after initializing Bluetooth so that previous bonds can be restored.
As per the documentation for `CONFIG_BT_SETTINGS`, we must call the API function `settings_load()` manually to be able to store the pairing keys and configuration persistently.
The signature is: `int settings_load(void);` or `int settings_load_subtree(const char *subtree);`
Add the following line in `main.c` (typically after `bt_enable()` and before starting advertising or registering auth callbacks, but the exact placement might depend on when settings are needed):
```c
    // After bt_enable() if it's non-blocking and uses a callback,
    // or after it returns if blocking.
    // If using a bt_ready callback, settings_load might be called there.
    // For simplicity here, assuming it's in main() after bt_enable() succeeds.
    if (bt_is_ready()) { // Or a similar check
        settings_load();
    }
```

1.4 Build and flash the application to your board.

1.5. Verify that after you pair your phone with the device, you can reset the hardware and can connect to the same phone again without having to pair again. This means the information was stored during the first pairing, i.e the devices were bonded.

**2. Delete the stored bond**

Our application can now store bond information. But it should be able to remove the stored bond information when needed as well. We can do this by calling `bt_unpair()`, which has the signature: `int bt_unpair(uint8_t id, const bt_addr_le_t *addr);`

2.1 Add an extra button handling to remove bond information. In this case, we will use button 2 (button 1 on nRF54 DKs).
Add the following line in `main.c`:
```c
#define BOND_DELETE_BUTTON             DK_BTN2_MSK
```

2.2 Call `bt_unpair()` to erase all bonded devices.
We want to erase all bonded devices whenever button 2 is pressed, by calling `bt_unpair()` with `BT_ID_DEFAULT` as the address. This will erase all bonded devices. If you want to erase one single device in the bond list, you would need to input the address of the device you want to delete.
Add the following code in the `button_changed()` function in `main.c`:
```c
    if (has_changed & BOND_DELETE_BUTTON) {
        uint32_t bond_delete_button_state = button_state & BOND_DELETE_BUTTON;
        // Typically, action is on button press (state becomes 1 if active high, or 0 if active low and pressed)
        // Assuming button_state is 0 when pressed for active low buttons (common on DKs)
        if (bond_delete_button_state == 0) { // Or adjust based on your button logic
            int err = bt_unpair(BT_ID_DEFAULT, BT_ADDR_LE_ANY);
            if (err) {
                LOG_ERR("Cannot delete bond (err: %d)", err); // Corrected log level
            } else {
                LOG_INF("Bond deleted successfully"); // Corrected newline
            }
        }
    }
```

2.3 Build and flash the application to your board.

2.4. Connect your smart phone to the device then disconnect and press button 2 (button 1 on nRF54 DKs) to erase all bonded devices. If you try connecting again, you will notice that the phone can’t re-encrypt the link. This usually results in the connection being dropped. You would need to remove the bond on the phone (in Bluetooth settings -> Forget this device) before you connect again to be able to make a new pairing.

**3. Add a Filter Accept List to the application.**

Now that we have the bond information stored in flash, we will use it to create a Filter Accept List that will only allow the devices on this list to connect to the peripheral.

3.1 Enable support for Filter Accept List and Privacy Features.
Let’s enable the Filter Accept List API (`CONFIG_BT_FILTER_ACCEPT_LIST`) and the Private Feature support, which makes it possible to generate and use Resolvable Private Addresses (`CONFIG_BT_PRIVACY`).
Add the following lines in the `prj.conf` file:
```kconfig
CONFIG_BT_FILTER_ACCEPT_LIST=y
CONFIG_BT_PRIVACY=y
```

3.2 Add new advertising parameters based on the Filter Accept List.
We want our advertising packet to depend on whether or not we are using the Filter Accept List. Let’s create two different ones using the `BT_LE_ADV_PARAM` helper macro that we used in Lesson 2.
The `BT_LE_ADV_PARAM()` helper macro signature: `BT_LE_ADV_PARAM(options, interval_min, interval_max, peer)`

3.2.1 Define the advertising parameter `BT_LE_ADV_CONN_NO_ACCEPT_LIST` for when the Filter Accept List is not used.
For options, we want the advertising to be connectable by using `BT_LE_ADV_OPT_CONNECTABLE`. We also want to use `BT_LE_ADV_OPT_ONE_TIME`, so the device will not automatically advertise after disconnecting. So that we can do advertise with the new Filter Accept List after it’s bonded to the first device.
Define in `main.c` or a relevant header:
```c
#define BT_LE_ADV_CONN_NO_ACCEPT_LIST  BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE|BT_LE_ADV_OPT_ONE_TIME, \
                                       BT_GAP_ADV_FAST_INT_MIN_2, \
                                       BT_GAP_ADV_FAST_INT_MAX_2, NULL)
```

3.2.2 Define the advertising parameter `BT_LE_ADV_CONN_ACCEPT_LIST` for when the Filter Accept List is used.
This will be similar to the previous one. However, we will use `BT_LE_ADV_OPT_FILTER_CONN` to filter out the connection requests from devices not in the list.
Define in `main.c` or a relevant header:
```c
#define BT_LE_ADV_CONN_ACCEPT_LIST BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE|BT_LE_ADV_OPT_FILTER_CONN|BT_LE_ADV_OPT_ONE_TIME, \
                                       BT_GAP_ADV_FAST_INT_MIN_2, \
                                       BT_GAP_ADV_FAST_INT_MAX_2, NULL)
```

3.3 Define the function `setup_accept_list()` to loop through the bond list and add the addresses to the Filter Accept List.

3.3.1 Define the callback `setup_accept_list_cb` to add an address to the Filter Accept List.
Define the callback function that will be called for every iteration of the bond list to add the peer address to the Filter Accept List, using `bt_le_filter_accept_list_add()`, which has the signature: `int bt_le_filter_accept_list_add(const bt_addr_le_t *addr);`
Add the following code snippet in `main.c`:
```c
static void setup_accept_list_cb(const struct bt_bond_info *info, void *user_data)
{
	int *bond_cnt = user_data;
	if ((*bond_cnt) < 0) { // Stop if a previous add failed
		return;
	}
	int err = bt_le_filter_accept_list_add(&info->addr);
    char addr_str[BT_ADDR_LE_STR_LEN];
    bt_addr_le_to_str(&info->addr, addr_str, sizeof(addr_str));
	LOG_INF("Attempting to add peer %s to Filter Accept List", addr_str); // Corrected log
	if (err) {
		LOG_ERR("Cannot add peer %s to Filter Accept List (err: %d)", addr_str, err); // Corrected log
		(*bond_cnt) = -EIO; // Indicate error
	} else {
		(*bond_cnt)++;
	}
}
```

3.3.2 Define a function to iterate through all existing bonds, using `bt_foreach_bond()` and then call `setup_accept_list_cb()`.
We can use the function `bt_foreach_bond()` to iterate through all existing bonds. Signature: `void bt_foreach_bond(uint8_t id, bt_bond_cb_t func, void *user_data);`
For each bond, we will call `setup_accept_list_cb()` to add the peer address into the Filter Accept List.
Add the following function in `main.c`:
```c
static int setup_accept_list(uint8_t local_id)
{
	int err = bt_le_filter_accept_list_clear();
	if (err) {
		LOG_ERR("Cannot clear Filter Accept List (err: %d)", err);
		return err;
	}
	int bond_cnt = 0;
	bt_foreach_bond(local_id, setup_accept_list_cb, &bond_cnt);
	return bond_cnt; // Returns number of successfully added bonds or negative error code
}
```

3.4.1 Define the function `advertise_with_acceptlist()` to begin advertising with the Filter Accept List.
The next step is to make a work queue function that will call `setup_accept_list()` to build the Filter Accept List, and then to start advertising with the Filter Accept List (if it is non-empty), otherwise, advertise with no Filter Accept List.
In this function, we will advertise with `BT_LE_ADV_CONN_NO_ACCEPT_LIST` if the list is empty. This will do open advertising, but the advertising will not automatically restart when disconnected as explained earlier at step 3.2.
This way we will be able to change advertising setting to use Filter Accept List when disconnected.
Notice how it’s defined as a work queue thread instead of a normal function. The reason for it is explained at Step 3.5.
Add the following code in `main.c` (ensure `ad` and `sd` advertising data arrays are defined):
```c
// Assuming ad and sd are globally defined advertising data structures
void advertise_with_acceptlist(struct k_work *work)
{
	int err=0;
	int allowed_cnt = setup_accept_list(BT_ID_DEFAULT);
	if (allowed_cnt < 0){
		LOG_ERR("Acceptlist setup failed (err:%d)", allowed_cnt); // Corrected log
	} else {
		if (allowed_cnt == 0){
			LOG_INF("Advertising with no Filter Accept list");
			err = bt_le_adv_start(BT_LE_ADV_CONN_NO_ACCEPT_LIST, ad, ARRAY_SIZE(ad),
					sd, ARRAY_SIZE(sd));
		}
		else {
			LOG_INF("Acceptlist setup, number of devices = %d", allowed_cnt); // Corrected log
			err = bt_le_adv_start(BT_LE_ADV_CONN_ACCEPT_LIST, ad, ARRAY_SIZE(ad),
				sd, ARRAY_SIZE(sd));
		}
		if (err) {
		 	LOG_ERR("Advertising failed to start (err %d)", err); // Corrected log
			return;
		}
		LOG_INF("Advertising successfully started");
	}
}
K_WORK_DEFINE(advertise_acceptlist_work, advertise_with_acceptlist);
```

3.4.2 Submit this work queue in `main`, right before the original advertising code (or replacing it).
In `main()`:
```c
    // Remove or comment out previous bt_le_adv_start()
    k_work_submit(&advertise_acceptlist_work);
```

3.4.3 Remove the original advertising code that advertises without using Filter Accept List.
(This step is covered by 3.4.2 if the old code is removed/commented).

3.5 Submit the same work queue in the `on_disconnected()` callback.
Submit the work queue for `advertise_acceptlist()` in the callback for a disconnected event. So if there is any new bond we will have it updated to the Filter Accept List upon disconnection.
In `on_disconnected()`:
```c
    // Inside on_disconnected()
    k_work_submit(&advertise_acceptlist_work);
```
We submit a work item here because if we call `bt_le_adv_start()` directly in callback we will receive an `-ENOMEM` error (-12). This is because in the `disconnected()` callback, the connection object is still reserved for the connection that was just terminated. If we start advertising here, we will need to increase the maximum number of connections (`CONFIG_BT_MAX_CONN`) by one., in our case, it would need to be two. In order to save on RAM, we submit a work item using `k_work_submit` that will delay starting advertising until after the callback has returned.

3.6 Verify if the Filter Accept List works as intended.
To perform this step, you will need an extra phone or a central device to verify if the Filter Accept List works or not. We will start by erasing the bond information on both the Nordic hardware and your phone that has previously been connected to the device. Next, connect and bond the device with your phone, as we have done previously, and make sure you can control the LED from your phone. Then disconnect.
Now use another central device to connect to the Nordic device. If the Filter Accept List works as it should, you will not be able to connect with this new central device. Now use the original phone that you have bonded to the Nordic device and you should be able to connect.
This shows that the Filter Accept List now works as expected. The device only accepts connections from the previously bonded phone.

**4. Add “Pairing mode” to allow new devices to be added to the Filter Accept List**

The code we have built so far, only allows a single device to be added to the Filter Accept List.
To allow new devices to connect and bond, we need to add an option to do “open advertising”, often called “Pairing mode”. We will use a button press to enable “Pairing mode”.

4.1 Increase the number of maximum paired devices.
Increase the number of paired devices allowed at one time, using `CONFIG_BT_MAX_PAIRED`, which has a default value of 1.
Let’s increase this to 5, by adding the following line in the `prj.conf` file:
```kconfig
CONFIG_BT_MAX_PAIRED=5
```

4.2.1 Add the button handling code to enable pairing mode.
Define a new button for “pairing mode”. We will use button 3.
In `main.c`:
```c
#define PAIRING_BUTTON             DK_BTN3_MSK
```

4.2.2 Add the following code to `button_changed()` callback.
When button 3 is pressed, we want to stop advertising, clear the Filter Accept List and start to advertise with the advertising parameters we made for the case with no Filter Accept List.
Add the following code in `main.c` (inside `button_changed()`):
```c
    if (has_changed & PAIRING_BUTTON) {
        uint32_t pairing_button_state = button_state & PAIRING_BUTTON;
        // Assuming button_state is 0 when pressed for active low buttons
        if (pairing_button_state == 0) { // Or adjust based on your button logic
            int err_code = bt_le_adv_stop();
            if (err_code) {
                LOG_ERR("Cannot stop advertising err= %d", err_code); // Corrected log
                return;
            }
            err_code = bt_le_filter_accept_list_clear();
            if (err_code) {
                LOG_ERR("Cannot clear accept list (err: %d)", err_code); // Corrected log
            } else {
                LOG_INF("Filter Accept List cleared successfully"); // Corrected newline
            }
            err_code = bt_le_adv_start(BT_LE_ADV_CONN_NO_ACCEPT_LIST, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
            if (err_code) {
                LOG_ERR("Cannot start open advertising (err: %d)", err_code); // Corrected log
            } else {
                LOG_INF("Advertising in pairing mode started");
            }
        }
    }
```
Note that if you want to advertise with an Filter Accept List again you have two options: either reset the device or make a new bond then disconnect.
> **Note**
> The button should only be pressed when the device is advertising and not connected to a peer. It is possible to set a flag, so that if the device is in a connection it will return to open advertising once it is disconnected. But this is not covered in the scope of this exercise.

4.3 Verify the pairing mode.
You will need an extra phone or a central device to perform this step. Start by erasing the bond information on the Nordic hardware and your phone that was previously connected to the device. Next, connect and bond the device with your phone, as we have done previously, and ensure you can control the LED from your phone. Then disconnect.
Now use another central device to try and connect to the Nordic device. Just like we saw previously, you should not be able to connect.
Now press button 3 (button 2 on nRF54L15 DK) to enable “Pairing mode”. When in “Pairing mode”, try to use the second phone to connect again. This time it should be able to connect, and you can perform pairing with this phone. After this, your Filter Accept List will contain 2 devices.# Sniffing Bluetooth LE packets

A Bluetooth sniffer is a tool used to intercept the Bluetooth LE packets as they are transmitted, ie. “sniff” the packets, and view them in real-time. This not only provides an overview of what happens over the air but also offers you a better understanding of the protocol. It gives you very detailed information about each and every packet exchanged between two Bluetooth LE devices in near real-time, even when the connection is encrypted.

It’s also an excellent tool to capture and provide the sniffer trace to our Technical Support team so that they can quickly inspect your data without having to reproduce the whole setup on their side. This can significantly speed up the investigation and troubleshooting process.

## nRF Sniffer for Bluetooth LE

Nordic provides a simple-to-use and easy-to-set-up Bluetooth LE Sniffer called the nRF Sniffer for Bluetooth LE. nRF Sniffer works by running in Bluetooth LE hardware placed in radio range of the Bluetooth LE communication you would like to debug. Therefore, it requires an extra nRF52 development kit or dongle to use as the hardware for the sniffer.

_Diagram illustrating a Bluetooth LE sniffer setup with a DK/Dongle capturing packets between two communicating BLE devices._

nRF Sniffer was initially built in the spare time of our engineers when they were developing Bluetooth LE applications. The aim was to have an alternative to the rather expensive professional Bluetooth LE sniffer equipment to test and verify our own Bluetooth LE stack. And it quickly proved to be an imperative tool, not only for us but also for our customers. Anyone with a spare nRF52 development kit can use it as a sniffer for debugging.

### How does nRF Sniffer work?

The sniffer works by using the radio hardware on the Nordic SoC running Nordic proprietary firmware that utilizes said radio to observe and analyze Bluetooth LE packets between other devices. The firmware does not use the Bluetooth stack we have been using in this course, but a stack that was written in bare metal (i.e without an operating system). This gives the sniffer more flexibility and control over how we can utilize the radio to capture Bluetooth LE packets.

Since the Nordic chips only have one antenna, the sniffer can only observe a single RF channel at a time. As we have covered, Bluetooth LE advertising transmits advertisement packets on three channels, channel 37, 38 and 39. This is solved by utilizing the advertising pattern. So the majority of the time, the sniffer will scan in the first channel in the pattern, say channel 37. When it captures a packet in channel 37, it will automatically switch to scanning channel 38 until it has captured another packet, and then switch to channel 39.

What about connection-oriented communication where up to 37 channels can be used? Luckily, the channel hopping when in connection can be easily tracked by looking at the connection request and the channel map update. nRF Sniffer will automatically detect that and follow the channel hopping of the connection.

Because of the limitations on the SoC (with only one radio and one antenna) it is not possible to follow more than one connection at a time. For example, if you are following the connection from an advertising device, you will not be able to capture advertising packets from other devices.

## Setting up nRF Sniffer for Bluetooth LE

In this chapter, we will go through how to set up nRF Sniffer and verify that it functional by sniffing a Bluetooth LE packet.

nRF Sniffer has a comprehensive documentation on how to setup the nRF Sniffer on your computer. Since the time of writing this chapter the way of installing nRF Sniffer has been changed. You can either follow the linked documentation to use `nrfutil` tool to install the Sniffer for your or you can continue with the manual installation described in this document. It’s recommended to follow the instruction in the nRFSniffer’s documentation linked above as it should contain the most up-to-date installation instructions.

### Programming the nRF Sniffer firmware

The nRF Sniffer firmware supports the following boards:

*   nRF52840 DK
*   nRF52840 Dongle
*   nRF52833 DK
*   nRF52 DK
*   nRF51 DK
*   nRF51 Dongle

> **Important**
> Due to a recent update of the nRF52833 DK version 3 and nRF52840 DK version 3, the new Interface IC on the DK is not fully compatible with the nRF Sniffer software. If you have an nRF52840DK v3, you will need to use the nRF USB port instead of the Interface IC USB port. The nRF52833 DK v3 is not compatible with the sniffer software at the moment, so you will need to use another DK as the sniffer backend. nRF52833 DK v2 and earlier works fine.

#### Download the firmware

1.  Download nRF Sniffer for Bluetooth LE v4.x or later and extract the contents of the zip file into a folder of your choice.
    In the following sections, this folder is referred to as `Sniffer_Software`.
    All the firmware HEX files are located in `Sniffer_Software/hex`.

    | Development kit/dongle | Firmware file name                        |
    | :--------------------- | :---------------------------------------- |
    | nRF52840 DK            | `sniffer_nrf52840dk_nrf52840_*.hex`       |
    | nRF52840 Dongle        | `sniffer_nrf52840dongle_nrf52840_*.hex`   |
    | nRF52833 DK            | `sniffer_nrf52833dk_nrf52833_*.hex`       |
    | nRF52 DK               | `sniffer_nrf52dk_nrf52832_*.hex`          |
    | nRF51 DK               | `sniffer_nrf51dk_nrf51422_*.hex`          |
    | nRF51 Dongle           | `sniffer_nrf51dongle_nrf51422_*.hex`      |

2.  Open up nRF Connect for Desktop and install and launch the Programmer application.
    On macOS and Linux: install the SEGGER J-Link software before proceeding to the next step.
    If you are running an M1-based Mac, you must install the Intel/x86 variants of J-Link.

3.  In the upper left hand corner, select the board you are using as the Bluetooth LE sniffer.

4.  Select Add file and Browse, then navigate to `Sniffer_Software/hex` and select the file that applies to the hardware you are using, see the table above. Select Open.

5.  Click Erase & write to flash the firmware to your board.

_Screenshot of nRF Connect Programmer application showing device selection, adding HEX file, and erase & write button._

### Installing Wireshark

This will explain the installation process for Windows and macOS. For instructions on Ubuntu Linux, see Installing Wireshark on Ubuntu Linux.

1.  Go to the [Wireshark download page](https://www.wireshark.org/download.html).
2.  In the Stable Release list at the top of the page, select the release package for your operating system.
    The download should start automatically.
3.  Open up the file when it’s finished downloading, and follow the instructions to download Wireshark.

Wireshark is an open-source packet analyzer, and can be used for many different protocols. To use it with the nRF Sniffer firmware, we offer an external capture plugin to use with Wireshark.

### Installing the nRF Sniffer capture tool

The nRF Sniffer capture tool comes either as stand alone tool or as an external capture plugin for Wireshark.

1.  Install nRF Sniffer command.
    1.1 Open a command window and navigate to the folder `Sniffer_Software/extcap`.
    1.2 Run the following commands to install Python’s requirements (make sure you have Python v3.6 or later installed on your computer):
    ```bash
    pip3 install -r requirements.txt
    ```

2.  Copy the nRF Sniffer capture tool into Wireshark
    2.1 Open Wireshark
    2.2 Go to Help > About Wireshark (on Windows or Linux) or Wireshark > About Wireshark (on macOS).
    2.3 Select the Folders tab.
    2.4 Double-click the location for the Personal Extcap path to open this folder.
    _Screenshot of Wireshark About dialog, Folders tab, highlighting Personal Extcap path._
    You may be prompted with a notice saying `The directory does not exist.` Click Yes to create it.
    2.5 Copy the contents of the `Sniffer_Software/extcap/` folder into this folder.
    _Screenshot showing files from `extcap` folder being copied to Wireshark's Personal Extcap folder._

3.  Enable the nRF Sniffer capture tool in Wireshark.
    3.1 Refresh the interfaces in Wireshark by selecting Capture > Refresh Interfaces or pressing F5.
    3.2 Select View > Interface Toolbars > nRF Sniffer for Bluetooth LE to enable the nRF Sniffer interface.
    You should see that nRF Sniffer is displayed as one of the interfaces on the Wireshark capture screen, and you should see the nRF Sniffer toolbar.
    _Screenshot of Wireshark interface showing nRF Sniffer as a capture interface and its toolbar._

### Running the nRF Sniffer

1.  To start sniffing, make sure the nRF Sniffer (your DK or dongle running the nRF Sniffer firmware) is turned on and place it between the two devices that are communicating over Bluetooth LE.
    _Diagram showing the physical setup for sniffing: two BLE devices communicating, with the nRF Sniffer DK/Dongle placed between them._

2.  In Wireshark, under Capture, double-click on the hardware interface `nRF Sniffer for Bluetooth LE COM port`, see below.
    _Screenshot of Wireshark capture interface selection, highlighting the nRF Sniffer COM port._

3.  Wireshark should now look something like the image below, listing all Bluetooth LE packets in radio range.
    _Screenshot of Wireshark live capture window showing a list of Bluetooth LE packets._

### Explaining Wireshark in Live Capture

Before proceeding to the exercise portion of this lesson, let’s explain what we are seeing in the Wireshark window.
Your window should be divided into three parts, the packet list, packet details and packet bytes.
If you cannot see all three windows, select View and make sure the following three lines are checked off:
_Screenshot of Wireshark View menu options related to displaying Packet List, Packet Details, and Packet Bytes panes._

*   **Packet List:** Displays all the packets in the current capture session. Each line corresponds to one packet, and if you select a line, more details about the packet will be displayed in the “Packet Details” and “Packet Bytes” panes, below.
*   **Packet Details:** Shows the current packet, selected in the Packet List window, in a more detailed form.
*   **Packet Bytes:** Shows the data of the current packet, selected in the Packet List window, in a hexdump style.

Clicking on a specific section of the data in the Packet Bytes window will show where in the Packet Details window. And similarly, selecting a header in the Packet Details window, will show where in the data this information is defined, in the Packet Bytes window.

#### Columns in the Packet List window

Let’s take a look at the columns in the Packet List window. Your column headers should look like this:
_Screenshot of Wireshark column headers: No., Time, Source, Protocol, Length, Info._

If you are missing any of the column headers, go to the Packet Details window and expand `nRF Sniffer for Bluetooth LE`. Then right-click on any of the parameters you are missing, select `Apply as Column` and it will show up in the main view as a column.
_Screenshot showing how to right-click on a parameter in Packet Details and select "Apply as Column"._

Now you should have the following column headers in your live capture view.
_Screenshot showing updated Wireshark column headers including Event counter, Channel Index, Delta time._

*   **No.:** The packet number, incremented for every packet the sniffer captures.
*   **Time:** The timestamp for when the packet was captured, relative to how long the sniffer has been running.
*   **Source:** The address of the device that the packet came from.
*   **Protocol:** Which Bluetooth LE stack layer the packet came from, most will come from the link layer (LE LL). Connection parameter updates come from L2CAP, while GATT operations come from the ATT layer, and packets having to do with encrypting and pairing come from SMP.
*   **Length:** The number of bytes captured in the packet.
*   **Event counter:** The instant number of each connection event starting from 0 when the connection is established.
*   **Channel Index:** Channel number the packet was captured on.
*   **Delta time (start to start):** The time between the start of the previous packet until the start of the current packet. It’s often used to count the distance between each connection event, and very close to the actual connection interval.
*   **Info:** Information about the packet.

You are now ready for the exercise portion of this lesson, where we will go into more detail on what you are seeing.

> **Important**
> If you have issues setting up the nRF Sniffer, there is a [Troubleshooting section](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fug_sniffer_ble%2FUG%2Fsniffer_ble%2Ftroubleshooting.html) from the documentation that you can take a look at.

## Exercise 1: Capture and analyze Bluetooth advertising packets

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

This exercise builds on the firmware we made in Exercise 2 of Lesson 2, where the peripheral advertised in scannable, non-connectable mode, and we also made a scan response packet containing a URL.
We will use the sniffer to capture advertising packets and analyze the content of the advertising packet, as well as the scan request packet and scan response packet.

### Exercise steps

In the GitHub repository for this course, go to the code for this exercise, found in `l6/l6_e1`.
Note that this is the same firmware as the solution to exercise 2 found in `l2/l2_e2_sol`.

1.  **Build and flash the application on your board.**
    LED1 on your board should be blinking (or LED0 on nRF54 Series devices), indicating that your board is advertising.

2.  **Run the sniffer on Wireshark**
    Open Wireshark. Under Capture, double-click on the hardware interface `nRF Sniffer for Bluetooth LE COM port`, just like we did when setting up nRF Sniffer.

3.  **Filter advertising packets from “Nordic_Beacon“**
    You may notice that the captured advertising packets are from multiple different advertising devices.
    Let’s filter these out, by clicking on the Device drop-down list to find the “Nordic_Beacon“.
    _Screenshot of nRF Sniffer toolbar in Wireshark, highlighting the Device drop-down list._
    > **Note**
    > If the name of the advertiser is not shown, you can also look for the address. You can find the address of the device in nRF Connect for Mobile (on Android).

    Now you should only see the advertising packets from this device, including the scan requests and scan response related to this device.
    _Screenshot showing Wireshark filtered to display packets only from "Nordic_Beacon"._
    Make sure that the “Automatic Scroll” function is enabled to always see the latest packets.
    _Screenshot of Wireshark toolbar, highlighting the "Automatic Scroll" button._
    > **Note**
    > Since the peripheral in exercise 2 from lesson 2 uses a randomly generated address that is assigned boot-up, resetting the device will give it a new address. The sniffer won’t be able to track that, so you will need to select “All advertising devices” to track all advertisers and then select the new Nordic_Beacon device with the new address.

4.  **(optional) Apply an RSSI filter for the Capture interface**
    If you are working in a dense environment, with many Bluetooth LE devices, this list of devices can be quite long. In the next step, we will filter out these devices based on their vicinity to the sniffer, using the RSSI. If you don’t have a problem with too many devices, you can skip straight to step 5.
    Let’s apply a filter for the capture interface, based on the RSSI, or Received Signal Strength Indicator, of the advertising packets.

    4.1 Close and re-open Wireshark, to see the Capture menu again.
    4.2 In the Capture interface selection, type in `RSSI >= -50`.
    Make sure to click on `nRF Sniffer for Bluetooth LE COM port` before typing in the filter. Otherwise, the bar will turn red.
    This will filter out all Bluetooth LE packets that have RSSI smaller than -50dBm.
    _Screenshot showing Wireshark capture filter input field with `RSSI >= -50` entered._
    4.3 Start the sniffer again, and you should see much fewer devices in the Device drop-down list.

5.  **Inspect the broadcasted advertising packets**
    _Screenshot of Wireshark showing ADV_SCAN_IND packets from Nordic_Beacon on channels 37, 38, 39 with ~500ms interval._
    1. First, observe that the advertising packets are of type `ADV_SCAN_IND`, which is non-connectable and scannable. This means the advertiser will accept scan request, but not connection requests.
    2. Notice that the advertising packets are broadcasted consecutively on the three advertising channels 37, 38 and 39.

    Another thing to note, in the `Delta time` column, is that the advertising interval is roughly 500 ms. The three packets are relatively close together, with around 1.5ms between them, and then about 500ms later, another cluster of three advertising packets are sent.
    Notice the slight difference in the delta time between each advertising event. It’s not exactly 500ms between them. This is because of the 10ms random delay added to each advertising event to avoid continuous collisions if two advertisers have the same advertising interval.

6.  **Inspect the contents of an advertising packet**
    Let’s inspect an advertising packet, by clicking on a `ADV_SCAN_IND` packet from the Nordic_Beacon device.
    The bottom half of your window (the Packet Details and Packet Bytes window) will now be updated to show this advertising packet.
    _Screenshot of Wireshark Packet Details and Packet Bytes panes for an ADV_SCAN_IND packet._
    Expand `Bluetooth Low Energy Link Layer` and `Advertising Data`. Clicking on the different subitems (Flags, Device Name, Manufacturer Specific) will highlight in which part of the packet this data is.
    We can match the advertising data in binary to the format we learned in Lesson 2. Recall that the advertising data consists of multiple advertising data structures, starting with the length followed by the type and then the content.
    _Diagram illustrating the AD structure: Length, AD Type, AD Data._
    In this case, we can see `0x02 0x01 0x04` is the first advertising structure. In this we have the length is `0x02` byte, the type is `0x01` (meaning it’s a flag) and the value of the flag is `BT_LE_AD_NO_BREDR` (`0x04`). You can find the same pattern repeated with the Manufacturer Specific data, starting with the length `0x05`, then the type `0xFF` (Manufacturer Specific), and the actual contents which consist of the Company ID (`0x0059`) and then the Data `0x0000`.

7.  **Inspect the scan response packet**
    To inspect a scan response packet, we need the central, i.e your smartphone, to send a scan request packet to the advertiser.

    7.1 Open the nRF Connect for Mobile application and start scanning. This will trigger the phone to automatically send a scan request.
    The `SCAN_REQ` (Scan Request) from the scanner is sent after an advertising packet (in this case on channel 39) and it is followed by a `SCAN_RSP` (Scan Response) from the advertiser. Both `SCAN_REQ` and `SCAN_RSP` is performed on the same channel as the advertising packet it follows.
    7.2 Select the `SCAN_RSP` packet to inspect the contents.
    _Screenshot of Wireshark SCAN_RSP packet details showing URI data._
    You can find the same pattern of the advertising structure here. It starts with the length `0x1A` (26 bytes) followed by type `0x24` (which is URI) and then the actual data which is the URL: `//academy.nordicsemi.com`

8.  **Observe the dynamic data being updated**
    Recall from lesson 2 exercise 2, that we learned how to dynamically change the contents of the advertising data, triggered by pressing button 1.

    8.1 Select any of the advertising packets, `ADV_SCAN_IND`, and observe the Manufacturer Specific data value of `0x0000`.
    _Screenshot of Wireshark showing Manufacturer Specific Data as 0x0000._
    8.2 Now press button 1 on the board acting as the peripheral.
    8.3 Inspect a new advertising packet.
    Observe that the contents of the advertising packets will now be updated, to `0x0100`.
    _Screenshot of Wireshark showing Manufacturer Specific Data updated to 0x0100._
    Each time you press button 1 on the board that is advertising, the value of the Manufacturer Specific Data will be increased by one.
    > **Note**
    > Bluetooth LE uses little endianness to represent the data in GAP and GATT layers, which is why it increments from `0x00 00` to `0x01 00`, etc.

## Exercise 2: Inspect a Bluetooth connection, analyze GAP and GATT packets

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

In this exercise, we will be sniffing the packets in a Bluetooth LE connection between your Nordic device and your phone. This exercise will help you apply what you learned in Lesson 3 about connection establishment and connection parameters to what actually happens over the Bluetooth LE link.
We will be using the application we made in Lesson 3 Exercise 2 for this exercise.

### Exercise steps

In the GitHub repository for this course, go to the code for this exercise, found in `l6/l6_e2`.
Note that this is the same firmware as the solution to exercise 2 found in `l3/l3_e2_sol`.

1.  **Build and flash the application on your board.**
    LED1 (LED0 on nRF54 DKs) on your board should be blinking, indicating that your board is advertising.

2.  **Filter only the device packets from Nordic_Peripheral.**
    In Wireshark, run the sniffer again and open the Device drop-down list to select `Nordic_Peripheral`. If you only see the name from the previous exercise (Nordic_Beacon), you may need to close Wireshark, and open it again.
    If there are too many devices, you can use the RSSI filter as we did in the previous exercise.
    _Screenshot of Wireshark Device drop-down list._
    After you select `Nordic_Peripheral`, you should only see the packets from this device, in this case, the device address is `cd:f6:1b:aa:5f`. Here we can see mainly advertising packets (`ADV_IND`), and some scan requests (`SCAN_REQ`) and scan response (`SCAN_RESP`) from the same advertiser.
    _Screenshot of Wireshark filtered for "Nordic_Peripheral" showing ADV_IND, SCAN_REQ, SCAN_RSP packets._
    Make sure that the “Automatic Scroll” function is enabled to see the latest packets.
    _Screenshot of Wireshark Automatic Scroll button._

3.  **Establish a Bluetooth LE connection**
    Launch nRF Connect for Mobile and connect to the `Nordic_Peripheral` device, just like we have done several times previously.
    When the connection is established, you should be able to see this from the nRF Sniffer in Wireshark.
    _Screenshot of Wireshark showing a connection established, with many Empty PDU packets._
    Notice a large number of packets being exchanged between the peers at a high speed. Most of them are empty PDU packets.
    > **Note**
    > If you don’t see any empty PDU packets, the sniffer may have missed the connection. This happens if the sniffer fails to capture the connection request packet to follow the connection. Try to connect again, by disconnecting the peripheral from the nRF Connect application, and initiating the connection again.

4.  **Inspect the connection parameter update request packet.**
    Find a packet with the Info: “Connection Parameter Update Request”, from the L2CAP protocol, see below.
    It might be a good idea to turn off “Auto Scroll” to easier navigate through all the captured packets.
    _Screenshot of Wireshark showing an L2CAP Connection Parameter Update Request packet._
    Expand `Bluetooth L2CAP Protocol` and `Command: Connection Parameter Update Request` to find the request minimum and maximum connection interval of 800 (1000 ms) which is what we requested in Lesson 3 Exercise 2.

5.  **Inspect the connection update indication packet (`LL_CONNECTION_UPDATE_IND`).**
    Right after the request, you can see the `LL_CONNECT_UPDATE_IND` packet from the phone. This packet dictates the new updated connection parameters according to what was requested by the peripheral.
    _Screenshot of Wireshark showing an LL_CONNECTION_UPDATE_IND packet._
    Inspecting `LL_CONNECT_UPDATE_IND` will show you the new connection parameters. In this case, we see the connection interval of 800 (1000ms) and the connection timeout of 400 (4 seconds). This corresponds to what was requested in the code. Also, notice the `Instant` value of 177. This value tells the peers at which connection event the new parameters will take effect.
    As we can see from the `Delta time` column of the packets after this, the new connection interval of 1000 ms takes effect at Event number 177.

6.  **Apply a filter to filter out the empty data packets.**
    The majority of the packets you see in the Live Capture are just empty PDU packets that are sent to keep-alive the connection between the peers. The central sends a packet at the beginning of the connection event and the peripheral responds with a packet as an Acknowledge. When they don’t have anything to send, they simply send Empty PDU packets that only contain a data header and no payload. Without these packets being sent and acknowledged, the connection times out after the connection supervision timeout.
    However, these Empty PDU packets make it difficult to inspect the communication, especially when you need to find a certain meaningful packet. The best way of solving this is to create a filter to hide these Empty PDUs.
    Let’s apply the filter by selecting an Empty PDU. Then in the Packet Details window, expand `Data Header` and right-click where it says `Length: 0`. Then click `Apply as a Filter > Not Selected`.
    _Screenshot showing how to apply a Wireshark filter to hide Empty PDU packets by right-clicking on "Length: 0"._
    Alternatively, you can write the filter manually in the “Apply a display filter” text box in the top left corner. To filter out packets with empty length you can enter the following filter command: `!(btle.data_header.length == 0)`
    After the filter has been applied, you will only see the packets that actually have data payload.
    _Screenshot of Wireshark with Empty PDU filter applied, showing only packets with data payload._

7.  **Inspect the communication when connected.**
    Now that all the empty packets are filtered out, let’s inspect the packet exchanges when two devices are connected.
    The following image shows the anatomy of a connection between the phone and the “Nordic_Peripheral” where we enable notification on the button characteristic via the phone and then press and release the button a few times:
    _Screenshot of Wireshark showing a sequence of packets: CONNECT_IND, LL_PHY_REQ, Write Request (to CCCD), Handle Value Notification (for button press/release)._
    Try to reproduce a similar capture log, by subscribing to notifications from the Button Characteristic in nRF Connect for Mobile, like we have done in previous exercises.
    Let’s inspect some of the other packets in the connection lifecycle.

    7.1 Inspect the connection request, `CONNECT_IND`.
    The connection request is sent from your phone to the device, when you select Connect in nRF Connect for Mobile. This is where we will find the initial connection parameters, like the connection interval and the connection supervision timeout.
    _Screenshot of Wireshark CONNECT_IND packet details showing initial connection parameters._
    Here we can see that we get an initial connection interval of 30 ms, which explains the delta time between the empty PDU packet we saw in a previous step. And a connection supervision timeout of 5000 ms.

    7.2 Inspect the PHY request, `LL_PHY_REQ`.
    The packet `LL_PHY_REQ` is the request from the peripheral to use 2M PHY radio mode, where the peripheral informs that it prefers to use the LE 2M PHY (left image). We can also see the response from the central in `LL_PHY_UPDATE_IND`, indicating that LE 2M PHY shall be used (right image).
    _Left: Screenshot of Wireshark LL_PHY_REQ packet. Right: Screenshot of Wireshark LL_PHY_UPDATE_IND packet._
    > **Note**
    > The actual packets exchanged depend on whether the central or peripheral initiates the procedure.
    > If the procedure is initiated by the central, which is what happened in this case, it sends an `LL_PHY_REQ` and the peripheral responds with an `LL_PHY_RESP`, before the central sends the `LL_PHY_UPDATE_IND`.
    > If the procedure is initiated by the peripheral, it sends an `LL_PHY_REQ` and the central responds directly with an `LL_PHY_UPDATE_IND`.

    7.3 Inspect the write request to the CCCD to enable notifications.
    Find the packet that sends a write request with the handle of the CCCD attribute (`0x0013`). Upon inspection, notice that it is setting the notification bit to true, to enable notifications from this characteristic.
    _Screenshot of Wireshark Write Request packet to CCCD (handle 0x0013) with value enabling notifications._

    7.4 Inspect the notifications when the button is pressed and when it’s released.
    You may notice many consecutive “Rcvd Handle Value Notification” packets from the ATT layer in the capture log.
    _Screenshot of Wireshark showing multiple Handle Value Notification packets for button state changes._
    The handle of the notification value attribute is `0x0012`. It’s very common in the attribute table that the value attribute is located right above the CCCD attribute `0x0013`. Also notice that the value of the characteristic when the button is pressed is `0x01` and when the button is released is `0x00`. This is how the app on the phone detects whether to display “Button Pressed” or “Button Released”.

This marks the end of this exercise. You should be able to start using the sniffer to inspect other exercises. For example, the screenshot below is from the capture log of Lesson 4 Exercise 3, where we use NUS service to send UART data from the computer to the phone. In this case, we have typed “Nordic Academy” into a serial terminal and can now see the notification that contains this data being sent to the phone:
_Screenshot of Wireshark showing a NUS notification packet containing the string "Nordic Academy"._

## Exercise 3: Follow and decrypt a paired connection

_(Note: The exercise text might have variations for different nRF Connect SDK versions: v3.0.0, v2.9.0 – v2.7.0, v2.6.2 – v2.3.0. The following is based on the provided common text.)_

It can be tricky to follow an encrypted connection, especially when LE Secure Connections is used. Even with Just Works pairing, it’s not possible for the sniffer to automatically decrypt the encrypted connection without a security key provided.
This exercise can be used in supplement to Exercise 1 Lesson 5 Security. If you haven’t completed the security exercise, you can use the provided solution. The solution is available at `l5/l5_e1_sol`.

### Exercise steps

In the GitHub repository for this course, go to the code for this exercise, found in `l6/l6_e3`.
Note that this is the same firmware as the solution to exercise 1 found in `l5/l5_e1_sol`.

1.  **Build and flash the application on your board.**
    LED1 on your board should be blinking, indicating that your board is advertising.

2.  **View the log output from the application.**
    Open up a terminal window to see the log output from the application.

3.  **Filter only the device packets from Nordic_LBS.**
    Close and re-open Wireshark and run the sniffer again. Go to the Device drop-down list to select `Nordic_LBS` (or `Nordic_Peripheral` if the name changed), just like we have done in the previous exercises.

4.  **Connect to the device using your phone.**
    Using the nRF Connect for Mobile application, connect to the device `Nordic_LBS`. Make sure that you can follow the connection with the sniffer.
    Observe in the sniffer, that the connection is established (`CONNECT_IND`). You may want to use the Empty packet filter again to make it easier to follow.

5.  **Trigger bonding by doing a write command to change the LED state.**
    Just like we did in lesson 5, try writing a value to change the LED state, and you will be prompted to write in a 6-digit passkey that is printed in the UART log, like this.
    `Passkey for 4B:DA:4C:3B:E4:E0 (random): xxxxxx`
    When this is complete, you should see the following in the sniffer, look for the three packets highlighted below:
    _Screenshot of Wireshark showing sequence: Sent Write Request, Rcvd Error Response (Insufficient Authentication), Sent Pairing Request._
    *   `Sent Write Request`: The Write Request gets sent when we tried to write to the LED characteristic from the central (your phone).
    *   `Rcvd Error Respond`: The Write Request gets rejected with Insufficient Authentication, because the connection is still open, and not encrypted, at security level 1. Recall from Exercise 1 in Lesson 5, that the requirement for accessing the LED characteristic is at security level 3.
    *   `Sent Pairing Request`: After receiving the rejection, the phone will send a Pairing Request to start the process of upgrading security level of the connection.

    Continue with the pairing process in the sniffer trace, you will see the key is generated and the link is encrypted after the `LL_START_ENC_REQ` packet.
    _Screenshot of Wireshark showing LL_START_ENC_REQ followed by encrypted packets marked "Encrypted packet decrypted incorrectly"._
    Notice that `LL_START_ENC_REQ` is the last packet where the communication is not encrypted. After this packet, the sniffer is not able to decrypt the communication and all the messages from there on out are marked as “Encrypted packet decrypted incorrectly”. Shortly after this, the sniffer won’t able to capture any more encrypted messages. This is because when the sniffer can’t decrypt the communication, it won’t be able to follow the change of timing or channel hopping of the connection.

6.  **Enable Bluetooth LE log information for sniffer.**
    To be able to decrypt the communication, we need to provide the sniffer with the LTK from the connection. The Kconfig symbol `BT_LOG_SNIFFER_INFO` will log the LTK of the connection after pairing so we can provide this key to the sniffer.
    Add the following Kconfig symbols in the `prj.conf` file of the application:
    ```kconfig
    CONFIG_BT_LOG_SNIFFER_INFO=y
    ```

7.  **Build and flash the application on the board.**
    7.1 Make sure you select Erase And Flash To Board, to remove the previous bonding information.
    _Screenshot of IDE option "Erase And Flash To Board"._
    7.2 Remove the bond information from your phone.
    On the phone, you would need to remove the bond information of the device as well.
    _Screenshot of Android Bluetooth settings showing "Unpair" option._

8.  **Perform the same pairing process as we did in step 5.**
    Connect to the device in nRF Connect for Mobile and try to write a value to the LED characteristic to be prompted with the Pairing Request.
    Input the 6-digit passkey and notice in the UART log, that there is an extra line printed, containing the LTK:
    ```
    *** Booting Zephyr OS build v3.2.99-ncs 1 ***
    Starting Bluetooth Peripheral LBS example
    Bluetooth initialized
    Advertising successfully started
    Connected
    Passkey for 40:A1:08:FF:EF:95 (random):947467
    Security changed 40:A1:08:FF:EF:95 (random) level 4
    I: SC LTK: 0xe58c6433d0b6fa31cc5593483878ad536
    ```

9.  **Provide the sniffer with the outputted LTK, to decrypt the connection.**
    Back in the sniffer, in the header above the Packet List window, under Key, select `SC LTK` and then copy the LTK from the log output into the `Value` section. Click the small arrow to the right of the `Value` section to apply the changes.
    _Screenshot of nRF Sniffer toolbar in Wireshark, showing Key selection (SC LTK) and Value input field for the LTK._
    > **Note**
    > The LTK is randomly generated after each pairing, so you will have your own LTK that you need to copy and paste into the nRF Sniffer. The example LTK provided here will not work for your connection.

10. **Disconnect and re-connect the device from the phone.**
    In nRF Connect for Mobile, disconnect the device to the phone and then connect to it again. This time the LTK generated in the last connection will be re-used and the phone and the device will automatically re-encrypt the link. The sniffer will use the provided key to decrypt the link.
    To confirm this, open a random packet, expand `nRF Sniffer for Bluetooth LE` and then `Flags` and note that the `Encrypted` flag is set.
    _Screenshot of Wireshark Packet Details showing nRF Sniffer flags with Encrypted set to Yes._
    Observe that there is no new Pairing Request and the central only sends `LL_ENC_REQ` to start re-encrypting the link. After the `LL_START_ENC_REQ` packet the link is encrypted, but this time the sniffer is able to decrypt the link and the `Encrypted Flag` is now changed to `Yes` after the `LL_START_ENC_REQ`.
    Try to send an LED write request from the phone, and it will be observed by the sniffer trace, as shown above.
    If your phone doesn’t support LE Secure Connection and only supports Legacy Pairing, you will need to select `Legacy LTK` instead of `SC LTK` in the Key dropdown menu.