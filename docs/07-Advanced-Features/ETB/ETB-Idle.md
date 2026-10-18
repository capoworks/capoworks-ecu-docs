# Idle control using ETB

ETB idle control is a cascade. The idle controller determines a position from its open-loop table plus optional closed-loop RPM correction. `applyIACposition()` sends that position to every ETB controller. In the normal non-torque-model path, ETB target logic converts it into a throttle target, then the separate ETB position PID drives the plate until physical TPS matches.

## Which feedback does what

With an accelerator-pedal input configured, `DriverThrottleIntent` comes from the combined pedal sensor instead of TPS. The idle **TPS threshold** therefore tests pedal demand on an ETB car. The idle RPM PID uses target versus engine RPM; throttle-body TPS is not its feedback.

For the normal target path, `ETB idle maximum angle × idle position / 100` becomes the range's low endpoint. Pedal-table demand interpolates from there to 100%, so increasing idle position raises the closed-pedal target without adding the same amount at wide-open pedal. Idle position is clamped to 0-100%. With the torque model enabled, the target is the model request capped by the pedal table; this remap is not applied, so validate idle behavior for the selected strategy.

Open-loop idle position always applies. Closed-loop correction requires **Open Loop + Closed Loop** mode and a valid driver-intent signal; an invalid signal omits correction. Configure RPM targets and general idle behavior in [Advanced Idle Control](/Basic-Features/Idle-Control/Advanced-Idle); this page covers only ETB interaction.

The optional **Idle-only RPM feedback: Rolling cycle** setting replaces instantaneous RPM for closed-loop idle air and timing. It does not change the ETB position loop, which still uses throttle-body TPS. Until one complete cycle is valid, idle air retains instantaneous feedback. See [Advanced Idle Control](/Basic-Features/Idle-Control/Advanced-Idle) for the shared setting and fallback.

Log **Idle position**, **Idle: Target RPM**, idle PID terms/error, **Target**, physical TPS, **ETB: position error**, and **ETB: Duty**. If idle position changes but body TPS does not follow, check calibration, position limits, paused/stopped-engine disable, rev limiting, jam protection, and the H-bridge before changing gains. A low pedal does not guarantee a zero target.

## Sources

- [Pedal intent](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_tps.cpp#L236-L243)
- [Idle output](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/idle_thread.cpp#L289-L375)
- [ETB plumbing](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/idle_hardware.cpp#L30-L39)
- [Target composition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/electronic_throttle.cpp#L388-L415)
