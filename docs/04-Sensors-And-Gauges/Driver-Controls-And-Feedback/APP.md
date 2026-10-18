# Accelerator Pedal

The accelerator pedal position sensor (PPS or APP) measures driver demand for an electronic throttle. It is separate from the throttle position sensor on the throttle body. Electronic-throttle initialization requires the combined accelerator-pedal sensor to be redundant; if it is not, the throttle controller reports a configuration error instead of enabling normal ETB control ([electronic throttle initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L196)).

## Configuration and calibration

Open **Sensors > Accelerator pedal**. Assign both analog inputs with **Primary Sensor** and **Secondary Sensor**, then enter each sensor's released and fully pressed voltages ([pedal dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3302)). To calibrate with the pedal installed and the sensors powered, leave the pedal released and select **Grab Up**. Fully depress it and select **Grab Down**. Each command captures the raw value of both channels ([calibration handler](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/tps.cpp#L18)).

Use a second, electrically independent pedal track for redundancy. Normal configuration rejects two inputs whose calibrations are nearly identical. Enable **BRZ/FRS/GT86 pedal** only for a known platform that uses an intentionally identical secondary characteristic ([pair validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_tps.cpp#L108)).

## Diagnostics and wiring

Check **Pedal position**, **Raw Pedal Primary**, **Raw Pedal Secondary**, **Pedal error**, and the pedal error counter. The firmware reports timeout, low, high, and correlation faults such as P2137. A failed combined pedal is sanitized to a 0% demand, but the resulting throttle target still follows the configured control logic, including idle/Lua adjustments, trims, minimum-position limits, and other overrides; 0% demand does not guarantee a fully closed throttle ([setpoint handling](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L337)).

Both tracks need board-supported analog inputs plus the sensor supply and ground specified by the pedal manufacturer. Pin locations and input circuits vary by board revision; use the [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) only when that is your actual hardware.

## Sources

- [Accelerator pedal dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3302)
- [PPS pair initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_tps.cpp#L168)
- [PPS calibration capture](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/tps.cpp#L18)
- [PPS diagnostic mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L63)
