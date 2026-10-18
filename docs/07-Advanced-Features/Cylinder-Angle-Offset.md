# Cylinder Angle Offset Configuration

This firmware has three unrelated angle controls. Use each for one purpose:

| Control | Purpose | Runtime effect |
| --- | --- | --- |
| `globalTriggerAngleOffset` | Calibrate the trigger's synchronization point to TDC | Shifts the complete trigger-to-engine phase |
| `timing_offset_cylinder[]` | Correct unequal firing intervals or mechanical phase | Shifts an individual cylinder's event angle |
| `ignTrims[]` | Correct combustion timing between cylinders | Adds BTDC ignition advance per cylinder |

## Mechanical cylinder phase

Open **Ignition > Cylinder offsets**. Despite the menu's wording,
`timing_offset_cylinder[cylinder]` is not added to the ignition table's advance.
`OneCylinder::getAngleOffset()` returns:

`engineCycle * firingOrderIndex / cylinderCount + timing_offset_cylinder`

The firing-order index is the cylinder's position in the configured order.
Positive offsets move the scheduled event later; negative offsets move it
earlier, matching the TunerStudio note that positive retards and negative
advances. The offset is consumed when computing injection opening angle,
primary spark angle, per-cylinder MAP sampling start, and instantaneous-RPM
measurement position. It therefore describes where events occur in the engine
cycle, not how much advance is commanded.

A nonzero offset also marks the engine as odd fire. Unless the engine is
two-stroke or `pairedOddFireWastedSpark` is enabled, wasted-spark mode can use
the odd-fire +360-degree re-fire path. Do not use this field to trim a
cylinder's combustion advance.

## Global trigger and advance controls

`TriggerCentral::toEngPhase()` converts trigger phase with
`trgPhase.angle - triggerShape.tdcPosition - globalTriggerAngleOffset +
m_phaseAdjustment`; `toTrgPhase()` performs the reverse conversion by adding
the TDC position and global offset. The global offset is therefore subtracted
on trigger-to-engine conversion, not universally added as a positive phase
shift. It moves every cylinder together and cannot correct unequal firing
intervals. Establish this value with all per-cylinder offsets zero.

Normal ignition-table advance is a BTDC target. `getCylinderIgnitionTrim()`
reads each cylinder's `ignTrims` table, then firmware calculates
`untrimmedAdvance + ignitionTrim`. A positive trim therefore increases advance;
a negative trim reduces advance. This sign is opposite the Cylinder offsets
menu's positive-retards convention.

## Setup and diagnostics

Start with zero cylinder offsets and trims, fixed timing enabled, and verify
trigger phase with a timing light. Then set mechanical offsets from the actual
firing geometry, and use ignition trims only for small combustion-timing
corrections. **Ign: Timing Cyl** (`ignitionAdvanceCyl`) reports final primary
advance after the timing clamp but before the mechanical angle offset, so use
event/trigger diagnostics to verify phase. An angle-range assertion can
identify offsets that move an event outside the valid engine cycle.

## Sources

- [Cylinder-offset configuration and sign note](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1157)
- [Firing-order base offset and odd-fire detection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/math/engine_math.cpp#L151)
- [Global trigger-to-engine phase conversion](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_central.cpp#L36)
- [Per-cylinder ignition-trim addition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine2.cpp#L254)
