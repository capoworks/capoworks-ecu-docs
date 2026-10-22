# On/Off VVT control

Capoworks ECU enables VVT control only when several arming conditions are met. When any condition is not met, the VVT output is held at zero duty and the PID integrator is reset so it does not accumulate while control is inhibited.

## Arming conditions

The controller allows output when all of the following are true:

- The engine is running and RPM is above **VVT control minimum RPM**.
- Coolant temperature is above **VVT control minimum CLT**.
- The engine has been running longer than **VVT activation delay**.

The activation delay is compared against the time since engine start. Capoworks ECU preserves fractional millisecond values in this comparison, so the delay you enter is honored rather than truncated. The comparison is strictly greater-than: at exactly the configured delay the output is still inhibited, and control begins just after it.

## Ramp-in

Once arming conditions are satisfied, the target ramps from zero to the table target over two seconds. This avoids an abrupt step in commanded cam angle at the moment control is enabled. The ramp restarts whenever an arming condition drops out, because the time-since-enabled timer is reset while control is inhibited.

## Near-rest disable

If the target is very near the rest position, control is disabled entirely. This avoids integrator windup from pushing the cam against its stop and avoids problems with VVT lock pins jamming. A hysteresis band keeps control from chattering at the threshold. The direction of the band depends on the configured control direction (advance or retard).

## Output limits

When enabled, the commanded duty is compensated for battery voltage, then clamped between **VVT output minimum** and **VVT output maximum** for the cam. When disabled, duty is set to zero.

## Tuning notes

Set the activation delay long enough for oil pressure to build and the cam mechanism to be ready, but short enough that the engine does not run long without intended cam control. Verify arming behavior in a log by watching RPM, coolant temperature, time since start, target, and output together. See [VVT PID control](/Advanced-Features/Variable-Cam-Timing/VVT-PID) and [VVT target tables](/Advanced-Features/Variable-Cam-Timing/VVT-Target-Tables) for the related tuning steps.

## Sources

- [Arming conditions and activation delay comparison](https://github.com/capoworks/capoworks-ecu/blob/776881beac8ecfb148244b1aa4452cd1123952e1/firmware/controllers/actuators/vvt.cpp#L38-L52)
- [Target ramp-in and near-rest hysteresis](https://github.com/capoworks/capoworks-ecu/blob/776881beac8ecfb148244b1aa4452cd1123952e1/firmware/controllers/actuators/vvt.cpp#L86-L129)
- [Output enable gate, voltage compensation and clamping](https://github.com/capoworks/capoworks-ecu/blob/776881beac8ecfb148244b1aa4452cd1123952e1/firmware/controllers/actuators/vvt.cpp#L160-L190)
- [Activation delay unit tests](https://github.com/capoworks/capoworks-ecu/blob/776881beac8ecfb148244b1aa4452cd1123952e1/unit_tests/tests/actuators/test_vvt.cpp#L259-L325)
