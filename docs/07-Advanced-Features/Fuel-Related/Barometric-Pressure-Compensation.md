# Barometric Pressure Compensation

The current **Barometric pressure correction** table is a four-by-four fuel
multiplier indexed by barometric pressure and RPM. Its default cells are all
`1.0`, so the table does nothing until it is calibrated. The TunerStudio menu is
displayed only when the selected fuel model is **Speed Density**, but that is a
visibility condition, not a runtime gate. The running-fuel correction stack
includes the computed `baroCorrection` value globally. Alpha-N also has separate
`alphaNBaroCompensation` and `alphaNBaroReferencePressure` controls.

`baroCorrTable`, `baroCorrPressureBins`, and `baroCorrRpmBins` define the lookup.
The resulting `baroCorrection` is consumed in the running-fuel correction stack
after the base air mass is calculated. Calibrate it only from measured behavior
for the installed intake and operating range; changing the axis breakpoints
changes what each row means.

Failure behavior is specific. If no barometric-pressure sensor is registered,
`getBaroCorrection()` returns `1`. If a sensor is registered but has no valid
value, the lookup uses 101.325 kPa as its pressure fallback. A lookup result
that is `NaN` or below `0.01` produces the **Invalid baro correction** warning
and returns `1`. That warning itself emits
`OBD_Barometric_Press_Circ_Range_Perf`; there is no separate sensor-checker
diagnostic for this path.

For a MAP-derived start-up value, `useFixedBaroCorrFromMap` can seed the
barometric-pressure sensor from `MapSlow`. A missing MAP value defaults to
101.325 kPa, so an absent sample can seed standard atmospheric pressure. The
result is accepted only from 60 to 110 kPa; otherwise the fixed value is
disabled. The decoder has no RPM gate, so it cannot prove the engine is stopped:
the operator must ensure that condition before initialization or a re-read.
Use a dedicated barometric sensor when continuous ambient-pressure change
matters.

During diagnostics, compare the `baroCorrection` gauge with barometric pressure,
RPM, MAP, and the live correction cursor. Confirm the barometric sensor is
registered before interpreting unity. If unity is reported, check whether the
**Invalid baro correction** lookup warning was logged. That warning itself emits
`OBD_Barometric_Press_Circ_Range_Perf` when the lookup result is `NaN` or below
`0.01`, rather than through a separate sensor-checker diagnostic. See
[Load Sources](/Fuel/Fuel-Settings/Load-Sources) and
[Alpha-N](/Fuel/Fuel-Algorithms/AlphaN) for the model-specific paths.

## Source references

- [Correction lookup, warning, and missing-sensor behavior](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L825-L845)
- [MAP start-up seed, fallback and range validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/impl/map.cpp#L24-L39)
- [Running-fuel multiplier use](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L133-L149)
- [Speed Density editor gate](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2191-L2193)
