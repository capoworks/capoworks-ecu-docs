# Rev Counter/Tachometer

The tachometer feature is an ECU output that generates a pulse train for an external rev counter. It does not read a tachometer signal. Configure it under **Base Engine > Outputs > Tachometer output** ([output menu](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4091)).

## Configuration

Set **Output** and **Output mode**, then choose whether **Pulse duration** is a constant high time or a duty-cycle value with **Pulse Mode**. **Pulse per Rev** tells the firmware how many tachometer periods one engine revolution represents ([tach dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4077)). The implementation calculates output frequency as engine RPM multiplied by pulses per revolution and divided by 60. It rejects a pulse-per-revolution value of zero or greater than ten and reports `CUSTOM_ERR_6709` ([frequency calculation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/tachometer/tachometer.cpp#L35)).

Use the gauge manufacturer's documented input and pulse convention. Test first with ignition/engine operation and verify indicated RPM through the useful range. Do not infer the pulse count from cylinder count alone when an adapter, coil driver, or OEM instrument changes the signal.

## Wiring and diagnostics

Connect the configured output to the tachometer input through the electrical interface required by that instrument and your board revision. Use an inverted or open-collector mode only where the output circuit and tachometer input support it. Some boards expose a tachometer pull-up option under **Controller > Fancy Hardware**; it is board-target dependent ([board settings](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L5113)).

If the gauge does not move, confirm the output pin is valid, the selected polarity is correct, the tachometer has the supply/ground/pull-up path it requires, and the configured pulses per revolution match the instrument. The optional startup sweep is a useful output test because it runs from the tachometer module at ignition-on when configured ([startup sweep](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/tachometer/tachometer.cpp#L89)).

## Sources

- [Tachometer output dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4077)
- [Tachometer frequency generation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/modules/tachometer/tachometer.cpp#L29)
- [Board pull-up setting](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L901)
