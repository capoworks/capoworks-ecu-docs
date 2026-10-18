# Electronic Throttle Settings

## Enable and disable

In **Electronic throttle body**, assign each throttle to an H-bridge with **H-Bridge #1 function** or **H-Bridge #2 function**. `Throttle 1` and `Throttle 2` enable both position controllers; `None` disables a slot. After Burn, the configuration-change handler calls `doInitElectronicThrottle()` to rebuild the ETB/DC-motor bindings from the current function, frequency, and two-wire settings; a power cycle is not required solely by this path. Reinitialization stops old bindings, so make changes with actuator output safe. A configured pedal without a throttle raises a firmware error.

**Disable ETB if engine is stopped** stops control when the trigger reports no recent engine movement. **Disable ETB Motor** inhibits output for sensor and wiring checks; it does not replace vehicle safety precautions. Invalid feedback, configuration failure, rev limiting, or jam protection can also prevent output.

See [ETB idle control](/Advanced-Features/ETB/ETB-Idle) and [ETB PID and autotune](/Advanced-Features/ETB/ETB-PID).

## Hardware assignment

Use only pin and H-bridge assignments documented for the exact Capoworks board target and revision. The ETB panel names direction, control, and disable pins, but does not make a pin suitable for a motor load. Routing, output mode, polarity, and available bridges are board-specific.

**Two-wire mode** must match the bridge. Enabled: PWM on both direction pins, with **Control** as enable. Disabled: PWM on **Control**, with direction pins selecting polarity. Frequency has a 100 Hz floor and board-defined ceiling; unsupported values raise a firmware error. Use board/bridge documentation and verify direction/disable before motion.

## Sensors and calibration

Assign primary and secondary throttle-body inputs under **Sensors > Throttle Body #1/#2**, and both pedal inputs under **Sensors > Accelerator pedal**. ETB initialization requires a configured primary TPS, redundant TPS, and redundant pedal signal. Operation needs valid calibration. `allowIdenticalPps` is passed only to the accelerator-pedal pair; throttle TPS pairs have no identical-calibration bypass. The identical-pedal exception therefore does not apply to a throttle-body TPS pair. See [ETB redundancy](/Advanced-Features/ETB/Redundant-Sensors).

Calibrate the pedal with **Grab Up** released and **Grab Down** at full travel. **Auto Calibrate ETB** requires a configured throttle and no other calibration. Stopped, it drives open for one second, captures both TPS channels, drives closed for one second, and captures again. It stops without writing if primary TPS moves less than 0.5 V. Burn accepted values, then verify raw voltages, pedal and throttle percentages, target, error, and duty.

## Sources

- [H-bridge fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3843-L3858)
- [Configuration reinitialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L283-L291)
- [TPS and pedal pair validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_tps.cpp#L184-L226)
- [TPS autocal](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L821-L923)
