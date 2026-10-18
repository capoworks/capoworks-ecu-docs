# Override VE, Ignition and AFR Table Axis

The target lambda and main ignition tables can use a consumer-load source other than their model default. The VE load field is different: the current configuration still exposes it, but the standard physical air-mass models do not use it to redirect the main VE table. Changing an axis also changes what each row means; existing breakpoints and cell values are not converted automatically.

## Current consumer selectors

The target lambda/AFR and main ignition selectors are active, independent table-coordinate choices:

| Consumer | Field | Allowed choices |
| --- | --- | --- |
| Target lambda / AFR | `afrOverrideMode` | `Model default`, `Measured MAP`, `TPS`, `Acc Pedal`, `Cyl Filling %`, `Effective MAP` |
| Main ignition | `ignOverrideMode` | The same six choices |

The fields and `load_override_e` are defined in
[`fome_config.txt`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1068),
and the TunerStudio labels are **Target lambda load source** at
[`tunerstudio.template.ini`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2725)
and **Ignition table load source** at
[`tunerstudio.template.ini`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2749).

The selectors are captured into the air-mass input snapshot in
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L545)
and resolved independently by the shared load resolver starting at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L407).
They select coordinates for the lambda and ignition table lookups; they do not change how the active physical model calculates air mass.

`Model default` resolves through
[`resolveNativeModelLoad()`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L326).
It is effective MAP for Speed Density and SD + Alpha-N, normalized TPS for standalone Alpha-N, and pre-trim standardized cylinder filling for MAF Air Charge. `Measured MAP` requires a valid measured MAP value. `Effective MAP` may use the configured MAP estimate, while the percent choices are normalized coordinates. See [Load Sources](/Fuel/Fuel-Settings/Load-Sources) for their validity and fallback rules.

## VE field and current model axes

The generated configuration still exposes `veOverrideMode` with choices `None`, `MAP` and `TPS` in
[`fome_config.txt`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1064),
and TunerStudio still labels it **Override VE table load axis** in the
[final template](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2724).
It is retained as a legacy compatibility field. `captureAirmassInputs()` copies it at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L560),
but the only firmware code that reads the captured value is the legacy `getVe(rpm, load, ...)` wrapper at
[`airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/airmass.cpp#L865).

The standard physical models do not call that wrapper. They pass their strategy-owned axes directly to `evaluateVe()` or `evaluateRawVe()`:

| Strategy or table | Current Y axis |
| --- | --- |
| Standalone Speed Density `VE` | Captured effective MAP ([`speed_density_airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/speed_density_airmass.cpp#L69)) |
| Standalone Alpha-N `Alpha-N filling` | Normalized TPS ([`alphan_airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/alphan_airmass.cpp#L129)) |
| MAF Air Charge `MAF Trim` | Pre-trim standardized cylinder filling ([`maf_airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/maf_airmass.cpp#L129)) |
| SD + Alpha-N raw branches | Speed Density's native MAP and Alpha-N's normalized TPS, before the two masses are combined ([`blended_airmass.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/airmass/blended_airmass.cpp#L166)) |

Consequently, changing `veOverrideMode` does not redirect the current Speed Density VE table, Alpha-N filling table, MAF trim table, or either raw branch of SD + Alpha-N. The selector is also unrelated to a blend table's **Y axis override**.

The source test named
[`AirmassModes.VeOverride`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_fuel_math.cpp#L231)
drives a dummy model that explicitly calls the compatibility wrapper. It verifies the wrapper's behavior, not a current physical-model load axis.

## Before changing a consumer axis

1. Record the current table and breakpoints.
2. Confirm that the setting is a lambda or ignition consumer selector, not a blend table's Y-axis override.
3. Replace breakpoints that were tuned in the old units; values are not converted automatically.
4. Confirm the consumer table's live cursor follows the chosen source.
5. Check source validity and fault or fallback channels during a steady state before applying load.

Changing `afrOverrideMode` affects only the target lambda/AFR lookup, and changing `ignOverrideMode` affects only the main ignition lookup. The two selectors are independent.
