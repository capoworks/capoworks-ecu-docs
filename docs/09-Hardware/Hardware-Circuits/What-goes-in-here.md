# Electrical Interface Overview

The Hardware Circuits pages explain the electrical interface between a
Capoworks ECU board and an engine load. They cover the circuit concept, the
matching Capoworks software controls, and the checks needed before connecting
hardware. They are not universal drop-in schematics: connector pins,
protection, driver capability, and firmware support depend on the installed
board and revision.

Start with the load and its required current path. Decide whether it needs a
high-side, low-side, push-pull, or bridge output, then determine the required
flyback or clamp, supply, switching frequency, and protection. Only then choose
a board-supported output or input and a Capoworks mode. The firmware pin types
distinguish flexible GPIO names from outputs actually routed to a board
function, and output modes change logic polarity or open-drain behaviour rather
than the power stage itself.

The same separation applies to processors. Capoworks selects an F4, F7, or H7
port through a concrete board build; the MCU family alone does not define
connectors or usable peripherals. For every change, confirm the board target,
hardware revision, pinout, schematic, and matching firmware definition.

## Circuit Pages

- [Discrete VR Sensor Inputs](/Hardware/Hardware-Circuits/Discrete-VR)
- [Highside Driver Circuits](/Hardware/Hardware-Circuits/Highsides)
- [Lowside Driver Circuits](/Hardware/Hardware-Circuits/Lowsides)
- [High-Low Driver Circuits](/Hardware/Hardware-Circuits/High-Low)
- [Power Supply and References](/Hardware/Hardware-Circuits/Power-Supply)
- [PT2001 Low-Z Driver](/Hardware/Hardware-Circuits/PT2001)
- [STM32 Compatibility](/Hardware/Hardware-Circuits/STM32-Compatability)

For a matching installation, use the [Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas)
or [Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112)
hardware documentation. Pin locations and protection details from one revision
must not be transferred to another.

## Sources

- [Firmware pin categories and output modes](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L274)
- [Board and CPU selection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/rusefi.mk#L45)
- [Signed DC motor interface](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/system/dc_motor.h#L58)
- [Discrete VR threshold interface](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/vr_pwm.cpp#L13)
