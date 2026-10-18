# Battery Settings

The battery-voltage input provides the ECU's measured supply voltage. It is used by gauges, logging, injector dead-time compensation, dwell correction, actuator voltage compensation, and other voltage-sensitive calculations.

## Configuration

Open **Base Engine > Battery and alternator > Battery Settings**. **vBatt ADC input** selects the processor channel and **Battery Input Divider Coefficient** scales the divided ADC voltage back to battery voltage ([battery dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4287)). The firmware applies the coefficient, a 20 Hz filter, and a 100 ms timeout to the registered battery-voltage sensor ([sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_vbatt.cpp#L11)).

Calibrate against a trusted meter. Compare the meter reading with **VBatt** while the ECU and its sensor supply are powered as they will be in service, then adjust the coefficient until they agree. **Raw Battery** shows the ADC voltage before the coefficient is applied. This distinction helps separate a scaling error from a low actual supply.

## Wiring and diagnostics

Use the board's dedicated battery-sense divider and the input named by that board target. Do not connect battery voltage directly to an arbitrary analog input. The divider is board hardware, not a firmware setting. Verify the exact connector and revision in your hardware documentation; the [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) applies to that revision only.

Compare **VBatt** with the meter at idle and with electrical loads applied. A stable raw value that does not scale correctly points to the coefficient; a changing or absent raw value points to sensing supply, wiring, or the ADC channel. This revision has no dedicated battery-sensor code in the normal Sensor Checker list, so do not expect a battery-voltage DTC to identify a calibration mistake ([checked inputs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L617)).

Alternator **Target** is separate from battery sensing and appears only when alternator control is enabled.

## Sources

- [Battery and alternator dialogs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4287)
- [Battery sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_vbatt.cpp#L11)
- [Battery divider field description](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L514)
