# ETB PID and Autotune

The ETB position loop runs at 500 Hz. For target `r` and measured position `y`, error is `e = r - y`:

- `pTerm = pFactor × e`
- `iTerm += iFactor × dt × e`, clamped by `iTermMin`, `iTermMax`, and the shared hard limit based on `pid max`
- `dTerm = dFactor × (e - previousError) / dt`
- Unclamped output is `pTerm + iTerm + dTerm + offset`

First derivative after reset is zero. PID output is clamped by **pid min** and **pid max**; validation requires negative min and positive max. No separate low-pass derivative or output filter exists here. Final duty is the **ETB bias curve** feed-forward plus PID output, limited to plus or minus 90%.

`pid min` and `pid max` limit the complete result; `iTermMin` and `iTermMax` constrain only integral. The shared PID `offset` is added but absent from this dialog. Reset clears integral/derivative history; configuration changes may request reset.

## Using the logs

Use **ETB 1 PID pTerm**, **iTerm**, **dTerm**, **output**, **error**, and **resetCounter**; these channels represent throttle #1. Compare **Target: Base**, **Target: Trim**, **Target**, physical TPS, **ETB: position error**, feed-forward, and **ETB: Duty**. Large duty with little movement indicates motor, wiring, calibration, or jam protection, not automatically gain. No universal gains apply.

## PID autotune

First complete throttle calibration. **Start ETB PID Autotune** is offered with a configured throttle and no active calibration; activation requires zero RPM, throttle #1, and neither ETB-disable option. It does not run on throttle #2. It oscillates around 50% with plus/minus 20% relay output, measuring amplitude and period. It applies relay and Ziegler-Nichols-style factors: `Kp = 0.35 Ku`, `Ki = 0.25 Ku / Tu`, and `Kd = 0.08 Ku Tu`. P, I, and D publish in five-cycle groups through TunerStudio.

Keep the engine stopped. **Stop ETB PID Autotune** clears the request and calibration mode. Blocking flash cancels autotune, clears PID history, and inhibits the motor until fresh valid feedback. Review results, stop, then test before burning gains.

## Sources

- [PID math](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/util/math/efi_pid.cpp#L41-L82)
- [ETB PID and autotune](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L541-L663)
- [Autotune math](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L454-L538)
- [PID fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4830-L4837)
