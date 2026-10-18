# Fuel priming pulse

The priming pulse essentially "primes" the intake before the car starts by spraying a pulse of fuel into it. This wets the intake walls which helps atomization by vaporizing the fuel from the turbulence caused when the intake valve is opened, sucking the pulse into the engine. For cars with long intake runners and injectors far from the valves, this is more important to tune so there is no delay in fuelling when cranking is initiated. For cars like Miatas with injectors spraying almost directly onto the back of the intake valves, this setting isn't strictly necessary to tune.

## Flood clear and priming

The priming pulse is skipped when flood clear is enabled and the driver throttle intent is strictly greater than 90%. It is also skipped whenever the engine is not stopped. The [flood clear](/Basic-Features/Cranking-Control/Flood-Clear) request uses the same driver throttle intent signal as the runtime fuel cut, so holding the accelerator down to clear a flooded engine also prevents the priming pulse from adding more fuel.

If `DriverThrottleIntent` is unavailable, the firmware treats it as 0 for this check. The missing signal therefore does not meet the flood-clear condition, but it does not guarantee that priming will occur because the engine-state and other priming conditions still apply.
