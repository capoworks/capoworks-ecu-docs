# On/Off VVT Control

Capoworks firmware does not expose a separate binary VVT mode. A configured cam uses a PWM solenoid output and a position controller; commanding the target near its rest position is how control is switched off.

## Configuration and arming

Select the VVT mode that matches the camshaft pattern and identify the cam used for engine sync. Assign only a solenoid output supported by the exact board, then set the VVT PWM frequency and intake/exhaust control direction. TunerStudio marks VVT pin and frequency changes for a power cycle.

Before control, calibrate each VVT offset with the solenoid disabled so the reported angle reads zero at its mechanical reference. Control requires the engine to be running, RPM to be above **Do not control below RPM**, coolant temperature to be above **Do not control below CLT**, and the configured activation delay to elapse. The target then ramps from zero over two seconds.

A target near rest is hysteresis-disabled. With the normal direction, control can enable above 3 degrees and remains enabled down to 1 degree; the inverted direction mirrors those thresholds below -3 and -1 degrees. This protects the control mechanism from continuous travel against its stop.

## Decoder-relative angle

The reported value is the configured VVT offset minus decoded engine phase, then wrapped for the selected cam type. It is decoder-relative, not necessarily absolute valve timing or cam-centerline angle. Most modes wrap to plus or minus 360 degrees; Toyota 3 Tooth and Honda K Intake wrap to plus or minus 180 degrees. Toyota 3 Tooth also rejects measurements outside its decoder range.

Readings are stored only with full engine synchronization and expire after one second without a new measurement. An unsynchronized cam, expired reading, invalid target/load source, failed activation gate, or active control-disabled target forces output to zero and resets PID history.

Use the VVT position, target, output, RPM, load-source, coolant and oil-temperature channels while diagnosing arming. See [VVT target tables](/Advanced-Features/Variable-Cam-Timing/VVT-Target-Tables) and [VVT PID control](/Advanced-Features/Variable-Cam-Timing/VVT-PID).

## Sources

- [VVT arming and validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L37-L64)
- [Target ramp and near-rest disable](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L86-L129)
- [VVT reading timeout](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_central.cpp#L60-L74)
- [Angle calculation and synchronization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_central.cpp#L302-L358)
