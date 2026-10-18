# Barometric Pressure Sensing

Barometric pressure is the actual ambient absolute pressure at the sensor's elevation, not sea-level-corrected weather pressure, manifold boost, or vacuum. This revision supports an external analog barometric sensor and an onboard LPS2x sensor where the board target provides one ([external setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_map.cpp#L137), [onboard setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_baro.cpp#L9)).

Open **Sensors > Baro sensor**. For an analog sensor, assign **Baro ADC input**, choose **Type**, and enter the low/high points. Analog baro uses the same pressure decoder presets and custom linear endpoints as MAP. For a board-supported LPS2x, assign **LPS2x Baro SCL** and **SDA** with the analog channel disabled. The external analog sensor takes priority: onboard initialization is skipped if a barometric provider is already registered.

## Calibration and correction

For an analog sensor, select the exact device preset where available; otherwise enter pressure and voltage endpoints from its datasheet. Compare the barometric reading with a known local absolute-pressure reference, or convert a weather report to station pressure using the local elevation. At key-on with the engine stopped, the reading should be plausible for the location, but do not enter a sea-level-corrected weather value or a universal sea-level value.

**Fuel > Barometric pressure correction** applies a three-dimensional correction by pressure and RPM in Speed Density. Its default table is unity, not a calibration shortcut ([default table](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/defaults/default_fuel.cpp#L87)). Correct the sensor first, then change this table only when the engine model needs a validated elevation correction.

**Use fixed baro corr from MAP** reads the MAP sensor once at initialization and holds it as barometric pressure. An invalid initial value is rejected and generates P2226; the fixed override is then disabled ([startup validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/impl/map.cpp#L24)).

## Diagnostics and wiring

Use the **Baro pressure** log gauge and the MAP/baro raw diagnostic gauges. If baro is absent, fuel barometric correction returns 1, while several injector and actuator calculations use 101.325 kPa as a fallback ([fuel correction](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L825)). There is no generic barometric-pressure value check equivalent to the MAP DTCs in this revision.

The Atlas documents an onboard barometer; the [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) should be used for an external analog input only on that board revision.

## Sources

- [Baro dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3739)
- [Analog baro initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_map.cpp#L137)
- [Onboard LPS2x initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_baro.cpp#L9)
- [Barometric fuel correction](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L825)
