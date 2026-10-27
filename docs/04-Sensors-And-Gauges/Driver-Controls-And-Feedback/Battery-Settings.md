# Battery Settings

The battery-voltage input provides the ECU's measured supply voltage. It is used by gauges, logging, injector dead-time compensation, dwell correction, actuator voltage compensation, and other voltage-sensitive calculations.

## Configuration

Open **Base Engine > Battery and alternator > Battery Settings**. **vBatt ADC input** selects the processor channel. **Override battery divider coefficient (advanced)** controls whether the manual **Battery Input Divider Coefficient** is used ([battery dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4287)). The firmware applies the coefficient, a 20 Hz filter, and a 100 ms timeout to the registered battery-voltage sensor ([sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_vbatt.cpp#L11)).

## Divider override

On boards with a fixed battery-voltage divider, the override checkbox defaults off. With it off, the board applies its nominal divider coefficient and the coefficient field is not editable. Enable the override only for the rare case that requires manual calibration against a voltmeter; clearing it restores the board's nominal coefficient. On boards without a firmware-provided nominal, the checkbox only controls whether the manual coefficient is editable.

When the override is enabled, a coefficient that is not finite or is outside `0.01` to `99.0` falls back to the board nominal. The coefficient uses controller priority, so a tune import keeps the connected ECU's value even when the override is enabled. Edit the coefficient after connecting to change it.

Stop the engine before changing this setting. Divider changes apply after a Burn with the engine stopped, or after saving and rebooting.

## Calibrate against a trusted meter

Compare the meter reading with **VBatt** while the ECU and its sensor supply are powered as they will be in service, then adjust the coefficient until they agree. **Raw Battery** shows the ADC voltage before the coefficient is applied. This distinction helps separate a scaling error from a low actual supply.

## Wiring and diagnostics

Use the board's dedicated battery-sense divider and the input named by that board target. Do not connect battery voltage directly to an arbitrary analog input. The divider is board hardware, not a firmware setting. Verify the exact connector and revision in your hardware documentation; the [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) applies to that revision only.

Compare **VBatt** with the meter at idle and with electrical loads applied. A stable raw value that does not scale correctly points to the coefficient; a changing or absent raw value points to sensing supply, wiring, or the ADC channel. This revision has no dedicated battery-sensor code in the normal Sensor Checker list, so do not expect a battery-voltage DTC to identify a calibration mistake ([checked inputs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L617)).

Alternator **Target** is separate from battery sensing and appears only when alternator control is enabled.

## Tune migration

The divider override advances the stored tune version to `20034`. Back up the tune and transfer values using matching TunerStudio definitions from the older schema; existing field offsets are unchanged, but binary migration is not provided.

## Sources

- [Battery and alternator dialogs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4287)
- [Battery sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_vbatt.cpp#L11)
- [Battery divider field description](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L514)
- [Divider override enforcement and fallback](https://github.com/capoworks/capoworks-ecu/blob/b0e5bf850e65cd427f7537ae719352d166be908a/firmware/controllers/algo/engine_configuration.cpp)
- [Override field and flash data version](https://github.com/capoworks/capoworks-ecu/blob/b0e5bf850e65cd427f7537ae719352d166be908a/firmware/integration/fome_config.txt)
