# Lambda Protection

Lambda protection cuts fuel when the measured lambda stays outside the allowed
deviation for too long under high load. It is a protective fuel cut, not a
tuning aid: it does not correct fuelling, and it does not replace a valid
lambda sensor, fuel pressure or air-mass calibration.

Open it from **Base Engine > Limits and protection > Lambda protection**.

## Enabling and thresholds

Enable the feature with **Enable lambda protection**. The cut is armed only
while all of the following are true:

- Load is above **Check above load**.
- Throttle is above **and above TPS**.
- Engine speed is above **and above RPM**.
- Lambda has been out of range for **and after delay**.

Once fuel is cut, it is restored only when load, TPS and RPM all fall below
their restore thresholds.

## Load threshold units

**Check above load** and **Load less than** follow the coordinate chosen in
**Threshold load source**. They are not always percentages. The TunerStudio
help text now states the units for each choice:

| Threshold load source | Units for the min and restore load fields |
| --- | --- |
| `Measured MAP` | kPa |
| `Effective MAP` | kPa |
| `TPS` | percent |
| `Acc Pedal` | percent |
| `Cyl Filling %` | percent |
| `Model default` | The active fuel model's native units |

`Model default` resolves to effective MAP in kPa for Speed Density and
SD + Alpha-N, TPS in percent for standalone Alpha-N, and pre-trim cylinder
filling in percent for MAF Air Charge. See
[Load Sources](/Fuel/Fuel-Settings/Load-Sources) for the full coordinate
definitions and fallback rules.

Changing **Threshold load source** changes what the stored load numbers mean.
The values are not converted automatically, so review and retune both load
thresholds after switching between a kPa source and a percent source. The
allowed numeric range of the fields is unchanged, so no tune migration is
needed for this clarification alone.

## Deviation table

The **Lambda Difference Table** defines the allowed lambda deviation. Its own
load coordinate is chosen with **Deviation table load source**, independently
of the threshold load source. Retune its breakpoints if you change that
selector.

## Safety boundaries

- Confirm the lambda channel is valid and the sensor is healthy before relying
  on protection. A dead sensor produces no new error and cannot trigger a cut.
- Verify the selected threshold source is available; a fallback coordinate can
  make the cut arm at an unexpected load.
- Test the restore thresholds at low load before normal driving, because a cut
  that does not restore leaves the engine without fuel.

## Source references

- [Lambda protection threshold fields and load-source help text](https://github.com/capoworks/capoworks-ecu/blob/29c5db284be586200df3d5d74e00f909c19cbef4/firmware/integration/fome_config.txt)
- [Lambda protection dialog and load-source selector](https://github.com/capoworks/capoworks-ecu/blob/29c5db284be586200df3d5d74e00f909c19cbef4/firmware/tunerstudio/tunerstudio.template.ini)
- [Firmware changelog entry](https://github.com/capoworks/capoworks-ecu/blob/29c5db284be586200df3d5d74e00f909c19cbef4/firmware/CHANGELOG.md?plain=1)
