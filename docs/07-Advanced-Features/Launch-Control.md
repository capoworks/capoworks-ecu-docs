# Launch Control

Launch Control is a driver-engaged secondary RPM limit with optional ignition
retard and a fuel-enrichment setting. It is separate from the hard RPM limit under
**Limits and Protections**. Open **Racing Features > Launch Control** to set
the activation source, RPM, timing, and cut behavior.

## Activation and admission

`launchActivationMode` selects **Launch Button**, **Clutch Down Switch**, or
**Always Active(Disabled By Speed)**. For the two input modes, configure the
corresponding pin and inversion and confirm it changes state.

While launch control is enabled, the controller requires all four conditions
simultaneously:

- `activateSwitchCondition`
- `rpmCondition`, where `launchRpm < rpm` (strictly above)
- `speedCondition`
- `tpsCondition`, where `launchTpsThreshold < DriverThrottleIntent`

The throttle intent must be valid. The speed threshold is enforced only in
Always Active mode; button and clutch modes return the speed condition as true.
All conditions must remain true for `launchActivateDelay`; any false condition
resets the timer and clears `isLaunchCondition`.

## Retard, enrichment, and cuts

With `enableLaunchRetard`, the launch path replaces the base advance returned
by `getRunningAdvance()`. Without smooth mode it returns `launchTimingRetard`
directly. With `launchSmoothRetard`, that base advance is interpolated from the
normal value at `launchRpm` to `launchTimingRetard` at `launchRpm +
launchTimingRpmRange`. Smoothing applies to timing only.

This is not necessarily the final scheduled spark timing. After the launch
override, `IgnitionState::getAdvance()` adds the enabled dynamic IAT, CLT, idle
PID, and DFCO corrections, and the per-cylinder path adds `ignTrims` to the
result. Treat `launchTimingRetard` as a base timing target, not as the exact
ignition angle finally scheduled at the cylinder.

The launch cut threshold is `launchRpm + hardCutRpmRange`. Above that threshold,
`launchSparkCutEnable` and `launchFuelCutEnable` independently remove the
entire spark or fuel permission. This is a binary hard cut, not a proportional
or random soft cut. The launch-specific cut predicates release when RPM is at
or below the cut threshold, while launch retard remains active while
`isLaunchCondition` is true.

Current source limitation: `launchFuelAdderPercent` does not provide numeric
launch fuel enrichment. `LaunchControlBase::getFuelCoefficient()` is declared
to return `bool`; for the configured nonnegative percentage range, its
`1 + percent / 100` expression converts to `true` (1). Fuel math then
multiplies the correction by that boolean, leaving the fuel correction
unchanged. Do not use this field to tune launch mixture in this source version.

Current source limitation: disabling launch control while it is active does not
guarantee immediate release from launch retard or launch cuts. `update()`
returns early when `launchControlEnabled` is false without clearing
`isLaunchCondition`; the retard and cut predicates check
`isLaunchCondition` and RPM but do not recheck `launchControlEnabled`, and
`LimpManager` consumes those predicates. This conclusion is from code
inspection, not runtime bench validation, so the enabled flag should not be
treated as a guaranteed immediate stop or release control.

## Diagnostics

Use the Launch Control indicators for `combinedConditions`,
`activateSwitchCondition`, `rpmCondition`, `speedCondition`,
`tpsCondition`, and `isLaunchCondition`. `retardThresholdRpm` shows the launch
cut RPM. During a cut, `fuelCutReason` and `sparkCutReason` report launch
control. If nothing engages, verify `launchControlEnabled`, the input pin,
driver throttle intent, activation delay, and the strict RPM/throttle
comparisons. In button or clutch mode, changing `launchSpeedThreshold` will not
disable launch.

These settings do not establish safe RPM, retard, or cut values for an engine.
Verify ignition and driveline behavior on appropriate test equipment.

## Sources

- [Launch activation fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L851)
- [Admission, timer, threshold, and release logic](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/launch_control.cpp#L20)
- [Launch timing override](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/ignition/ignition_state.cpp#L93)
- [Dynamic advance corrections](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/ignition/ignition_state.cpp#L150)
- [Per-cylinder ignition trim addition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine2.cpp#L254)
- [Boolean fuel-coefficient declaration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/launch_control.h#L21)
- [Fuel coefficient and disabled-update behavior](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/launch_control.cpp#L96)
- [Fuel correction consumer](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L156)
- [Fuel and spark cut consumers](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/limp_manager.cpp#L89)
