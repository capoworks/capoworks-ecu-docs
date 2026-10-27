# Knock Control

Knock control retards ignition timing when the knock sensor reports combustion
knock, then reapplies timing gradually once knock stops. Capoworks ECU uses the
configured maximum retard table to bound how much timing can be removed at the
current operating point.

## Maximum knock retard table

The **Max knock retard** table is a 6 x 6 table of allowed retard in degrees.
Its Y axis is selected by **Maximum retard table** under
**Ignition > Knock table load sources**, and its X axis is engine speed.

As of flash data version `20033`, the load bins are 16-bit values that accept
`0` to `1000` with no fixed percent unit. This lets a pressure-based load axis
distinguish boost pressures above `250 kPa`. Loads above the final bin clamp to
the final table row, so the last row also acts as the high-load ceiling.

Because the bins are no longer percent-only, check the unit shown on the table
axis before entering breakpoints. A table calibrated in percent must be
re-expressed in the units of the selected load source.

## Tune migration

The 16-bit load bins change the tune layout, and the flash data version is now
`20033`. Older binary tunes reset when loaded by this firmware. Before
flashing, record the maximum knock retard table and both of its axes, then
recreate them with the TunerStudio INI generated for the installed firmware.
Binary migration is not provided.

## Validation status

The high-pressure load-bin behavior is covered by unit tests, including loads
of `350 kPa` and `750 kPa`. It has not been validated on an engine or on
physical knock hardware.

## Sources

- [Knock retard load-bin definition and flash data version](https://github.com/capoworks/capoworks-ecu/blob/45627ba30adf3f7ac015c51b92924a3fbf26714f/firmware/integration/fome_config.txt)
- [High-pressure load-bin unit test](https://github.com/capoworks/capoworks-ecu/blob/45627ba30adf3f7ac015c51b92924a3fbf26714f/unit_tests/tests/test_knock.cpp)
- [Firmware changelog entry](https://github.com/capoworks/capoworks-ecu/blob/45627ba30adf3f7ac015c51b92924a3fbf26714f/firmware/CHANGELOG.md?plain=1)
