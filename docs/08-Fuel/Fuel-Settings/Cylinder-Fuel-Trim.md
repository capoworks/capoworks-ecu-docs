# Cylinder Model Fuel Trim

Every cylinder is slightly different. Intake manifold design, injector variation,
and uneven cooling can require small cylinder-specific fuel corrections. The
final Capoworks ECU calibration layout supports those corrections as
per-cylinder model fuel trims for Speed Density and Alpha-N.

This page describes the final `20032` tune layout at firmware commit
`8f4fcfb4`. It replaces the obsolete 4 x 4 fuel-trim guidance. The old tables
and their operating points are not migrated automatically.

## Final table layout

There are two independent trim families. Each is 16 x 16, uses one pair of
shared axes for its family, and has one table for every configured cylinder.

| Fuel model | X axis | Y axis | Cell value |
| --- | --- | --- | --- |
| Speed Density | RPM | Effective MAP in kPa | Signed fuel change in percent |
| Alpha-N | RPM | Normalized TPS in percent | Signed fuel change in percent |

The Speed Density and Alpha-N axes are independent of each other. Within each
family, every cylinder uses the same axes. In a four-cylinder engine, for
example, cylinder 1 and cylinder 4 do not each have private RPM and load
breakpoints; they both use the family's shared axes.

The generated menus are named `Cylinder model fuel trims - Speed Density
(16x16)` and `Cylinder model fuel trims - Alpha-N (16x16)`. Only cylinders up
to the configured cylinder count appear as active menu entries.

Each trim cell is a signed percentage. A positive value adds modeled fuel and
a negative value removes it. The exact neutral value is `0`, not `100`: all
trim tables are initialized to `0`, and the runtime factor is `1 + trim / 100`.

The final configuration accepts trim cells from `-25` to `25 percent` in
`0.2 percent` steps. The Speed Density load axis is limited to `0` through
`1000 kPa`; the Alpha-N TPS axis to `0` through `100 percent`; and RPM to `0`
through `18000 RPM`. Every active axis must also be strictly increasing.

## When each trim family is used

Standalone Speed Density uses only the Speed Density family. Standalone
Alpha-N uses only the Alpha-N family. MAF Air Charge, Lua, and mock air-mass
modes do not apply either family.

In `SD + Alpha-N` mode, the requested Alpha-N contribution comes from the
air-mass authority table. A `0%` authority cell runs Speed Density only and a
`100%` cell runs Alpha-N only. Interior values combine both model masses.
Consequently, both trim families can contribute at an interior authority.

The active trim family follows the effective authority after branch fallback,
not merely the requested authority:

- If both active branches are healthy, both contribute according to their
  blend weights.
- If one contributing branch fails and the other is healthy, the healthy
  branch supplies the complete model result. Effective authority moves to
  that branch's endpoint, and trim selection follows that endpoint.
- If neither branch is healthy, the model result is invalid. The runtime does
  not publish a partial trim candidate.

The trim calculation uses the branch masses captured for the same fuel
calculation. For each cylinder, the factor is:

`factor = 1 + ((weightedSD * sdTrim) + (weightedAlphaN * alphaNTrim)) / (weightedSD + weightedAlphaN) * 0.01`

`weightedSD` and `weightedAlphaN` are the branch cylinder air masses after
their effective blend weights. Common VE corrections are applied once after
the raw branch masses are selected and cancel from this trim ratio.

If the active family has no model evidence, the factors remain neutral. A
true zero-air result also remains neutral, but the runtime still validates the
active family. Invalid cells or axes in an inactive family do not block an
endpoint that does not use that family. Invalid calibration in an active
family prevents the complete fuel result from being published.

## What the trim does and does not include

The per-cylinder factor multiplies the modeled running fuel for that cylinder.
Because it is applied after modeled running corrections are calculated,
coolant, intake-air, barometric and after-start corrections can affect the
quantity that is then scaled by the trim.

The following terms remain outside the trim factor:

- Additive TPS acceleration enrichment.
- The Lua fuel multiplier and Lua fuel offset. They are applied later and can
  change the final trimmed quantity.
- Closed-loop bank trim, which is applied after the cylinder-specific modeled
  fuel calculation.
- Injector dead time, which is part of converting fuel mass to injector pulse
  width.
- Fixed cranking fuel when `Fuel Source For Cranking` is set to the fixed
  base-fuel mode. If running math is selected for cranking, the modeled path
  and its active trims are used.

DFCO and disabled injection still produce zero fuel. That includes the path
where a Lua fuel offset would otherwise be added.

