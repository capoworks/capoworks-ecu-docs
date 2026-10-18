# Advanced Idle Control Features

## Idle tables for cranking taper

Setting this value to __true__ enables the use of the Idle Ignition Table and Idle VE Table during the cranking to idle taper period. See _Cranking Settings > After cranking IAC taper duration (cycles)_. If set to __false__ these tables are only active when idle is detected; see Idle Detection Thresholds section of the _Idle settings_ menu.

## Coasting Idle tables

Setting this value to __true__ will enable the _Coasting IAC Position_ table. This will manually over-ride the Idle Air Control valve position during the coasting phase. This can be used to help reduce engine braking and may be useful if the engine has difficulty returning to idle.

The coasting phase is determined by first checking if the TPS (or throttle pedal position if using ETB) is less than the _TPS Threshold_. If so, Capoworks ECU next checks if the current RPM is greater than the maximum idle RPM (`Idle Target RPM + RPM Upper limit`) and the engine is no longer in the _cranking IAC taper duration_. If all of these conditions are true, the engine phase is coasting and the _Coasting Idle Table_ is used.

## Rolling-cycle idle RPM feedback

Closed-loop idle air and closed-loop idle ignition timing can use either instantaneous RPM or a full-engine-cycle RPM estimate as feedback. The selector is named __Idle-only RPM feedback__ in both:

- __Idle > Idle settings > Closed Loop Idle__, for closed-loop idle air. This panel is available when _Idle control mode_ is _Open Loop + Closed Loop_.
- __Idle > Closed-loop idle timing__, for closed-loop idle ignition timing. Enable __Enable closed loop idle ignition timing__ to use the timing controller.

Both controls edit the same `idleTimingUseRollingRpm` setting. The choices are _Instantaneous_ and _Rolling cycle_. _Instantaneous_ is the default. Changing the selection from either dialog changes the feedback source for both closed-loop consumers and resets the idle PID states and rolling RPM history.

In _Rolling cycle_ mode, Capoworks ECU measures RPM from the same decoded trigger event one complete engine cycle earlier. That is 720 degrees for a four-stroke engine and 360 degrees for a two-stroke engine. The calculation reuses the Instant RPM timestamp history and rejects history across a trigger-shape change, a cam phase resynchronization, or a discontinuity in the decoded event sequence.

One complete engine cycle of valid, synchronized history is required before the rolling estimate becomes available. After a mode change, synchronization loss, or trigger change, the history must fill again.

Until the window is ready:

- Closed-loop idle air continues to use instantaneous RPM and RPM rate, so airflow control remains responsive.
- Closed-loop idle ignition timing applies zero correction. It does not substitute instantaneous RPM for the rolling source.

_Rolling cycle_ changes only the feedback used by closed-loop idle air and closed-loop idle ignition timing. Idle phase detection still uses instantaneous RPM, and open-loop air control and other RPM consumers are unchanged. The different feedback may require retuning the idle PID gains.

The diagnostic channel is `rollingCycleRpm`, shown in TunerStudio as __RPM - rolling cycle__. It reads zero while _Instantaneous_ is selected, while rolling history is disabled or invalid, and until one complete cycle is available. A non-zero value confirms that the idle controllers have a usable rolling estimate.

## Current tune layout

The current tune layout is `20032`. Older binary tunes are not compatible with this layout and reset when the firmware is installed. Use the TunerStudio INI generated for the installed firmware and transfer calibration values manually.
