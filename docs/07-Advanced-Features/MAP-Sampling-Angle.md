# MAP Sampling Angle

MAP angle sampling captures and averages fast pressure samples during a crank-angle window instead of using one arbitrary ADC reading. Enable it in **Sensors > MAP sampling**, then configure the two RPM-indexed curves: **MAP Sampling Start Angle** and **MAP Sampling Duration**. The firmware uses the same conversion as the continuously sampled MAP channel.

## Angle and engine-cycle coordinate

The start curve is evaluated at current RPM in engine-phase coordinates. The firmware adds each cylinder's configured angle offset to that base value and wraps the result into the engine cycle. For each cylinder, the actual schedule is therefore the curve angle plus that cylinder's position offset, not a universal angle for every engine.

The engine cycle is 720 degrees for a four-stroke and 360 degrees for a two-stroke. Therefore the same configured window represents a different fraction of a cycle on each type. The requested duration is clamped to at least 10 degrees and to no more than one cylinder period minus 10 degrees, where cylinder period is engine-cycle angle divided by cylinder count.

When averaging is enabled, the scheduler starts at each computed cylinder angle and samples during the window. **Measure Map Only In One Cylinder** schedules only the first cylinder; otherwise all cylinders are scheduled. The per-window result is the mean of valid converted pressure samples. The fast MAP value then uses the minimum of the most recent requested number of cylinder results.

## Valid samples and fallback

If a window ends without a valid sample, the firmware reports **No MAP values** and does not refresh the averaged fast value. A fast value older than 200 ms becomes invalid. The combined MAP selector prefers a valid fast value and otherwise uses the continuous slow MAP value; it does not blend the two.

This fallback can make the final **MAP** channel appear healthy while fast sampling is failing. Check **MapFast**, **MapSlow** and the averaging-sample count separately when diagnosing. Verify trigger synchronization, cylinder angle offsets, the MAP ADC input, sensor conversion, start angle and window duration.

The firmware does not prescribe a best engine angle. Select the window from logged, repeatable behavior for the specific intake, sensor location, cylinder offsets, RPM and load. See [Manifold Absolute Pressure](/Sensors-And-Gauges/Pressure-Sensors/MAP) for sensor calibration and fault thresholds.

## Sources

- [Sampling angle and window configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L340-L344)
- [Per-cylinder scheduling and duration clamp](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/map_averaging/map_averaging.cpp#L220-L269)
- [Window averaging and minimum buffer](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/map_averaging/map_averaging.cpp#L93-L151)
- [Fast-to-slow MAP fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_map.cpp#L19-L33)
