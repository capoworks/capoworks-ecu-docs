# Load Sources

Capoworks firmware can give individual fuel, ignition and actuator tables their
own captured load coordinate. A selector changes the Y-axis source and units
for that consumer only. It does not change `Fuel strategy`, and it does not
change the authority of the SD + Alpha-N blend.

The selectors use full-precision values captured during the completed fuel
calculation. Packed datalog cursors are display values and are not read back as
control inputs.

## Selector choices and units

The final TunerStudio selector choices are:

| Selector label | Coordinate | Valid physical range |
| --- | --- | --- |
| `Model default` | The active physical model's native load | Depends on model |
| `Measured MAP` | MAP sensor value in kPa | `0` to `1000 kPa` |
| `TPS` | Throttle position in percent | Normalized to `0` to `100 percent` after sensor-tolerance checks |
| `Acc Pedal` | Accelerator pedal in percent | Normalized to `0` to `100 percent` after sensor-tolerance checks |
| `Cyl Filling %` | Standardized cylinder filling in percent | Finite and non-negative |
| `Effective MAP` | Measured or estimated MAP in kPa | `0` to `1000 kPa` |

The enum also contains `INVALID` entries. They are runtime guard values, not
normal choices to select for a table.

`Measured MAP` is only the physical MAP sensor. `Effective MAP` can be the
measured MAP or the `MAP Estimate` table value. An estimate is marked with the
MAP-estimate diagnostic bit and must not be mistaken for a measured sensor.

`Cyl Filling %` is calculated from the final, corrected cylinder air mass and
the captured displacement and cylinder count. It is not the same coordinate as
the pre-trim MAF load.

### What Model default means

The runtime resolves `Model default` as follows:

| Active fuel model | Runtime native coordinate |
| --- | --- |
| Speed Density | Effective MAP in kPa |
| Alpha-N | TPS in percent |
| MAF Air Charge | Pre-trim MAF cylinder filling in percent |
| SD + Alpha-N | Effective MAP in kPa |

The template helper label `modelDefaultLoadAxis` now matches these runtime
coordinates: it renders `Effective MAP kPa` for Speed Density and for
SD + Alpha-N, `TPS %` for standalone Alpha-N, and `Cylinder filling %` for the
remaining modes. Tables that use `Model default` therefore show the same
coordinate the runtime uses. This is a display-label correction only; it does
not change calibration offsets, the tune layout, or the runtime load
coordinate, and no breakpoint retune is required.

Capoworks ECU declares that `modelDefaultLoadAxis` helper in the TunerStudio
`[OutputChannels]` section, not in `[PcVariables]`. The `loadAxisLabels` list
that the helper indexes remains a `[PcVariables]` entry, and the table Y-axis
labels bind to it through `bitStringValue(loadAxisLabels, ...)`. This placement
only affects how the generated definition resolves the label; it does not
change calibration offsets, the tune layout, or the runtime load coordinate.

Legacy Lua and mock modes keep a compatibility path that resolves consumer
coordinates from the live historical fuel load. The captured publication
identity and model-validity gate described below are used by the revised Speed
Density, Alpha-N, MAF and SD + Alpha-N models.

## Configurable consumers

These exact field labels expose independent selectors in the final template:

| Function | Exact UI field label | Diagnostic load channel |
| --- | --- | --- |
| Target lambda table | `Target lambda load source` | Existing target-lambda table cursor; `Air blend: current lambda load` in model diagnostics |
| Main ignition table | `Ignition table load source` | Main ignition-table cursor |
| Injection phase | `Injection phase load source` | `Load: injection phase` |
| Cylinder ignition trims | `Cylinder 1` through `Cylinder 12` in `Cylinder ignition trim load sources` | `Load: ignition trim` |
| Short-term fuel trim regions | `Load source and units` | `Load: STFT` |
| Staged-injection table | `Table load source` | `Load: staged injection` |
| Lambda protection thresholds | `Threshold load source` | `Load: lambda protection` |
| Maximum lambda deviation table | `Deviation table load source` | `Load: lambda deviation` |
| Trailing-spark table | `Trailing spark table` | `Load: trailing spark` |
| Ignition IAT correction | `IAT correction table` | `Load: ignition IAT correction` |
| Maximum knock retard | `Maximum retard table` | `Load: knock retard` |
| Per-cylinder knock gain | `Gain cylinder 1` through `Gain cylinder 12` | `Load: knock gain` |
| HPFP target-pressure table | `Target table load source` | `Load: HPFP target` |

Ignition trim and knock gain each have one selector per cylinder. The other
listed functions have one selector. The base `Fuel strategy` remains a
separate setting.

## Independence from fuel mode and blend authority

A consumer selector is resolved from the values captured for the completed
fuel calculation:

- Speed Density supplies an effective-MAP native coordinate.
- Alpha-N supplies a TPS native coordinate.
- MAF Air Charge supplies pre-trim MAF cylinder filling as its native
  coordinate, while `Cyl Filling %` uses the final corrected mass.
- SD + Alpha-N supplies effective MAP as its native coordinate after branch
  blending and shared corrections.

Changing one consumer from `TPS` to `Measured MAP` does not change fuel
strategy, branch weights, the VE/filling calibration or another consumer's
selector.

SD + Alpha-N has a separate `Authority Y-axis source` with only these choices:

| UI choice | Authority coordinate |
| --- | --- |
| `TPS %` | TPS in percent |
| `Measured MAP kPa` | Strict measured MAP in kPa |

This authority control decides how much raw Speed Density mass and raw Alpha-N
mass are combined. It is not one of the consumer `load_override_e` selectors.
Changing `Authority Y-axis source` changes the units of the blend table and
requires all blend breakpoints to be retuned.

