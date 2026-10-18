# Flex Fuel

Capoworks reads a Continental/GM-style flex sensor through `flexSensorPin`.
Configure it under **Sensors > Flex fuel sensor** using an input suitable for a
frequency signal; a slow switch input is not appropriate.

The two edges of each sensor pulse carry different information. On the falling
edge, firmware measures frequency and publishes `FuelEthanolPercent`. The current
converter targets the 50-150 Hz sensor range, reports low below 45 Hz and high
above 155 Hz, converts accepted frequency to ethanol percentage with a low-pass
filter, and preloads that filter from the last valid percentage stored in backup
RAM. On the rising edge, pulse width is measured as fuel temperature: 1000 us represents
-40 C and 5000 us represents 125 C, with values outside roughly 900-5100 us
reported as invalid. If an analog fuel-temperature channel is configured, it is
used instead of the flex sensor's temperature output.

The enabled correction is intentionally limited. `stoichRatioPrimary` applies at
E0 and `stoichRatioSecondary` at E100; the active stoichiometric ratio is
interpolated between them. `flexCranking` optionally blends the normal cranking
coolant multiplier with `crankingFuelCoefE100`. When the sensor is invalid, the
ECU uses the last valid percentage from backup RAM, then
`flexFuelFailedEthanol` if no valid value has ever been stored.

This is not automatic calibration of every fuel or ignition map. VE, lambda
targets, ignition, and other tables do not gain a complete E0-to-E100 calibration
from enabling the sensor. If ethanol-dependent changes are required, configure
them explicitly, for example as a blend axis in
[Multi-Dimensional Mapping](/Advanced-Features/Multi-Dimensional-Mapping) or in
an output-control table using **Ethanol (Flex) %**. Those are user-defined
corrections, not an automatic tune.

Verify **Flex Ethanol %** and fuel temperature after installation. Missing or
out-of-range frequency can raise the configured P0176, P0178, or P0179 diagnostic;
use that code plus the live percentage to separate wiring, frequency, and
contamination problems.

## Source references

- [Flex-sensor registration and pulse-width temperature decoding](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_flex.cpp#L10-L72)
- [Frequency-to-ethanol conversion and filtering](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/converters/flex_sensor.h#L18-L37)
- [Stoichiometric interpolation and fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/fuel_computer.cpp#L25-L118)
- [Current flex controls and labels](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3395-L3400)
