# How to test inputs and outputs

Use this sequence to prove Capoworks wiring and configuration before
commissioning. Check inputs first with the engine off. Output checks command
real loads, so plan isolation, fusing, and an actuator observer first.

## Input tests

1. Make the engine safe to remain stopped, power the ECU, and connect
   TunerStudio with the INI that matches the installed board target.
2. Open Sensor Checker or the live dashboard. Confirm battery voltage, coolant
   temperature, intake-air temperature, MAP, baro, and TPS readings are
   plausible for the current conditions. Compare temperature sensors with a
   reference and verify MAP/baro against a known pressure source where fitted.
3. Sweep the throttle with the engine off and check that TPS or accelerator
   pedal channels move smoothly without dropouts. For redundant tracks, verify
   they agree with the configured relationship.
4. Crank only after the engine-off checks pass, then confirm RPM and trigger
   sync appear. A stable RPM with no sync is not a valid trigger result.

## Output tests

Use __Bench Test & Commands__ for one output at a time. Confirm the configured
logical output against the board-specific pinout before applying power to a
load. Injector and ignition-coil commands are ignored while the engine is
running; those tests still require safe isolation from fuel, compression, and
ignition.

For a safe low-energy load or meter, trigger a single pulse and verify both the
software command and physical response. The Main Relay test enters a short
bench-test state before normal logic is evaluated; physical action depends on
the firmware's main-relay build gate. Fuel Pump On adds a forced-on request,
while Fuel Pump Off removes that request only: normal prime and recent-trigger
operation can still hold the pump on, so it is not an emergency fuel cut.

Stop after each check, confirm the output returned to the intended state, and
record any fault or unexpected load behavior. If a command produces no physical
response, verify supply, board output capability, pin, and output mode before
changing calibration.

## Sources

- [Bench command dispatch and engine-running guards](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/bench_test.cpp#L421)
- [Timed output-pulse implementation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/bench_test.cpp#L82)
- [Available bench output categories](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/bench_test.cpp#L266)
