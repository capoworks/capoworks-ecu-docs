# Fuel Pump Control

This setting controls the low-pressure fuel-pump output. High-pressure
direct-injection pump control is a separate system.

Configure __Output__ and __Output mode__ under _Fuel > Fuel Pump_. Select only
an output supported by the installed board. __Prime duration__ sets how long
the pump is requested after the ignition-on transition; do not describe that
interval as universal, because it is part of the calibration.

## Prime, run, and shutdown

At ignition-on, Capoworks starts the prime timer and requests the pump for the
configured duration. The timed prime request requires the ignition to remain on:
if the ignition is switched off before the prime duration expires, the prime
request ends on the next controller update instead of holding the pump on. Each
ignition-on transition restarts the prime interval.

When the prime request ends, the pump stays on only while a crank or cam trigger
event has been seen recently, or while a forced-on bench request is active. The
recent-motion window is calculated from the trigger pattern and low-RPM
threshold rather than a single fixed delay. Builds without shaft-position input
cannot use the recent-trigger hold term, although the configured prime request
still applies.

When none of those conditions remains true, the controller drives the output
off. If pump power is supplied through the main relay, main-relay shutdown also
removes that supply. Use the __Fuel pump on__ bench command only with the fuel
system arranged for a controlled test. __Fuel pump off__ clears the manual
request; it does not override an active prime or recent-trigger request.

## Diagnostics

Watch the __Fuel pump on__ indicator and `isFuelPumpOn`. Confirm the selected
output and output mode, then check the physical supply and relay/fuse circuit.
If the pump runs briefly at key-on and stops, that is consistent with the prime
expiring while the engine is stopped. If it does not continue during cranking,
inspect trigger sync. If it remains on with no cranking or prime, check for a
leftover forced-on request or unexpected trigger activity.

See [High Pressure Pump Settings](/Advanced-Features/GDI/High-Pressure-Pump)
for the separate direct-injection valve.

## Sources

- [Fuel-pump prime, trigger, and forced-state logic](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/fuel_pump/fuel_pump.cpp#L10)
- [Published fuel-pump state channels](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/fuel_pump/fuel_pump_control.txt#L1)
- [Prime, run, and forced-state tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/actuators/test_fuel_pump.cpp#L12)
- [Prime-duration setting](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1017)
