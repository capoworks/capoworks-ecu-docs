# Multispark

Multispark adds extra coil discharges after the primary spark. It does not
replace the main spark or its dwell table. Open **Ignition > Multispark** and
configure the RPM, angular window, extra-spark limit, post-spark delay, and
subsequent-spark dwell.

## Count and scheduling

`getMultiSparkCount(rpm)` returns zero unless `multisparkEnable` is true, RPM is
nonzero and at or below `multisparkMaxRpm`, and
`multisparkMaxExtraSparkCount` is greater than zero. The allowed extra count is:

`floor((time_per_degree * multisparkMaxSparkingAngle) /
(multisparkSparkDuration + multisparkDwell))`

capped by `multisparkMaxExtraSparkCount`. The main spark is not included. The
configured count is recalculated during the periodic ignition calculation.

After the main discharge, firmware waits `multisparkSparkDuration`, charges
for `multisparkDwell`, and fires. It repeats in real time while sparks remain,
provided ignition is enabled and the current cut state still permits charging.
A cut that begins during an active charge still allows that pulse to end, but
it suppresses subsequent extra sparks. Every pulse retains the independent
physical overdwell guard.

## Experimental ignition paths

`ignitionCycleProfile` changes final angle-to-time conversion for the primary
ignition event. The extra sparks that follow remain scheduled as elapsed-time
charge/fire events after the main discharge. `ignitionTimeBudget` can plan the
primary event only when Individual Coils, full cam phase sync, and a supported
cycle profile are available; otherwise primary scheduling falls back to
Legacy. Neither experimental option provides a separate multispark strategy or
removes the live cut and physical-dwell gates.

With trailing sparks enabled, the trailing event waits while multispark is
still charging and firing. Firmware then hands off to the trailing event and
retains the trailing dwell snapshot; multispark cannot rewrite it.

## Diagnostics and limits

`multiSparkCounter` reports `engineState.multispark.count`, the allowed extra
count, rather than proof that every extra discharge occurred. Check
`sparkCutReason`, RPM versus `multisparkMaxRpm`, the configured angular window,
and the delay/dwell pair. A small or zero window can intentionally produce no
extra sparks. Multispark can overheat coils, drivers, and ignition components;
multiplying dwell or assuming a universal safe configuration is not
supportable. Validate coil current, temperature, and trigger behavior on the
actual hardware.

## Sources

- [RPM, angular-window, and extra-count fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L379)
- [Post-spark delay and subsequent dwell fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1009)
- [Gate checks and count calculation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/ignition/ignition_state.cpp#L221)
- [Real-time extra-spark scheduling](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/spark_logic.cpp#L350)
