# SD + Alpha-N Air Mass Blending

Capoworks ECU can combine Speed Density (SD) and Alpha-N cylinder-air-mass
calculations in one fuel strategy. Select **Fuel strategy > SD + Alpha-N**.
The strategy uses the existing SD and Alpha-N branch calibrations together; it
does not replace either branch's tables or sensors.

## What the blend changes

The SD branch calculates cylinder air mass from RPM, MAP, temperature and the
Speed Density table. The Alpha-N branch calculates cylinder air mass from RPM,
TPS, temperature and the **Alpha-N filling** table. The blend decides how much
of each calculated cylinder air mass contributes:

```text
blended cylinder air mass =
    (1 - Alpha-N authority) * SD cylinder air mass
    + Alpha-N authority * Alpha-N cylinder air mass
```

The authority is a percentage. A **0%** cell uses SD only, a **100%** cell uses
Alpha-N only, and an intermediate cell mixes the two cylinder-air-mass
results. After that mix, one shared air-mass correction multiplier is applied
to the blended mass before fuel is calculated; the correction is not applied
separately to each branch or again later in fuel computation.

This is not a VE-percentage blend and it does not blend fuel pulse widths. The
existing **VE blend tables** are separate correction overlays; they do not
choose or combine the SD and Alpha-N air-mass models.

## Firmware and tune compatibility

Use the matching generated TunerStudio INI for the installed Capoworks
firmware. The layout that contains this feature uses flash data version `20032`.
Older binary tunes reset under the new layout and are not migrated
automatically. Back up the old tune, open it with the matching old definition,
and transfer the needed values into the new definition by hand. This includes
recreating any former 4x4 cylinder fuel-trim values in the appropriate SD or
Alpha-N model family.

## Create the authority table

1. In TunerStudio, open **Base Engine > Base Engine Settings**, set
   **Fuel strategy** to **SD + Alpha-N**, and write the setting.
2. Set up the SD and Alpha-N branch tables and their sensor inputs. A mixed
   authority region needs both branch results; a `0%` or `100%` endpoint
   evaluates only the branch that contributes there.
3. Open **Fuel > SD + Alpha-N blend**.
4. Choose **Authority Y-axis source**.
5. Fill in the 8x8 authority table. Its columns are RPM and its rows are the
   selected authority load. Cell values are **% Alpha-N**.

The two authority choices have different meanings:

- **TPS %** schedules authority from the TPS reading and table breakpoints.
  This is the firmware default.
- **Measured MAP kPa** schedules authority from a valid measured MAP reading
  and its pressure breakpoints. A MAP estimate cannot authorize the blend.

For measured-MAP authority, the load must be a valid finite measured MAP from
`0` through `1000` kPa. If that coordinate is unavailable, the firmware does
not schedule the authority table: requested authority is `0%`, so it first
tries the SD branch, then uses a healthy Alpha-N branch if SD cannot complete.
It marks authority unavailable and branch fallback in diagnostics, and the
admission state is degraded rather than faulted when a complete branch carries
the calculation. A missing authority coordinate alone therefore does not
immediately reject the calculation. If both branches fail, admission is
closed. A permitted TPS/RPM MAP estimate may serve the SD fallback, but it
never becomes the measured-MAP authority-table coordinate.

The authority Y-axis selects how much Alpha-N contributes; it does not retarget
either model. The SD branch remains indexed by its MAP/RPM table and the
Alpha-N branch remains indexed by its TPS/RPM filling table.

Changing **Authority Y-axis source** changes the table's units. Review and
re-enter the load breakpoints before running with the new source; they are not
converted automatically.

The factory-initialized authority table is all **0%**, with TPS as its load
source. That is only a starting state for a new configuration, not a validated
engine calibration or safe operating recommendation.

## Calibration requirements

The blended authority table is bilinearly interpolated, so its axes must meet
the firmware's strict checks:

- The authority load axis has 8 finite, non-negative, strictly increasing
  breakpoints. It must end at or below `100` for TPS authority or at or below
  `1000` for measured-MAP authority.
- The RPM axis has 8 finite, non-negative, strictly increasing breakpoints and
  must end at or below `18000` RPM.
- Every authority-table cell must be within `0` to `100` percent Alpha-N.
- The SD and Alpha-N branch axes must also pass their own strict checks. Their
  load and RPM breakpoints must be finite and strictly increasing; an Alpha-N
  TPS axis must stay within `0` to `100`, while MAP load axes must stay within
  their supported range and RPM axes must end at or below `18000`.

