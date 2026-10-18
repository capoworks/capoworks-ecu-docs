# Hella OPS+T oil pressure and temperature sensor

Capoworks ECU supports the Hella OPS+T combined digital oil pressure and temperature sensor, part number `6PR 010 378-207`. One digital input provides both oil pressure and oil temperature.

## Wiring

The sensor transmits a repeating three-symbol pulse-width frame on one digital line. The input must be assigned to a pin that supports EXTI edge capture. Follow the Hella datasheet for the electrical connection, supply voltage, connector pinout, and any required input protection.

## Configuration

In TunerStudio, open **Sensors > Oil pressure** and assign **Hella OPS+T input** to the connected digital input pin. Leaving the pin unassigned disables the driver.

The driver evaluates the standard oil pressure and oil temperature channels independently. It registers each channel only when that channel has no existing provider, and any existing analog or digital provider retains its channel. If one channel already has a provider, OPS+T claims only the other channel; if both already have providers, it claims neither.

## Behavior

- Oil pressure is reported as gauge pressure: the current barometric pressure is subtracted and the result is clamped to zero. If baro is unavailable, 101.325 kPa is used.
- Both channels owned by the OPS+T driver time out after 500 ms without a valid frame. Faults and timeouts from OPS+T affect only those owned channels; a channel owned by another provider is unaffected.
- The sensor's diagnosis symbol can report pressure, temperature, or sensor-hardware faults. A pressure diagnosis affects the pressure channel, a temperature diagnosis affects the temperature channel, and a hardware diagnosis affects both owned channels. Where supported, the corresponding standard DTC is P0521 for oil pressure or P0196 for oil temperature.

## Validation status

The decoder, diagnostics, timeout, resynchronization, baro conversion, and provider priority are covered by unit tests, and the firmware compiles with the driver enabled. Validation on the physical sensor and a running engine is still required before the implementation should be considered production-tested.