The runtime prepares every configured cylinder's factor, validates the
candidate, and publishes the complete set with the fuel result. A stale tune
write or a stale fuel calculation cannot partially replace a newer result.

The related output channels are:

| Channel | Meaning |
| --- | --- |
| `sdCylinderFuelTrimLoad` | Captured Speed Density trim cursor in kPa, or `0` when that family is not contributing |
| `alphaNCylinderFuelTrimLoad` | Captured Alpha-N trim cursor in TPS percent, or `0` when that family is not contributing |
| `cylinderModelFuelTrim` | Effective per-cylinder change in percent after blend weighting |
| `cylinderModelFuelTrimBranches` | Active branch bits: `1` for SD and/or `2` for Alpha-N |

## Determining where trims are needed

Compare how evenly the cylinders are contributing under the same operating
conditions. Useful observations include:

- Per-cylinder exhaust gas temperature, where hotter and cooler runners can
  indicate different combustion conditions.
- Per-cylinder lambda, wideband O2 with cylinder balancing, or a controlled
  cylinder contribution test.
- Per-cylinder knock data logged by the ECU.
- Spark-plug appearance and deposits.
- Torque contribution measurements from an engine dynamometer.

These observations identify candidates; they do not by themselves prove that a
fuel trim is the correct correction. Address sensor, ignition, injector,
compression, and mechanical differences before using trim to mask them.

## Migrating the old 4 x 4 tables

Use the generated TunerStudio INI that matches the firmware and tune format.
The final tune format is `20032`; do not plan a migration through the older
intermediate layouts.

Before changing firmware:

1. Keep the old firmware, matching INI, and tune together.
2. Record or screenshot every old 4 x 4 trim table, including its RPM and load
   coordinates.
3. Record the old fuel strategy, blend table, blend load source, and blend
   breakpoints.

After moving to the final layout:

1. Recreate the intended Speed Density and Alpha-N behavior in their separate
   16 x 16 families. There is no automatic 4 x 4-to-16 x 16 conversion.
2. Enter the family axes first, then recreate cell intent at the desired
   RPM/load points. Do not assume that copying a 4 x 4 cell to one 16 x 16 cell
   preserves its old operating region.
3. For a blended tune, verify which authority values are active at idle,
   cruise, and transitional load after entering the new tables.
4. Verify the reported trim load cursors and branch bits, then check the
   resulting behavior under steady conditions before normal use.

The old and final table dimensions, axes, units, and active strategy rules are
different. The final engine configuration therefore cannot reconstruct a
universal replacement from the old binary tune.

## Core8 memory tradeoff

The expanded cylinder-model calibration is fitted on Core8 without removing
the existing `5 KiB` (`5120-byte`) main working stack or SD-card/FATFS and USB
mass-storage support. Core8 uses a `26000-byte` Lua heap instead of the
`30000-byte` F407 default. Other boards retain their existing Lua heap size.

On Core8, CAN, USB console, and USB mass-storage background working areas are
placed in ordinary SRAM so the calibration, engine state, and main-loop stack
can remain in CCM. This is a memory-placement change, not a change to the Lua
heap tradeoff described above.

## Source references

This page was checked against Capoworks firmware commit
[`8f4fcfb4`](https://github.com/capoworks/capoworks-ecu/commit/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52).
The final trim layout was introduced by
[`223895c1`](https://github.com/capoworks/capoworks-ecu/commit/223895c17f82f9fd07bac9e81414661440ac7475),
with blend and effective-authority behavior in
[`eee63c82`](https://github.com/capoworks/capoworks-ecu/commit/eee63c82b531db9bc6fa640c58ad76cf740a2ff0).

- [Authoritative cylinder-model trim notes](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/docs/user/cylinder-model-fuel-trims.md?plain=1)
- [Trim calculation and publication](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/cylinder_model_fuel_trim.cpp)
- [Trim candidate and state interfaces](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/cylinder_model_fuel_trim.h)
- [Final trim schema and shared-axis definitions](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/integration/fome_config.txt)
- [Neutral cells and default trim axes](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/defaults/default_fuel.cpp)
- [Fuel calculation and trim admission](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/fuel_math.cpp)
- [Per-cylinder final fuel composition](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/engine2.cpp)
- [Effective branch weights and fallback](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/blended_airmass.cpp)
- [TunerStudio trim tables, menus, and cursors](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/tunerstudio/tunerstudio.template.ini)
- [Core8 stack, RAM placement, and Lua heap settings](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/config/boards/core8/board.mk)
- [Trim unit and integration tests](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/unit_tests/tests/ignition_injection/test_cylinder_fuel_trim_integration.cpp)
