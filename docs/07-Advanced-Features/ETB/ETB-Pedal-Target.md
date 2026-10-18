# ETB pedal target mapping

The electronic throttle target is not a copy of throttle-body TPS. Capoworks converts accelerator-pedal demand through the **ETB Pedal to TPS** table, whose axes are engine RPM and pedal position. The selected strategy, trim, rev limit, and position limits then modify that value before the ETB position PID attempts to match physical TPS.

## Normal target path

Without the torque model, Capoworks interpolates the table value into an idle-shifted range. The lower endpoint is `ETB idle maximum angle × idle position / 100`; the upper endpoint remains 100%. This compresses the pedal range rather than adding one fixed percentage everywhere. A short-lived Lua adjustment and an active anti-lag addition can then change the target. A 0% table result therefore does not prove that the plate should be physically closed.

With the torque model enabled, the table value becomes the maximum permitted throttle instead. The final value is the lower of the torque-model throttle request and that pedal-derived cap. This path does not apply the non-torque idle remapping, Lua target adjustment, or anti-lag target addition. Validate torque-model idle behavior independently.

Both paths apply throttle trim, limiting throttle #2 trim to plus or minus 10%, clamp the result to 0-100%, taper it toward zero across the ETB RPM-limit range, then clamp it between **Minimum ETB position** and **Maximum ETB position**. Full rev limiting therefore stops at the configured minimum position, not necessarily an arbitrary physical stop.

An invalid pedal reading is sanitized to 0% demand, but idle/minimum-position, trim, Lua, anti-lag, or torque-model logic can still produce a nonzero target. ETB initialization rejects a configuration without a configured primary TPS, redundant TPS, or redundant accelerator pedal.

Log **Target: Base**, **Target: Trim**, **Target**, physical throttle position, and **ETB: position error**. If target and physical TPS diverge, check calibration and motor control before changing the table. See [ETB settings](/Advanced-Features/ETB/ETB-settings), [ETB redundancy](/Advanced-Features/ETB/Redundant-Sensors), and [ETB idle control](/Advanced-Features/ETB/ETB-Idle).

## Sources

- [ETB pedal table axes and TunerStudio panel](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L1385-L1389)
- [Pedal-to-target path and downstream limits](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L337-L385)
- [Non-torque idle remapping, Lua and anti-lag additions](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L388-L414)
- [Required redundant TPS and pedal sensors](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L172-L203)
