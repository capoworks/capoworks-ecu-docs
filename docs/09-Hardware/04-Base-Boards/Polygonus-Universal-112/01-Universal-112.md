# Universal 112

![alt](./../universal112.webp)

This is the wire-in open-source Universal 112 ECU base board design, compatible with Polygonus and
Atlas ECU brain modules. It uses the Molex 112-pin connector and is intended for custom wiring
harnesses or OEM harnesses where you will cut and replace the original connector.

## Features

### Data and Communication

- USB-B
- Dual CAN bus

### Inputs

- Dual wideband O2 sensor controllers using open source module (connected internally to CAN bus #2)
- Dual VR crank/cam sensor inputs. VR input 2 uses adjustable threshold, suitable for low tooth count (single tooth cam, etc) applications (LS12 unavailable if used)
- 11x Analog voltage Inputs (Weak pulldown to ground to avoid floating)
- 4x Analog Temperature inputs (2.7k pullup resistor to 5v)
- 6 digital inputs with integrated 2.7k pullup resistor to 5v. *Use for hall cam/crank sensors, switches, etc.)

### Outputs

- 2x Electronic Throttle Body H-bridge drivers.
- 20x Lowside outputs (LS1-16), 8 with freewheel diodes (LS9-12 and, optionally, IGN9-12)
- 8 logic level ignition outputs (IGN1-8)
- 8 ignition "dumb coil" IGBT drivers (IGN1-8, shared function with logic outputs, independent output pins)
- Stepper motor driver for stepper idle (LS9/10 outputs unavailable if used)

### Design Source

- [Universal 112 design source - FOME-Tech repository](https://github.com/FOME-Tech/Polygonus-Universal-112)

### Connector 

- [Universal 112 Pinout](../Universal-112-Pinout)
- [Universal 112 Connector Reference](../Universal-112-Connectors)

### Case 

- [Universal 112 Case V1.0 design source by OrchardPerformance - Github](https://github.com/FOME-Tech/Polygonus-Universal-112/tree/main/CAD)
- [FOME Polygonus-Universal-112 Case by MW - Printables](https://www.printables.com/model/1798637-fome-polygonus-universal-112-case)

### Buy

- [🇺🇲 Happy Cactus Garage](https://happycactusgarage.com/products/fome-universal-ecu)