The per-cylinder Speed Density and Alpha-N model fuel trims also have their own
captured branch coordinates. They are not selected by the consumer load-source
fields above. In blended mode, the active trim family follows the effective
branch authority after branch fallback.

## Validity and fallback behavior

Strict source validity and the numeric fallback used for compatibility are
kept separate. The published snapshot records which source coordinates were
strictly valid; a fallback does not make its source healthy.

For a valid overall fuel calculation, a missing consumer coordinate can use
the legacy numeric substitute:

| Missing source | Compatibility value |
| --- | --- |
| Measured MAP or Effective MAP | `200 kPa` |
| TPS or Accelerator Pedal | `100 percent` |
| Cylinder filling | No invented numeric substitute |
| HPFP target using Measured MAP | `0 kPa` |

If a required enabled consumer uses a substitute, the calculation is marked
`Degraded` with model fault code `Load`. This can keep injection available
while making the fallback visible. If the final air mass itself is invalid,
there is no substitute that keeps the model healthy: the model is `Faulted`,
new injection is not admitted, and the published consumer cursor fields are
cleared.

A missing optional coordinate does not by itself invalidate a good air mass.
Coordinates are resolved from the captured frame without re-reading sensors,
and a newer publication cannot be replaced by an older prepared calculation.
Stopping the engine or changing the tune invalidates the captured publication
and clears its cursors.

## Diagnostic channels

The final output-channel names are:

- `Load: injection phase`
- `Load: ignition trim`
- `Load: STFT`
- `Load: staged injection`
- `Load: lambda deviation`
- `Load: lambda protection`
- `Load: trailing spark`
- `Load: ignition IAT correction`
- `Load: knock retard`
- `Load: knock gain`
- `Load: HPFP target`
- `Air blend: current lambda load`

The per-cylinder `ignition trim` and `knock gain` channels contain one value
per cylinder. Disabled consumers and unused cylinder slots publish zero.
Because the load-channel entries have no single built-in unit, read the unit
from the selector or table axis. A zero can mean either a genuine zero
coordinate or an inactive or cleared cursor.

The shared model diagnostics use these codes:

| Channel | Code | Meaning |
| --- | --- | --- |
| `Air blend: injection admission state` | `0` | `Legacy`: a completed successful standalone-model publication, or a legacy mode |
| | `1` | `NotReady` |
| | `2` | `Ready`: a successful SD + Alpha-N publication |
| | `3` | `Faulted` |
| | `4` | `Degraded`: fuel is available with a fallback |
| `Air blend: model fault` | `0` | `None` |
| | `1` | `Configuration` |
| | `2` | `Sensor` |
| | `3` | `Correction` |
| | `4` | `Result` |
| | `5` | `Load` |
| | `6` | `StrategyChange` |
| | `7` | `Scheduling` |

`Airmass: Temperature/MAP estimate fallback flags` is a bit field:

| Bit | Meaning |
| --- | --- |
| `1` | Temperature fallback |
| `2` | Alpha-N barometric fallback |
| `4` | MAP or effective-MAP fallback |
| `8` | MAP estimate was used |

`Air blend: common correction multiplier`, the SD and Alpha-N raw-mass
channels, requested and effective authority, branch loads and branch VE/filling
channels show which physical values produced the published result.

## Tuning checks

When changing a selector:

1. Confirm the table's displayed Y-axis unit matches the selected coordinate.
2. Retune breakpoints when moving between kPa and percent coordinates.
3. Confirm the matching `Load:` cursor follows the expected source.
4. Check admission state and model fault during steady and transient
   operation.
5. If a fallback is present, repair the input or deliberately validate the
   fallback path before continuing calibration.

The selectors are independent, but they are not interchangeable tuning
coordinates. A table calibrated on TPS should not be moved to MAP until its
breakpoints and cell values have been reviewed.

## Source references

This page was checked against Capoworks firmware commit
[`8f4fcfb4`](https://github.com/capoworks/capoworks-ecu/commit/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52)
and its generated definition. The independent consumer selectors were
introduced in commit
[`45298b90`](https://github.com/capoworks/capoworks-ecu/commit/45298b9020a52059c278d3d0ba16bae89b7e6a7f),
with later final-layout and fallback changes folded into the pinned revision.
The `modelDefaultLoadAxis` output-channel placement was made in Capoworks ECU
commit
[`cd84c4d0`](https://github.com/capoworks/capoworks-ecu/commit/cd84c4d0c698251c6ff1769356b9e7fb504cff37).
The SD + Alpha-N `Model default` label was corrected to Effective MAP in
Capoworks ECU commit
[`54019cb7`](https://github.com/capoworks/capoworks-ecu/commit/54019cb7711125a71d7b1b1d31cc4fd6becca209).

- [Selector fields and final defaults](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/integration/fome_config.txt)
- [Exact TunerStudio labels, menus and table cursor bindings](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/tunerstudio/tunerstudio.template.ini)
- [Strict load resolution and fallback projection](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/airmass.cpp)
- [Captured consumer publication and cursor output](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass_loads.cpp)
- [Fuel admission and selector consumption](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/fuel_math.cpp)
- [Diagnostic output-channel names](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/console/binary/output_channels.txt)
- [Load-resolution tests](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/unit_tests/tests/ignition_injection/test_airmass_load_resolution.cpp)
- [Consumer-publication tests](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/unit_tests/tests/ignition_injection/test_airmass_consumer_infrastructure.cpp)
- [Derived load-axis template regression test](https://github.com/capoworks/capoworks-ecu/blob/54019cb7711125a71d7b1b1d31cc4fd6becca209/java_tools/configuration_definition/src/test/java/com/rusefi/test/newParse/TsDerivedLoadAxisTest.java)
