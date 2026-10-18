# Turbo Speed Sensors

Turbo speed is implemented in the pinned build as a generic frequency sensor, not a fixed CAN decoder. Choose a board-supported event input under **Other Sensor Inputs > Turbo Speed Sensor** and enter **Turbo Speed Multiplier**. The input is timed on falling edges; no edges for the sensor timeout period leaves it unavailable.

The conversion is explicit: measured frequency × multiplier × 60 = RPM. If the sensor produces one pulse per turbocharger revolution, the multiplier is 1. For ten pulses per revolution it is 0.1; for two pulses, 0.5. Confirm pulse count from the sensor documentation. Do not tune the multiplier by matching an assumed boost level.

On a bench, feed a known frequency and verify the displayed result against that formula before running the turbocharger. Then compare a low-speed known reference if the installation safely permits it. Verify the input uses the correct edge and conditioning for the sensor; changing the multiplier cannot cure dropped or double-triggered edges.

Two presentation limits matter. The published turbo speed channel metadata still labels the value `hz`, although the converter returns RPM, and `turboSpeed` is an unscaled 16-bit field. Values above 65535 cannot be represented faithfully, so do not treat the generic gauge as a full-range tachometer. There is no separate high-range scaling or limiter UI. The `turboSpeed` output is populated from `SensorType::TurbochargerSpeed`; because the multiplier is applied before that shared sensor value, changing it to fit the 16-bit channel affects every consumer, not only the gauge or logger. Do not use that as a workaround when actual RPM is required. Board input choices remain target-specific: Core8 advertises VR/Hall and digital event inputs, not every MCU pin.

## Sources

- [Turbo frequency sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_turbocharger_speed_sensor.cpp#L11)
- [Frequency-to-RPM conversion](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/converters/turbocharger_speed_converter.h#L7)
- [16-bit turbo output channel](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/binary/output_channels.txt#L234)
- [Turbo speed status assignment](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/status_loop.cpp#L521)
- [Core8 target event-input names](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/generated/fome_core8.ini#L89)
