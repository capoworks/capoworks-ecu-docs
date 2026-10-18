# Rotary engine specific settings

The current **Rotary** menu is a trailing-spark feature, not an engine preset.
It enables a secondary ignition event after each configured primary event.
Leading ignition still uses the normal ignition outputs, firing order, advance
table, dwell table, and trigger configuration.

## Configure leading and trailing sparks

1. Configure the primary trigger, engine cycle, firing order, and leading
   ignition outputs. Verify the leading timing and phase first.
2. In **Rotary**, enable **Enable Trailing Sparks** and assign the trailing
   outputs. The current TunerStudio dialog exposes trailing pins 1 through 4.
3. Calibrate the 8 x 8 **Trailing spark advance** table. Its RPM and load axes
   are independent, and `trailingSparkLoadSource` selects the load coordinate
   used by `engineState.trailingSparkAngle`.

`trailingIgnitionTable` is the angular delay after the main event, not a
separate total BTDC advance. For each main ignition event, the firmware loads
that offset and schedules charging and firing on the matching trailing output.
The trailing dwell is the main event's dwell snapshot. The primary
`minimumIgnitionTiming` and `maximumIgnitionTiming` clamp does not clamp the
trailing angle.

## Firing-order and paired-output cautions

The rotary menu does not derive rotor count, leading/trailing pairing, trigger
phase, or output assignment. A two-rotor tune represented by two primary
events therefore needs both leading events and their corresponding trailing
outputs configured explicitly; this page makes no universal claim about other
rotary arrangements.

`pairedOddFireWastedSpark` is a generic shared-coil option. In Wasted Spark
mode it drives one output for a companion pair from both cylinder events and
suppresses the separate +360-degree odd-fire re-fire path. It is not a rotary
leading/trailing switch and does not create trailing outputs.

## Checks and limits

Verify rising/falling edge and polarity on each leading and trailing output,
then confirm that only the intended coil fires. If trailing spark is absent,
check `enableTrailingSparks`, the trailing output, the selected table coordinate,
and a valid, finite load. Confirm the table axes are ascending. Experimental
ignition cycle-profile and time-budget planners change primary ignition timing
conversion; they do not replace the trailing-angle path. Coil dwell, coil
capacity, and safe trailing timing require hardware validation.

## Sources

- [Trailing-spark feature enable](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L415)
- [Trailing table, axes, and load-source declaration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1627)
- [Trailing-angle lookup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine2.cpp#L457)
- [Trailing charge and fire scheduling](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/spark_logic.cpp#L437)
