# Fuel priming pulse

The priming pulse essentially "primes" the intake before the car starts by spraying a pulse of fuel into it. This wets the intake walls which helps atomization by vaporizing the fuel from the turbulence caused when the intake valve is opened, sucking the pulse into the engine. For cars with long intake runners and injectors far from the valves, this is more important to tune so there is no delay in fuelling when cranking is initiated. For cars like Miatas with injectors spraying almost directly onto the back of the intake valves, this setting isn't strictly necessary to tune.

## Flood clear and priming

The priming pulse is skipped when flood clear is enabled and the driver throttle intent is strictly greater than 90%. It is also skipped whenever the engine is not stopped. The [flood clear](/Basic-Features/Cranking-Control/Flood-Clear) request uses the same driver throttle intent signal as the runtime fuel cut, so holding the accelerator down to clear a flooded engine also prevents the priming pulse from adding more fuel.

If `DriverThrottleIntent` is unavailable, the firmware treats it as 0 for this check. The missing signal therefore does not meet the flood-clear condition, but it does not guarantee that priming will occur because the engine-state and other priming conditions still apply.

## Ignition switch-off and delayed priming

Capoworks ECU waits a short minimum delay plus the configured priming delay before it fires the priming pulse, so the sensors have time to wake up. A priming request that is still waiting when the ignition is switched off is discarded: it will not fire after key-off, and it will not fire later during a subsequent key cycle. Only the request from the current key cycle can produce a pulse.

If the priming pulse has already started when the ignition is switched off, that pulse is allowed to finish and its injector outputs are closed normally. This prevents an injector from being left open by a pulse that was cut short.

No tune setting controls this behavior and no action is required. It applies to Capoworks ECU builds that include this change; do not assume an older or differently branded binary behaves the same way.
