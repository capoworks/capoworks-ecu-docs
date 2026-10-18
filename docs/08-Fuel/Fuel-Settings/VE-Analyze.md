# VE Analyze

TunerStudio's VE Analyze feature uses a target lambda table, a measured lambda
channel, and a closed-loop fuel-correction channel to adjust a selected fuel
table. The final Capoworks ECU template gives Speed Density, Alpha-N, and MAF
Air Charge their own analysis definitions and filters.

This page describes the generated INI and firmware behavior at Capoworks commit
`8f4fcfb4`. It does not claim that the default filters make every log valid or
that the result is suitable for an engine without other checks.

## Which table is analyzed

| Fuel strategy | Analyzed table | Extra condition |
| --- | --- | --- |
| Speed Density | `VE` | Healthy standalone model |
| Alpha-N | `Alpha-N filling` | Healthy standalone model |
| MAF Air Charge | `MAF Trim` | Healthy standalone model |
| `SD + Alpha-N` | `VE` only when qualified endpoint is `1` | Whole authority table must be uniformly `0%` |
| `SD + Alpha-N` | `Alpha-N filling` only when qualified endpoint is `2` | Whole authority table must be uniformly `100%` |

Every definition uses `Target Lambda Table` as its lambda target, `Lambda 1`
as the measured lambda channel, and `egoCorrectionForVeAnalyze` as the
closed-loop correction channel. The latter is calculated as
`100 + fuelPidCorrection1`.

VE Analyze is disabled in the template while `Use idle VE table` is enabled.
The separate Idle VE table has its own load source and is outside these
analysis definitions.

## Healthy status is required

The template admits a VE Analyze map only while `blendedStatus` is `0`
(`Legacy`) or `2` (`Ready`). These values represent a healthy standalone
model or a healthy composite SD + Alpha-N model, respectively.

| Status code | Name | VE Analyze admission |
| --- | --- | --- |
| `0` | `Legacy` | Allowed for a healthy standalone model |
| `1` | `NotReady` | Excluded |
| `2` | `Ready` | Allowed for a healthy composite model |
| `3` | `Faulted` | Excluded |
| `4` | `Degraded` | Excluded |

A fallback may still produce usable fuel, but the fuel status is `Degraded`.
Those samples are not healthy model evidence, so they are excluded from VE
Analyze even when injection continues. Inspect `Air blend: admission state`,
`Air blend: fault`, and `Air blend: flags` when the selected map does not
become available.

## Blended SD + Alpha-N qualification

The firmware scans the complete blended air-mass authority table. It qualifies
an endpoint only when every cell is the same valid endpoint:

- All cells exactly `0%`: qualified endpoint `1`, Speed Density.
- All cells exactly `100%`: qualified endpoint `2`, Alpha-N.
- Any mixed, intermediate, invalid, or unavailable result: endpoint `0`, no
  qualified analysis map.

This prevents a delayed lambda sample from a mixed-air-mass region from being
credited to either model table. The final firmware does not enable mixed-map
automatic tuning.

Qualification applies to a running session:

- A mixed authority table marks the session invalid and clears the qualified
  endpoint.
- Returning the table to an endpoint after that, without an engine stop, does
  not reopen the session.
- Branch or other fallback operation, a fault, active Idle VE, or a running
  configuration or calibration write also prevents qualification.
- An actual engine stop resets the session state. The next run must qualify
  its own endpoint.

The live channel `Air blend: qualified VE Analyze endpoint` has the same
codes: `0` means none, `1` means Speed Density, and `2` means Alpha-N. The
selection is based on the whole table, not only the cell under the current
cursor.

## Template filters

A filter excludes a sample when its condition is true. The generated
TunerStudio template supplies the following defaults. Values marked adjustable
can be changed in VE Analyze without changing the ECU calibration.

### Common operating filters

| Filter | Default condition |
| --- | --- |
| Minimum RPM | `RPMValue` less than `500` |
| Minimum CLT | `coolant` less than `60 C` |
| dTPS | `deltaTps` greater than `50` |
| VBatt | `VBatt` less than `12 V` |

The Speed Density definition also includes:

| Filter | Default condition |
| --- | --- |
| Minimum MAP | `MAPValue` less than `0 kPa` |
| Maximum MAP | `MAPValue` greater than `1000 kPa` |
| Minimum TPS | `TPSValue` less than `0 percent` |
| Maximum TPS | `TPSValue` greater than `100 percent` |

The Alpha-N and MAF definitions include `Minimum TPS`, with a default
condition of `TPSValue` less than `1 percent`.

### Fuel-event and lambda filters

These filters are present for all three analysis strategies:

| Filter | Default condition | Adjustable |
| --- | --- | --- |
| Cranking | `veAnalyzeIsCranking` greater than `0` | No |
| Maximum TPS AE correction | `veAnalyzeTpsAeMagnitude` greater than `0.01 ms` | Yes |
| Maximum wall correction | `veAnalyzeWallCorrectionPercent` greater than `2 percent` | Yes |
| Maximum after-start enrichment | `veAnalyzeAfterStartPercent` greater than `1 percent` | Yes |
| Maximum warmup correction | `veAnalyzeWarmupPercent` greater than `1 percent` | Yes |
| Fuel or spark cut / DFCO | `veAnalyzeCutActive` greater than `0` | No |
| Minimum time after cut | `veAnalyzeTimeSinceCut` less than `2 s` | Yes |
| Launch or anti-lag active | `veAnalyzeAuxFuelActive` greater than `0` | No |
| Invalid lambda | `veAnalyzeLambdaInvalid` greater than `0` | No |
| Minimum lambda | `lambdaValues1` less than `0.5` | Yes |
| Maximum lambda | `lambdaValues1` greater than `1.5` | Yes |

