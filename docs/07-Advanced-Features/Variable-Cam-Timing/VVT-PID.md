# VVT PID Control

Capoworks VVT control combines a temperature-indexed hold-duty curve with a position PID. There is no separate closed-loop enable: when the target and measured angle are valid, the controller computes the PID result, adds the hold curve, compensates duty for battery voltage, and applies the final output limits.

For error `e = target - measured angle`, the PID path is:

`pTerm = P factor x e`

`iTerm += I factor x dt x e`

`dTerm = D factor x (e - previousError) / dt`

`PID output = clamp(pTerm + iTerm + dTerm + Hold duty, PID min, PID max)`

The control-direction setting changes the error sign. The **Hold duty** PID field is a constant feed-forward term. The **VVT intake hold duty** and **VVT exhaust hold duty** curves add another feed-forward value indexed by oil temperature when available, otherwise coolant temperature, with 80 C used if neither sensor is valid.

## Limits and failure behavior

**Iterm min/max** constrain only the integral term, in addition to the shared hard integral limit. **PID min/max** clamp the complete PID result before the hold curve is added. **Output min/max** clamp final duty after battery compensation. The PWM output range is 0-100%, and output frequency is configured in the VVT configuration dialog.

With P, I and D factors set to zero, the controller behaves as a feed-forward path using the configured hold-duty terms, but it still requires a valid target and measured angle. This is not a separate selectable open-loop mode. Missing or stale cam feedback, an invalid target-axis source, a failed activation gate, or a target at the mechanical rest region produces zero output and resets the PID.

## Setup and diagnosis

First verify decoder synchronization, VVT-offset calibration and control direction. Use **VVT Testing** to apply the target bump temporarily for two seconds, then log position, target, output, P/I/D terms, error, RPM, load source, coolant, oil temperature and battery voltage. Adjust feed-forward until the actuator responds predictably, then tune gains for the observed hardware; do not copy universal PID values from another engine.

Large output with no position change indicates a mechanical, hydraulic, wiring, decoder or direction problem before it indicates a gain problem. See [On/Off VVT control](/Advanced-Features/Variable-Cam-Timing/On-Off-VVT) and [VVT target tables](/Advanced-Features/Variable-Cam-Timing/VVT-Target-Tables).

## Sources

- [PID and integral-limit initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L26-L63)
- [Hold curve, PID direction and output](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L136-L193)
- [PID calculation and clamping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/util/math/efi_pid.cpp#L41-L82)
- [VVT PID fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4257-L4279)
