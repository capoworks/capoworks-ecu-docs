# Injector Tester

The active injector tester is available at **Fuel > Injector test** and
**Controller > Injector test** when injection is enabled. It provides
**Injector #1** through **Injector #N** buttons, plus **Iterations**, **On time**,
**Off time**, **Abort test**, **Fuel pump on**, and **Fuel pump off**. Reference
gauges show battery voltage and low-side fuel pressure.

This is a static electrical/functional test, not an automatic flow bench. A
button sends one injector-test command. Firmware pulses the corresponding
configured injector output for the requested count, with the configured on and
off times. The Java console's **Bench Test** tab is another front end for the
same basic output test. No fuel-volume measurement, spray-pattern analysis,
dead-time calculation, dynamic-flow characterization, or automatic injector
calibration is performed.

The TunerStudio injector command is accepted only when the engine is stopped.
That interlock does not replace an external safe state: an already configured
output or console path must still be treated as capable of energizing an
injector. Use this function only with the injector circuit isolated from an
installed engine, or on a purpose-built bench with safe containment and
ventilation. Do not allow ignition or engine rotation during the test. Use
**Fuel pump off** unless controlled spray is intended, and do not treat it as an
emergency stop. It clears only the forced-on request; startup priming or a recent
trigger event can still hold the pump on. If the pump is turned on, verify
plumbing, pressure, and collection before commanding the injector. For a
guaranteed safe state, physically disconnect or isolate the pump circuit and
verify that its output is off.

For wiring diagnosis, compare the selected injector number with
`injectionPinsN`, confirm the output can be commanded, and observe battery voltage
and audible/electrical response. For flow testing, record pulse width and
pressure externally and compare collected mass in a proper bench setup. The
tester can prove that the output channel actuates; it cannot establish injector
flow or dynamic performance by itself.

## Source references

- [TunerStudio injector-test controls and commands](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4906-L4941)
- [Engine-stopped gate for TunerStudio test commands](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/bench_test.cpp#L421-L449)
- [Pulse generation and configured timing](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/bench_test.cpp#L82-L115)
- [Fuel-pump off clears only the forced request](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/fuel_pump/fuel_pump.cpp#L10-L35)
