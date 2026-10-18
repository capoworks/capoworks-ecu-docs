# Multi-Dimensional Mapping

This page is the detailed reference for Capoworks VE blend and ignition adder overlays. Read [Multi-Dimensional Mapping fundamentals](/Fundamentals-Of-Tuning/Multi-Dimensional-Mapping) first.

## Blend structure

Each `blend_table_s` contains an 8 by 8 correction table, eight RPM breakpoints, eight load breakpoints, a blend parameter, a Y-axis override, and an 8-point bias curve. The schema and current limits are in
[`fome_config.txt`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1710).
The TunerStudio table, curve and dialog definitions expose the same pieces; see the
[curves and tables](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L997) and
[VE blend dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3085).

Four controls must not be confused:

- **Blend parameter** is the source read for the bias curve.
- **Bias curve** converts that source from its physical units into a `0` to `100%` application factor. Its horizontal breakpoints use the source's units.
- **Correction table** supplies the requested VE percentage or ignition degrees at RPM and load.
- **Y-axis override** replaces the correction table's normal load coordinate. `Zero` means no override. This is a table-axis selection, not the blend source.

Source channels are fixed by the
[`gppwm_channel_e` enum](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L296).
They cover TPS, MAP, temperatures, loads, auxiliary and vehicle inputs, VVT, GPPWM and Lua gauges. `Zero` disables the blend.

## VE calculation and stacking

For an enabled, applicable VE blend, with correction-table value `T` in percent and bias `B` in percent:

```text
blend correction = T * B / 100
blend multiplier = 1 + (blend correction / 100)
corrected VE = base VE * multiplier
```

This is the calculation in
[`engine_math.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/math/engine_math.cpp#L216).
Within the selected set, the airmass path applies the same formula and multiplies the active VE blends together in
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L716).
For example, `T = +10%` and `B = 50%` produce `+5%`, multiplying VE by `1.05`. A second active result of `-10%` gives `1.05 × 0.90 = 0.945`, not a net `0.95`.

**Apply to table** selects which VE model consumes an overlay when corrections are applied inside a standalone Speed Density or Alpha-N calculation. Those models pass their consumer type into correction evaluation at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L840),
and the evaluator skips a blend assigned to the other table at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L703).
In those standalone modes, a disabled or differently assigned blend contributes a multiplier of `1`.

**Capoworks SD + Alpha-N exception:** raw Speed Density and Alpha-N masses are combined first, then
[`BlendedAirmass`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/blended_airmass.cpp#L237)
calls `evaluateAirmassCorrections()` without a consumer. That entry point passes no table filter at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L749).
Every enabled VE overlay is therefore applied once to the combined mass, regardless of its **Apply to table** assignment. The field does not route a correction to only the SD or only the Alpha-N branch in this mode. Unless a blend Y-axis override replaces it, the correction table uses the combined model's native effective-MAP coordinate.

Standalone MAF Air Charge does not apply these common VE overlays. It uses the dedicated `MAF Trim` table indexed by pre-trim standardized cylinder filling at
[`maf_airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/maf_airmass.cpp#L129).

## Ignition calculation and stacking

For ignition, the same product is added in degrees:

```text
ignition correction = T * B / 100
final advance = base advance + sum(all active ignition corrections)
```

The base table is interpolated first and every enabled adder is then added in
[`ignition_state.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/ignition/ignition_state.cpp#L47).
Thus `T = -6°` and `B = 50%` apply `-3°`. Active adders sum: `+2°`, `-3°` and `+1°` produce `0°` net.

## Neutral values and faults

`Zero` as the blend parameter disables the blend. A `0` correction cell, or a bias result of `0%`, also makes that blend neutral. For VE that means multiplier `1`; for ignition it means `0°`.

If the blend source is unavailable, the ignition path returns a zero correction. The VE path skips the unusable correction and marks the correction evaluation as a fallback. An unavailable VE Y-axis override likewise skips that blend; the ignition helper currently substitutes `0` for an unavailable Y-axis override. Inspect the live channels rather than assuming a failed axis produced a valid zero-load result.

The tests in
[`test_fuel_math.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_fuel_math.cpp#L475)
verify neutral VE behavior, invalid-source behavior, standalone table selection and multiplicative stacking. The combined-path test at
[`test_airmass_evaluation.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_airmass_evaluation.cpp#L394)
checks that both enabled overlays are applied after the raw branches have been combined.

## Diagnostics

Log `veBlendParameter`, `veBlendBias`, `veBlendOutput` and `veBlendYAxis` for VE, or the corresponding `ignBlend*` channels for ignition. Their declarations and units are in
[`output_channels.txt`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/binary/output_channels.txt#L286).
`Parameter` shows the source value, `Bias` the curve result, `Output` the applied percent or degrees, and `YAxis` the correction-table row actually used.

## Relationship to SD + Alpha-N

VE blend overlays are distinct from the **SD + Alpha-N** fuel strategy. SD + Alpha-N combines complete Speed Density and Alpha-N cylinder-air-mass calculations through its own 0 to 100% authority table, then in the Capoworks path applies every enabled shared VE correction once to the combined mass. **Apply to table** does not select a branch in that path. VE blends do not choose the authority value. See [SD + Alpha-N Air Mass Blending](/Fuel/Fuel-Algorithms/Blended) and [Load Sources](/Fuel/Fuel-Settings/Load-Sources).
