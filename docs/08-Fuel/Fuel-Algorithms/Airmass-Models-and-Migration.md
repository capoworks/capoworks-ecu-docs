# Airmass Models and Migration

Capoworks tune format `20032` separates the physical air-mass models from the
fuel, ignition and actuator tables that consume their calculated load. This
page describes the calibration layout and the manual migration needed when
coming from an older binary tune.

The standalone [Speed Density](/Fuel/Fuel-Algorithms/SD/),
[Alpha-N](/Fuel/Fuel-Algorithms/AlphaN/) and
[MAF Air Charge](/Fuel/Fuel-Algorithms/MAF/) strategies use different physical
inputs and different model tables. Do not reuse one table as though it had the
same axis in every strategy.

## Model calibration tables

The final template defines these tables:

| Strategy | Fuel menu table | Final size | Y axis | Cell value |
| --- | --- | --- | --- | --- |
| Speed Density | `VE` | 16 x 16 | Effective MAP in kPa | VE in percent |
| Alpha-N | `Alpha-N filling` | 16 x 16 | TPS in percent | Cylinder filling in percent at the configured reference pressure |
| MAF Air Charge | `MAF Trim` | 8 x 8 | Pre-trim standardized cylinder filling in percent (`100 × cylinder air mass / standard charge`) | Air-mass correction in percent |

The MAF trim table is intentionally not a 16 x 16 VE table in this layout. Its
primary air mass comes from the MAF sensor; the trim table corrects that
measured filling. The configuration template places RPM on the X axis and
`mafTrimLoadBins` on the Y axis. That Y coordinate is the pre-trim standardized
cylinder filling shown above, calculated from the MAF-derived cylinder air mass
before the trim cell is applied; it is not MAF sensor output in percent. With
two configured MAF sensors, the model sums two healthy sensors, uses twice one
healthy sensor if the other is unavailable, and returns no valid model result
if neither sensor is usable.

The later per-cylinder model fuel trims are separate from the tables above.
They have a 16 x 16 Speed Density family using effective MAP and RPM, and a
16 x 16 Alpha-N family using TPS and RPM. Each family has one shared pair of
axes and one trim table per configured cylinder. MAF, Lua and mock air-mass
modes do not apply those model fuel trims.

## What each model does

Speed Density calculates air mass from RPM, effective MAP, charge temperature,
displacement and cylinder count, using the `VE` table. Effective MAP is the
measured MAP when available, optionally estimated from the `MAP Estimate`
table when measured MAP is unavailable or transient estimation is enabled.

Alpha-N calculates reference filling from RPM and TPS using `Alpha-N filling`,
then applies one of two pressure policies. In standalone Alpha-N mode:

- With `Standalone Alpha-N: multiply MAP` enabled, the reference filling is
  multiplied by effective MAP divided by `101.325 kPa`. This branch does not
  apply BARO compensation.
- With that option disabled, the reference filling uses `101.325 kPa`. If
  `Alpha-N barometric compensation` is enabled, it is instead multiplied by
  ambient BARO divided by `Alpha-N calibration reference pressure`; if
  compensation is disabled, no BARO scaling is applied.
- An invalid BARO or calibration reference pressure falls back to
  `101.325 kPa` and marks the model result as degraded.

SD + Alpha-N always uses the pure-reference Alpha-N branch described above,
including its BARO policy; the standalone MAP-multiplication setting does not
change that branch.

MAF Air Charge converts measured mass airflow into cylinder air mass and a
standardized filling coordinate. It applies the `MAF Trim` percentage before
publishing the corrected mass. Its standard-air-charge calculation uses
`101.325 kPa` and `20 C`; the standalone MAF model does not expose the
`Air temperature source` field used by Speed Density and Alpha-N.

## Model settings in the final template

These labels appear in the final Capoworks TunerStudio definition:

| UI label | Choices or units | Models where shown |
| --- | --- | --- |
| `Fuel strategy` | `Speed Density`, `MAF Air Charge`, `Alpha-N`, `Lua`, `SD + Alpha-N` | Fuel settings |
| `Air temperature source` | `Tcharge` or `IAT` | Speed Density, Alpha-N and SD + Alpha-N |
| `Use MAP estimate table` | Enabled or disabled | Speed Density, Alpha-N and SD + Alpha-N |
| `Standalone Alpha-N: multiply MAP` | Enabled or disabled | Standalone Alpha-N |
| `Alpha-N barometric compensation` | Enabled or disabled | Standalone Alpha-N without MAP multiplication, and SD + Alpha-N |
| `Alpha-N calibration reference pressure` | kPa | When Alpha-N barometric compensation applies |
| `Idle VE load source` | `Model default`, `Measured MAP`, `TPS` or `Effective MAP` | When `Use idle VE table` is enabled |

`Use MAP estimate during transient` is an additional acceleration-enrichment
setting. It can make the MAP estimate active while measured MAP is still
usable. The estimate table is indexed by RPM and TPS, and its cells are
validated in the range `0` to `600 kPa`.

If the selected charge-temperature source fails, the model first falls back to
a valid IAT value. If IAT is also unusable, it uses `20 C`. Both cases set the
temperature-fallback diagnostic; a fallback is not reported as a healthy
measurement.

## Shared corrections

The four `VE blend` tables are common air-charge corrections. Each correction
has its own blend parameter, bias curve, table and optional Y-axis override.
The runtime evaluates these corrections from the same captured sensor frame as
the physical model.

In SD + Alpha-N mode, the raw Speed Density and Alpha-N masses are combined
first, and the common corrections are applied once to the combined mass. They
are not applied separately to each branch before blending.

