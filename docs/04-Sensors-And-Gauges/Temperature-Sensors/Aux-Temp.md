# Auxiliary Temperature Inputs

The ECU has two generic temperature inputs, `AuxTemp1` and `AuxTemp2`. They use the same three-point thermistor model as CLT and IAT but have no linear or pull-down option in this revision. Open **Sensors > AuxTemp1 sensor** or **AuxTemp2 sensor**, assign an analog temperature input, set the board bias resistance, and enter three temperature/resistance pairs ([aux-temperature dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3185)).

## Calibration

Use the sensor manufacturer's NTC table. The temperatures must be in ascending order. Choose points that span the temperatures you need to measure rather than placing all three around one operating point. Verify the bias resistor against the exact board schematic, then compare the gauge with a known ambient or reference temperature. A correct thermistor curve with the wrong bias will produce a plausible but offset reading.

The NTC inputs were designed for a board-supported temperature input with a pull-up. On the Universal 112 v1.2 the documented analog-temperature inputs use a board pull-up; verify the [v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) and schematic instead of applying that detail to another revision. Follow the sensor datasheet for its electrical connection and isolation requirements.

## Use and diagnostics

The processed channels appear as **Aux temp 1** and **Aux temp 2** in logs and can be selected as General Purpose PWM load axes. CAN dash formats also carry them. They are not automatic engine-protection inputs, so assigning an oil or transmission temperature here does not create a protection strategy by itself.

There is no Aux Temp entry in this revision's normal Sensor Checker DTC list ([checked temperature inputs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L620)). Diagnose from the gauge/log, input channel, bias value, and raw ADC behavior. Open-circuit and short-circuit behavior can produce an implausible temperature, but do not infer one universal voltage threshold from the displayed value.

## Sources

- [Aux-temperature dialogs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3185)
- [Thermistor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_thermistors.cpp#L71)
- [Thermistor conversion](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/converters/thermistor_func.cpp#L42)
- [Aux-temperature output channels](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/binary/output_channels.txt#L41)
