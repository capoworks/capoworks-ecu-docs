# Experimental Ignition Timing

Capoworks ECU exposes two independent experimental ignition scheduling settings
under Experimental/Broken in TunerStudio. Both default to Legacy behavior and
should be treated as unvalidated on any particular engine until bench-tested.

## Cycle profile

**Ignition scheduling: Legacy / Cycle profile (experimental)** changes only the
final angle-to-time conversion for ignition charge and firing. RPM, injection,
global phase interpolation, trailing-angle offsets, and dwell-angle planning
keep their existing behavior.

## Time budget

**Dwell planning: Legacy / Time budget (experimental)** plans charge and fire
timing from the same bounded causal cycle history. It requires Individual Coils;
shared-coil and wasted-spark modes remain on Legacy planning. It additionally
requires a supported four-stroke, single-primary, rising-only missing-tooth
crank wheel and full cam phase synchronization. Current support includes 36-2
and 60-2 wheels. Unsupported geometry, unknown phase, direct self stimulation,
or an unavailable profile falls back to the Legacy conversion.

## Anti-lag soft spark skip

When the anti-lag system and launch control are compiled in, the anti-lag soft
spark limiter uses the configured **ALS skip ratio** only while anti-lag is
enabled and the anti-lag controller reports an active condition. If anti-lag is
disabled or not armed, the target skip ratio is zero and no sparks are skipped
by this limiter. The ratio is re-evaluated on each trigger event, so skipping
resumes when anti-lag re-arms and stops when it disarms.

This gating is a Capoworks ECU behavior fix. It does not change the configured
ratio value, so no tune migration is required. Verify anti-lag spark behavior on
the bench before relying on it; the change is covered by unit tests but has not
been validated on an engine.

## Configuration migration

The ignition cycle-profile setting was introduced in flash data version `20028`,
followed by the time-budget setting in `20029`; later schema additions may
advance the current version. Use the TunerStudio INI generated for the installed
firmware and follow the manual tune-transfer instructions.

## Planned timing behavior

The profile reuses Instant RPM's existing timestamp history and updates it
before the current tooth timestamp is overwritten. There is no second timestamp
ring. The causal ETA and inverse conversion are limited to 180 degrees and 32
references. Missing history uses the existing RPM conversion.

When armed, a time-budget target is attached to one cylinder TDC occurrence. A
newly observed target already behind the bounded horizon is counted as expired
and is not wrapped into a later occurrence. A retained candidate can accept a
feasible portion of a changed advance or retard command; an unchanged command
is not repeatedly rescheduled merely because another tooth arrived.

Before HIGH, the window reserves 0.8 times nominal dwell plus 100 microseconds
for planning and timer setup. While charging, a revised LOW must allow physical
minimum dwell and finish before the immutable 1.5 times nominal-dwell hard
deadline, less the same service reserve. HIGH and LOW callback generations are
invalidated before replacement registration. The first HIGH timestamp, output
ownership, nominal dwell snapshot, and physical deadline do not change when LOW
is retargeted.

## Limits

The 100-microsecond reserve is a software planning allowance, not a measured
worst-case interrupt or execution bound. The 1.5 times nominal-dwell cutoff is a
firmware timer, not independently clocked hardware current protection. Physical
TDC, coil current, output propagation delay, cranking behavior, and worst-case
interrupt latency require hardware validation.

Interpolation assumes roughly constant speed within each historical interval.
Tooth logs do not establish physical TDC or instantaneous speed between edges.
Low-speed ripple rescaled to high RPM is synthetic stress evidence, and host
test duration is not STM32 execution time. The planner is bounded but may
perform multiple conversions when several targets share a tooth; keep it
experimental pending target builds, replay review, and bench validation.

## Sources

- [Anti-lag skip-ratio gating in spark scheduling](https://github.com/capoworks/capoworks-ecu/blob/99653553158be194c039c0e699a7194d472effbc/firmware/controllers/engine_cycle/spark_logic.cpp)
- [Anti-lag soft-cut unit tests](https://github.com/capoworks/capoworks-ecu/blob/99653553158be194c039c0e699a7194d472effbc/unit_tests/tests/ignition_injection/test_ignition_scheduling.cpp)
- [Time-budget anti-lag state test](https://github.com/capoworks/capoworks-ecu/blob/99653553158be194c039c0e699a7194d472effbc/unit_tests/tests/trigger/test_ignition_cycle_profile.cpp)
