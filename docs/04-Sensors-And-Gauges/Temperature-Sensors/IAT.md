# Intake Air Temperature

Intake air temperature (`IAT`) supplies the intake-air temperature used by the airmass model and available fuel and ignition corrections. Fit it where the selected airmass strategy expects the measurement; a post-heat-soak location can read hotter than the air reaching the cylinders.

## Configuration and calibration

Open **Sensors > IAT sensor**. Assign **Input channel** and **Pullup resistor**, then enter three ascending temperatures and the corresponding sensor resistances ([IAT dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3602)). The **Common IAT Sensors** selector offers GM, Miata, and Bosch presets, but the installed sensor and its data must match the preset.

Use the sensor manufacturer's NTC table to populate the three points. Enable **Linear characteristic** only when the supplied characteristic is intended to be linear and the first two points adequately describe it. Set the bias resistance from the board's input circuit, and use **IAT sensor is pulldown instead of pullup** only when the hardware requires that inversion. Verify **Intake air temp** against ambient before starting and observe **Raw IAT** while wiggle-testing the harness.

## Wiring and diagnostics

Use a board-supported analog temperature input, sensor ground, and documented bias supply. The [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) identifies its analog-temperature pins; pin locations and bias circuits are revision-specific. Follow the IAT datasheet for installation depth, thread/seal requirements, and acceptable environment.

Sensor Checker maps IAT timeout, low, and high faults to P0110, P0112, and P0113 ([diagnostic mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L128)). A failed sensor also removes valid IAT-based correction and airmass input, so inspect the DTC and raw value rather than masking the effect in unrelated correction tables.

The IAT path feeds the charge-air calculation and the optional [IAT fuel multiplier](/Fuel/Fuel-Settings/IAT_Multiplier/) and [IAT ignition correction](/Ignition/Ignition-Settings/IAT-Ignition-Adder/). Correct the sensor before tuning either table.

## Sources

- [IAT sensor dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3602)
- [Thermistor configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_thermistors.cpp#L101)
- [IAT diagnostic mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L128)
- [Airmass IAT input](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L534)
