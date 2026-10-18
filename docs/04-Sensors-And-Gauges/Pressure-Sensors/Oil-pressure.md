# Oil Pressure Sensors

Oil pressure can come from an analog pressure sensor or from a digital pressure switch. Open **Sensors > Oil pressure** for the analog input and low/high voltage-pressure endpoints ([oil-pressure dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3635)). The analog sensor is registered with a 50 ms timeout. A switch is instead assigned under **Base Engine > Limits and protection > Oil pressure protection**, where **Oil pressure source** selects switch or sensor operation.

The [Hella OPS+T](/Sensors-And-Gauges/Oil-Pressure/Hella-OPS-T/) is also supported through one EXTI-capable digital input. It reports both pressure and temperature and takes priority only for channels that do not already have another provider.

## Calibration

For an analog sensor, enter the datasheet or bench-verified voltages and pressures. Keep the higher pressure value on the higher-voltage endpoint when the sensor's transfer is non-inverted. Watch **Raw Oil Pressure** and **Oil pressure** and confirm the scaled gauge while the engine has both cold and warm oil pressure. Do not invent a minimum-pressure curve from a generic engine; establish it from the specific engine's valid pressure data.

For a switch, verify its normal state with the engine stopped and with verified oil pressure. Configure pull mode and polarity for the installed switch and board input. The switch path is debounced in the same Sensor Checker initialization ([switch debounce](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/allsensors.cpp#L21)).

## Protection and diagnostics

The minimum-after-start check uses a fixed five-second observation window. Low-pressure protection uses an RPM threshold curve, a start delay, and an accumulation timeout before fuel is cut ([protection logic](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/limp_manager.cpp#L159)). With sensor mode, the RPM-curve low-pressure branch treats an invalid or missing reading as sufficient after its start delay while reporting the sensor fault separately. Do not assume a sensor fault will cut fuel. Restore a valid input by repairing the sensor supply, wiring, connector, ADC channel, and calibration; changing tune values does not alter this branch's fail-open behavior.

Analog oil pressure maps timeout/inconsistent faults to P0521, low to P0522, and high to P0523 ([DTC mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L152)). Wiring and input conditioning must follow the sensor and exact board revision; do not reuse an analog pin from another board.

## Sources

- [Oil-pressure sensor dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3635)
- [Linear and switch initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L61)
- [Oil-pressure protection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/limp_manager.cpp#L159)
- [Hella OPS+T decoder](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/hella_opst.cpp#L24)
