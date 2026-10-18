# Experimental Ignition Timing

Capoworks ECU includes two independent, opt-in ignition scheduling experiments. Both default to _Legacy_, the established scheduling path. Keep _Legacy_ unless you are prepared to inspect logs, validate timing and dwell on the intended hardware, and change one setting at a time.

The settings are under __Controller > Experimental/Broken__:

- __Ignition scheduling__ edits `ignitionCycleProfile`. Its choices are _Cycle profile (experimental)_ and _Legacy_.
- __Dwell planning__ edits `ignitionTimeBudget`. Its choices are _Time budget (experimental)_ and _Legacy_.

The controls are independent. Either option may be enabled alone.

## Cycle profile

_Cycle profile (experimental)_ uses the recent tooth timing profile for the final angle-to-time conversion of ignition charge and firing delays. It does not change the engine RPM estimate or injection scheduling, and it does not change dwell-start angle planning.

The profile requires:

- A supported four-stroke, single-primary, rising-only missing-tooth crank wheel repeated over 720 degrees. Current support includes 36-2 and 60-2 wheels.
- Full cam/engine-phase synchronization.

Any interval outside the validated profile, an unsupported trigger shape, missing profile history, or loss of full synchronization falls back to the existing RPM-based angle conversion. Direct self-stimulation does not build the profile. During spin-up or other periods without full phase synchronization, use of the profile is therefore unavailable.

## Time-budget dwell planning

_Time budget (experimental)_ plans ignition charge and firing from a bounded causal model of recent tooth timing. It is active only when all of these conditions are met:

- __Dwell planning__ is set to _Time budget (experimental)_.
- The current ignition mode is Individual Coils. Shared-coil and wasted-spark scheduling remain on Legacy planning. Individual Coils also uses wasted-spark behavior during spin-up when full phase information is unavailable.
- Full cam/engine-phase synchronization is present.
- Direct self-stimulation is not active.
- The configured trigger shape produced a supported profile.

If any eligibility condition fails, ignition remains on the Legacy scheduling path. If the overall path is eligible but a bounded profile conversion is temporarily unavailable, the conversion uses the existing RPM-based angle calculation.

Each time-budget target is associated with one cylinder TDC occurrence. A new target that is already behind the bounded planning horizon expires instead of being wrapped into a later TDC. While a target remains available, a changed timing command may be retargeted within the feasible interval between the current plan and the new request. An unchanged command is not rescheduled merely because another tooth arrives.

The planner uses causal history and looks forward by no more than 180 degrees or 32 tooth references. The retarget window excludes the time required to service the change and the configured physical limits:

- Before the coil is switched on, the timing window reserves 0.8 times the nominal dwell plus 100 microseconds for planning and timer setup.
- While charging, a revised firing time cannot occur before 0.8 times the nominal dwell has elapsed.
- The revised firing time must also finish before the independent physical deadline, less the 100-microsecond service allowance.
- The physical output guard discharges the coil no later than 1.5 times the nominal dwell after its first HIGH edge. This deadline wins over a later requested firing time.

Before HIGH, a revised firing target can move the pending charge within the same causal window. Once charging has begun, retargeting does not renew the first HIGH time, output ownership, nominal dwell snapshot, or physical deadline. Old HIGH and firing callback generations are invalidated before replacement callbacks are registered, preventing a superseded callback from applying to the newer occurrence.

The 100-microsecond allowance is a software planning reserve, not a measured worst-case interrupt or execution bound. The 1.5-times-nominal deadline is a firmware timer guard, not independently clocked hardware current protection.

## Behavior that does not change

Neither experimental setting changes the RPM policy used by the rest of the engine controller or changes injection scheduling. They alter final ignition timing/dwell planning only. The selected dwell values still must be appropriate for the coils, [Dwell](/Ignition/Ignition-Settings/Dwell/) must remain configured, and [Ignition Mode](/Ignition/Ignition-Settings/Ignition_Mode/) must match the physical outputs.

The profile interpolates between observed tooth timestamps under an approximately constant-speed assumption. Tooth timestamps do not establish physical TDC, coil current, output propagation delay, or worst-case interrupt latency. Cranking behavior and timing accuracy therefore require bench and on-engine validation for the specific trigger, ECU, drivers, and coils.

## Current tune layout

The current tune layout is `20032`. Older binary tunes are not compatible with this layout and reset when the firmware is installed. Use the TunerStudio INI generated for the installed firmware and transfer calibration values manually.
