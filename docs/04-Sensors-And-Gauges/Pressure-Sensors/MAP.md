# Manifold Absolute Pressure

MAP is the absolute pressure in the intake manifold and is the primary load input for Speed Density. It must be referenced to the correct intake location specified for the engine; an atmospheric reference or boost-only sensor is not a substitute.

## Configuration

Open **Sensors > MAP sensor**. Assign **MAP ADC input** and an optional **MAP 2 ADC input**, select **MAP type**, and enter the endpoints for a custom sensor ([MAP dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3716)). Known presets include common GM, Mazda, Bosch, Denso, Honda, and other pressure sensors. The second MAP input uses the configured MAP conversion and is intended as a second measured-pressure channel, not as an independent sensor-type selector ([initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_map.cpp#L97)).

For a custom sensor, use its datasheet's pressure-versus-voltage characteristic. Verify **Raw MAP** against the sensor transfer curve, then verify **MAP** at key-on with the engine stopped, under idle vacuum, and under load. Calibration must also account for the board's analog input divider as documented for that hardware.

## Sampling and behavior

The `Map` value is selected from `MapFast` and `MapSlow`: the firmware prefers a valid fast sample when MAP averaging is enabled, otherwise it uses the continuously sampled slow value. The fast and slow values are not combined. Set the sampling angle and window on the [MAP Sampling Angle](/Advanced-Features/MAP-Sampling-Angle/) page. The low/high validity thresholds are configured on this page and generate P0106, P0107, or P0108 through the Sensor Checker ([diagnostic mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L91)).

MAP feeds Speed Density airmass, boost control, DFCO, wall-wetting, and other load consumers. The current airmass system can use the configured MAP estimate when the measured value is unavailable, but an estimate is not a measured sensor and must not be used to diagnose a MAP circuit fault.

## Wiring

Wire the sensor signal to a board-supported analog-voltage input and use the supply, ground, and sensor circuit specified by the sensor and board. A Universal 112 v1.2 exposes generic analog inputs rather than a mandatory MAP pin; locate the chosen `AV` input in its [revision-specific pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/). Connect pressure only through the sensor's documented pressure port.

## Sources

- [MAP sensor dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3716)
- [MAP conversion and registration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_map.cpp#L97)
- [MAP DTC mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L91)
- [MAP diagnostic thresholds](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1007)
