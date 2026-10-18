# Injection Phase Settings

The **Injection phase** table selects the crank angle at which fuel delivery is
targeted. Configure which part of the pulse the table controls with
`injectionTimingMode`: **Start of injection**, **Center of injection**, or **End
of injection**. Select the table's load coordinate with
`injectionPhaseLoadSource`; RPM remains the other axis. The map uses
`injectionPhase`, `injPhaseRpmBins`, and `injPhaseLoadBins`.

The scheduling code defines the table angle in degrees after combustion TDC. It
wraps the configured value into engine-cycle coordinates, so negative table
values are valid but should not be described generically as BTDC or ATDC without
accounting for that wrap. For **Start**, the table value is used without duration
correction. For **Center**, opening is advanced by half the pulse duration. For
**End**, opening is advanced by the full duration so the pulse ends at the table
angle. The actual opening angle is derived from the selected point and current
injection duration.

Sequential mode computes one scheduled event for each cylinder and fires that
cylinder's output. Batch mode uses the same per-cylinder phase calculation, but
each event's output mask also includes the injector half the cylinder count away
in firing order. This is pattern-dependent angular spacing, not necessarily 360
crank degrees. Thus batch is not a separate fixed timing rule: its individual
events retain the phase schedule while paired outputs are driven by the expanded
mask. This is why the physical wiring and the selected injection mode must be
checked together.

Before editing the table, confirm engine phase sync, firing order, injection
mode, output wiring, and the intended controlled point. Log RPM, the selected
load coordinate, injection duration, and injection timing while moving through a
steady operating point. Changing duration can move the opening angle even when
the table value and timing mode stay fixed. The table controls fuel scheduling
and does not set ignition timing.

## Source references

- [Timing-mode names and configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1049-L1050)
- [Phase table fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1608-L1610)
- [Angle convention and start/center/end correction](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/fuel_schedule.cpp#L291-L352)
- [Sequential and batch output masks](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/fuel_schedule.cpp#L69-L98)
