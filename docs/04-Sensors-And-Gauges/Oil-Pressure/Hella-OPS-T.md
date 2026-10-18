# Hella OPS+T oil pressure and temperature sensor

Capoworks ECU supports the Hella OPS+T combined digital oil pressure and temperature sensor, part number `6PR 010 378-207`. One digital input provides both oil pressure and oil temperature.

## Wiring

The sensor transmits a repeating three-symbol pulse-width frame on one digital line. The input must be assigned to a pin that supports EXTI edge capture. Follow the Hella datasheet for the electrical connection, supply voltage, connector pinout, and any required input protection.

## Configuration

In TunerStudio, open **Sensors > Oil pressure** and assign **Hella OPS+T input** to the connected digital input pin. Leaving the pin unassigned disables the driver.

The driver registers the standard oil pressure and oil temperature channels only when those channels do not already have providers. This allows mixed configurations and prevents OPS+T from replacing an existing analog or digital sensor. If both channels already have providers, the driver does not claim the input.

## Behavior

- Oil pressure is reported as gauge pressure: the current barometric pressure is subtracted and the result is clamped to zero. If baro is unavailable, 101.325 kPa is used.
- Both channels time out after 500 ms without a valid frame.
- The sensor's diagnosis symbol can report pressure, temperature, or sensor-hardware faults. Inconsistent readings are reported through the standard oil pressure and oil temperature DTCs.

## Validation status

The decoder, diagnostics, timeout, resynchronization, baro conversion, and provider priority are covered by unit tests, and the firmware compiles with the driver enabled. Validation on the physical sensor and a running engine is still required before the implementation should be considered production-tested.
