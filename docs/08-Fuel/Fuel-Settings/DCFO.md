# Deceleration Fuel Cutoff (DFCO)

DFCO removes fuel while the throttle is closed and the vehicle is coasting. It is
a hysteresis state machine, not a simple RPM cut. Enable it with
`coastingFuelCutEnabled` under **Fuel > Deceleration fuel cutoff (DFCO)**.

DFCO can start only while the engine is running. The driver-throttle value must
be below `coastingFuelCutTps`, coolant must be above `coastingFuelCutClt`, and a
configured MAP sensor must read below `coastingFuelCutMap` or its RPM-dependent
threshold when `useTableForDfcoMap` is enabled. Missing TPS or CLT data blocks
DFCO; MAP is optional, but a configured MAP sensor with an invalid reading also
blocks it.

RPM and vehicle speed use separate entry and exit thresholds. RPM above
`coastingFuelCutRpmHigh` can enter the state, RPM below
`coastingFuelCutRpmLow` exits it, and values between the two hold the previous
state. Vehicle speed follows the same pattern with `coastingFuelCutVssHigh` and
`coastingFuelCutVssLow`; setting either speed field to zero disables the speed
check.

When `disableFuelCutOnClutch` is enabled, a valid `clutchUpPin` reading clutch-up
is required. A pin that is not configured does not block DFCO. After the state is
eligible, `dfcoDelay` postpones the cut. Fuel is restored when the state exits,
so do not expect one universal RPM recovery point. While the DFCO state is
active, `dfcoRetardDeg` is applied as timing retard; because `dfcoDelay` can
postpone fuel removal, retard can begin before the injectors stop. It ramps out
over `dfcoRetardRampInTime` after fuel returns. `noFuelTrimAfterDfcoTime` keeps
closed-loop fuel correction paused during that recovery period.

Use the `dfcoActive` channel to confirm cut state and `fuelCutReason` to check
whether the fuel cut came from DFCO or another limiter. Log throttle intent,
MAP, RPM, speed, coolant, clutch state, and `dfcoActive` together when diagnosing
entry or recovery problems.

## Source references

- [DFCO entry gates and hysteresis](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/dfco.cpp#L9-L73)
- [Cut delay, timing retard, and recovery](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/dfco.cpp#L76-L118)
- [Configuration fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L703-L711)
- [TunerStudio labels](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L5088-L5104)