Downstream running-fuel corrections such as the
`CLT multiplier`, `IAT multiplier`, barometric correction and after-start
correction remain in the fuel calculation. The per-cylinder model fuel trim
therefore factors modeled fuel, while those later corrections can still move
the trimmed fuel quantity. Acceleration enrichment, the Lua fuel offset and
fixed cranking fuel remain outside the model trim.

## Fuel publication and validity

Each calculation captures its inputs and tune generation once, evaluates the
physical model, applies corrections and prepares the complete fuel result.
The runtime publishes the per-cylinder result and consumer coordinates
together only if the calculation is still current. Stopping the engine, writing
the tune or failing the current calculation closes new injection admission;
already accepted output callbacks are allowed to finish. Cranking priming has
its own gate and remains independent.

For a physical model, the following conditions apply only to inputs required
by the active model and its enabled consumers. An input that is neither modeled
nor selected for a consumer is not required. For example, MAF Air Charge does
not require MAP or TPS merely because those sensors are configured. A fallback
can satisfy a requirement only when the model or consumer defines a substitute
for that same coordinate; a value from a different available input does not
substitute for an unresolved requirement.

- RPM, displacement and cylinder count are finite and greater than zero.
- When the active model or a selected consumer requires measured or effective
  MAP, that coordinate is in the inclusive range `0` to `1000 kPa`.
- When a MAP estimate is used to satisfy a required MAP coordinate, it is in
  the inclusive range `0` to `600 kPa`.
- When the active model or a selected consumer requires TPS, it is inside the
  configured sensor-error tolerance, then normalized to the inclusive range
  `0` to `100 percent`.
- When the active model or a selected consumer requires charge temperature, it
  is finite and greater than zero kelvin after the selected source or fallback
  is applied.
- When MAF Air Charge is active, at least one MAF source used by the model is
  finite and non-negative, and the interpolated MAF trim is finite and between
  `0` and `200 percent`.
- Axes used by the active model and selected consumers are finite, inside
  their configured bounds and strictly increasing.
- Corrections and the final cylinder air mass are finite and non-negative.
- Base fuel and cycle fuel are finite and non-negative.

An invalid required model or fuel result does not publish stale fuel. The
status changes to `Faulted`, and new injection is not admitted. A usable
fallback, such as a valid MAP estimate or a usable charge-temperature
substitute, can still publish fuel, but the status is `Degraded` and the model
fault identifies the fallback. This distinction prevents a substitute
coordinate from being treated as healthy sensor evidence.

## Migrating a tune to format 20032

The final migration target is the `20032` layout. Older binary tunes are
rejected and defaults are restored, so there is no safe universal automatic
import of an old binary tune. Do not plan a migration through the intermediate
`20026` or `20030` schemas.

Before changing firmware:

1. Keep the old firmware, its matching TunerStudio INI and the old tune
   together. Do not open the old tune in the final INI.
2. Export or screenshot every table you may need, including its X and Y axes.
   Record the active `VE`, `Alpha-N filling` behavior and `MAF Trim`
   corrections for the strategies you used.
3. Record the old per-cylinder fuel-trim tables and their RPM/load coordinates.
   The former 4 x 4 trims are not copied automatically.
4. Record the model settings, blend settings, table-load selectors and
   experimental ignition settings that differ from their shown defaults.
5. Save a copy of the old matching INI with the tune. The final firmware's
   generated INI is the reference for the new field names and units.

After installing the final firmware:

1. Start from the matching generated TunerStudio INI for that firmware build.
2. Select the intended `Fuel strategy`, then enter the final table axes before
   entering cell values.
3. Recreate the applicable model tables manually. Alpha-N cells formerly
   carried through the shared VE table belong in `Alpha-N filling`; verify MAF
   corrections against the old active VE values and the final MAF load axis.
4. Recreate the 4 x 4 fuel-trim intent in the appropriate Speed Density or
   Alpha-N 16 x 16 family. Do not assume that cell-for-cell copying preserves
   the old operating points.
5. Recheck the model, correction and consumer-load settings. Changing a table
   selector to a different unit requires its breakpoints to be retuned.
6. Confirm that the final result is not `Degraded` or `Faulted`, then validate
   the calibration from a known-safe operating state before normal use.

There is no source-backed rule that makes an old tune universally safe to
import. The physical tables, their coordinates and the per-cylinder trims all
changed, so migration requires observed old values and deliberate re-entry.

## Source references

This page was checked against the Capoworks firmware source and TunerStudio
configuration template at commit
[`8f4fcfb4`](https://github.com/capoworks/capoworks-ecu/commit/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52).
The dedicated model and fuel-publication work originated in commit
[`fef0a82e`](https://github.com/capoworks/capoworks-ecu/commit/fef0a82ef6899b7b09c77ad0c9dd4f8996fe1733),
with later final-layout changes folded into the pinned revision.

- [Final unreleased `20032` migration notes](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/CHANGELOG.md?plain=1)
- [Model table and policy definitions](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/integration/fome_config.txt)
- [TunerStudio table, menu and settings template](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/tunerstudio/tunerstudio.template.ini)
- [Speed Density model](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/speed_density_airmass.cpp)
- [Alpha-N model](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/alphan_airmass.cpp)
- [MAF model](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/maf_airmass.cpp)
- [Captured inputs, corrections and load resolution](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/airmass.cpp)
- [Fuel publication and admission](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/fuel_math.cpp)
- [Cylinder-model fuel-trim and migration notes](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/docs/user/cylinder-model-fuel-trims.md?plain=1)
