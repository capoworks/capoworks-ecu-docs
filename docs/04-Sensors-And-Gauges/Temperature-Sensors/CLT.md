# Coolant Temperature

Coolant temperature (`CLT`) is used by idle target and correction tables, cranking and warm-up fuel, coolant timing correction, fan control, coolant-based limits, and charge-temperature estimation. A valid calibration therefore affects far more than the temperature gauge.

## Configuration and calibration

Open **Sensors > CLT sensor**. Assign **Input channel** and **Pullup resistor**, then enter **Lowest**, **Middle**, and **Highest temperature** with the corresponding resistances ([CLT dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3569)). A **Common CLT Sensors** selector fills known curves for GM, Miata, and Bosch sensors, but verify that the installed sensor matches the chosen option.

The resistance-to-temperature conversion uses all three calibrated points. Temperatures must be strictly ascending ([validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_thermistors.cpp#L31)). Enable **Linear characteristic** only for a sensor whose resistance-to-temperature relationship is intentionally represented by the first two linear points. Set the pull-up value from the exact board circuit, not from another board revision. **CLT sensor is pulldown instead of pullup** changes the resistance calculation for a board wired that way.

At a cold start and at a known warm operating point, compare **Coolant temp** with a trusted reference. Also watch **Raw CLT** while moving or disturbing the harness to detect intermittent connection.

## Wiring and diagnostics

Connect the two-wire thermistor to a board-supported analog-temperature input, sensor ground, and the documented bias supply. The Universal 112 v1.2 documents four analog temperature inputs and its pull-up arrangement in the [revision-specific pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/); other boards require their own documentation.

Sensor Checker maps CLT timeout, low, and high conditions to P0115, P0117, and P0118 ([DTC mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L116)). Do not treat a failed CLT as a normal warm engine: different consumers have different fallbacks. Correct the input and calibration before tuning dependent tables.

## Sources

- [CLT sensor dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3569)
- [Thermistor configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_thermistors.cpp#L92)
- [Thermistor conversion](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/converters/thermistor_func.cpp#L11)
- [CLT diagnostic mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L116)