`std_Custom` is also present in each block for an optional user expression.

The lambda limits above are the template defaults, not universal tuning
targets. The target table remains the source for the desired lambda. Calibrate
the Lambda Delay Table for the engine and exhaust installation; these filters
do not compensate exhaust transport delay, and they do not validate fuel
pressure or sensor health.

## Log-channel definitions

The template derives the filter channels as follows:

| Channel | Definition |
| --- | --- |
| `egoCorrectionForVeAnalyze` | `100 + fuelPidCorrection1` |
| `veAnalyzeTpsAeMagnitude` | Absolute value of `tpsAccelFuel` in milliseconds |
| `veAnalyzeInjectionMultiplier` | `currentInjectionMode == IM_SIMULTANEOUS ? 1 / max(cylindersCount, 1) : (currentInjectionMode == IM_BATCH ? 0.5 : 1)` |
| `veAnalyzeWallCorrectionPercent` | `100 * abs(wallFuelCorrectionValue) / max(running_fuel * veAnalyzeInjectionMultiplier, 0.01)` |
| `veAnalyzeAfterStartPercent` | `abs(running_postCrankingFuelCorrection - 1) * 100` |
| `veAnalyzeWarmupPercent` | `abs(running_coolantTemperatureCoefficient - 1) * 100` |
| `veAnalyzeCutActive` | DFCO active, or a nonzero fuel-cut reason, or a nonzero spark-cut reason |
| `veAnalyzeAuxFuelActive` | Launch control or anti-lag active |
| `veAnalyzeLambdaInvalid` | `Lambda 1` is NaN or less than or equal to `0` |

The wall-correction normalization accounts for simultaneous and batch
injection modes. If the wall-fuel model is disabled, the firmware reports
`wallFuelCorrectionValue` as `0` even though the model may retain internal
history. The derived wall-correction filter channel therefore becomes `0`; a
stale correction does not continue filtering valid samples.

The TPS acceleration term is the delivered additive fuel pulse, including
fractional tails and deceleration behavior. It is not merely the TPS
acceleration trigger flag.

## Published status and recovery channels

The final output definition publishes two VE Analyze recovery values in
padding that already existed in the output layout, so existing channel offsets
remain unchanged:

| Channel | Location and meaning |
| --- | --- |
| `VE Analyze: Cranking` (`veAnalyzeIsCranking`) | One byte at offset `259`; `1` while the engine is cranking |
| `VE Analyze: Time since fuel/spark cut or DFCO` (`veAnalyzeTimeSinceCut`) | Two bytes at offset `262`; seconds with `0.01 s` resolution |

`veAnalyzeTimeSinceCut` is the shorter of the time since the latest DFCO event
and the time since any fuel or spark cut. A new cut resets it to zero. The
reported value is clamped to the range `0` through `655.35 s`.

The combined state is also available through:

- `Air blend: admission state`
- `Air blend: fault`
- `Air blend: model flags`
- `Air blend: qualified VE Analyze endpoint`

The runtime test coverage includes cranking and disabled-wall-model telemetry,
cut-recovery reset and saturation, healthy and degraded admission, permanent
in-session invalidation after mixed authority, and reset at engine stop.

## Before accepting an analysis

Use the INI generated for the installed firmware. Confirm the intended fuel
strategy and target table, verify that the model status is healthy rather than
degraded, and review the active filters and lambda channels before accepting
table changes. For a blended run, the whole authority table must remain at one
endpoint for the complete qualified session.

The per-cylinder model fuel trims are a separate correction. They weight the
Speed Density and Alpha-N model masses, apply one factor after the common model
correction, and do not change the VE Analyze table-selection rules. See
[Cylinder Model Fuel Trim](/Fuel/Fuel-Settings/Cylinder-Fuel-Trim/) for that
layout.

## Source references

This page was checked against Capoworks firmware commit
[`8f4fcfb4`](https://github.com/capoworks/capoworks-ecu/commit/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52),
which finalized strategy-specific filters and recovery-state publication. The
qualified blended endpoint builds on
[`eee63c82`](https://github.com/capoworks/capoworks-ecu/commit/eee63c82b531db9bc6fa640c58ad76cf740a2ff0)
and captured consumer coordinates from
[`45298b90`](https://github.com/capoworks/capoworks-ecu/commit/45298b9020a52059c278d3d0ba16bae89b7e6a7f).

- [Final TunerStudio VE Analyze definitions and filters](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/tunerstudio/tunerstudio.template.ini)
- [Cranking and cut-recovery telemetry](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/console/status_loop.cpp)
- [Output-channel declarations and offsets](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/console/binary/output_channels.txt)
- [Whole-table endpoint qualification](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/airmass/airmass.cpp)
- [Runtime analysis admission and session state](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/fuel_math.cpp)
- [Injection admission state transitions](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/engine_cycle/airmass_injection_state.cpp)
- [Engine-stop reset](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/controllers/algo/engine.cpp)
- [Qualified endpoint and session tests](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/unit_tests/tests/ignition_injection/test_blended_airmass.cpp)
- [Cranking, wall-model, and cut-recovery tests](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/unit_tests/tests/test_tunerstudio.cpp)
- [Final unreleased firmware notes](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/CHANGELOG.md?plain=1)