Invalid axes can prevent a valid composite calculation. Do not repair an axis
by duplicating a breakpoint; equal adjacent values fail the strict-ordering
check.

## Air-mass and idle policies

Use **Fuel > Air mass model settings** to select behavior shared by the active
air-mass calculation:

- **Air temperature source** selects **Tcharge** or **IAT** for the physical
  air-mass calculation. If the selected source is unavailable, the result is
  marked degraded rather than silently treated as fully healthy.
- **Use MAP estimate table** permits the TPS/RPM estimate to serve SD sensor
  fallback and the optional transient comparison. It does not make an estimate
  eligible for measured-MAP authority.
- **Alpha-N barometric compensation** scales the Alpha-N filling reference by
  measured BARO. **Alpha-N calibration reference pressure** records the
  pressure at which the Alpha-N filling table was calibrated. Review the
  Alpha-N table and calculated mass after changing either policy.

If the separate idle VE table is enabled, its **Idle VE load source** controls
the idle overlay's coordinate. The choices are **Model default**,
**Measured MAP**, **TPS**, or **Effective MAP**. A missing coordinate for that
choice causes idle-VE fallback and marks the affected branch degraded. In
blended operation, review the idle policy as well as both main branch tables.

## Fallback and diagnostics

When one contributing branch fails, the firmware may replace the composite
with the other complete, healthy branch. It does not use a numeric result from
a failed branch. If neither branch is healthy, the calculation is rejected and
new fuel admission is closed rather than using a fabricated air mass.

Fallback is a calculation policy, not a guarantee of absolute engine safety.
It cannot determine whether the remaining branch's calibration is physically
correct for the engine, fuel, sensors or operating condition.

Log and inspect these TunerStudio channels while commissioning and testing the
strategy:

- **Air blend: injection admission state** shows whether the composite is not
  ready, ready, degraded, or faulted.
- **Air blend: requested Alpha-N weight** and
  **Air blend: effective Alpha-N weight** show the table request and the
  authority actually used after fallback.
- **Air blend: model fault** and **Air blend: model flags** identify the fault
  class and fallback details.
- **Air blend: SD raw mass**, **Air blend: Alpha-N raw mass** and
  **Air blend: common correction multiplier** show the pre-blend masses and
  the single correction multiplier applied afterward.
- **Air blend: SD branch load**, **Air blend: Alpha-N branch load**,
  **Air blend: SD branch VE**, **Air blend: Alpha-N branch filling** and
  **Air blend: authority Y coordinate** show which branch coordinates and
  table values participated.
- **Airmass: Temperature used**, **Airmass: Temperature source**,
  **Alpha-N: BARO coefficient** and
  **Airmass: Temperature/MAP estimate fallback flags** expose the pressure and
  temperature policies.

For decoded numeric logs, **Air blend: injection admission state** maps to
`AirmassInjectionStatus`: `0` `Legacy` (not used by this composite strategy),
`1` `NotReady`, `2` `Ready`, `3` `Faulted` and `4` `Degraded`.
**Air blend: model fault** maps to `AirmassInjectionFault`: `0` `None`,
`1` `Configuration`, `2` `Sensor`, `3` `Correction`, `4` `Result`, `5` `Load`,
`6` `StrategyChange` and `7` `Scheduling`.

Verify that the selected authority coordinate has the expected units, the
effective authority matches the request when no fallback is active, and the
reported branch masses move consistently with the logged sensors. Do not
assume correct fueling from the presence of a numeric gauge.

### VE Analyze

Capoworks ECU qualifies VE Analyze only when the entire authority table is
uniformly `0%` (SD endpoint) or uniformly `100%` (Alpha-N endpoint) for the
current running session. A mixed table, branch fallback, active separate idle
VE, authority failure, or configuration write during the session removes that
qualification until the next actual engine stop. Tune the branch endpoint
tables under a qualified endpoint; a mixed authority table is not a VE Analyze
target.

## Independent load coordinates

The authority table controls only the SD/Alpha-N cylinder-air-mass blend.
Ignition correction, injection phase, staged injection, short-term fuel trim,
lambda protection and other load-indexed functions have their own load
selectors. Changing the blend axis does not change those consumers
automatically. The composite's internal coordinate is effective MAP, but a
consumer must explicitly select that or another load source according to its
own configuration.

Implementation evidence:
[blended_airmass.cpp at firmware commit 8f4fcfb](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/blended_airmass.cpp).
