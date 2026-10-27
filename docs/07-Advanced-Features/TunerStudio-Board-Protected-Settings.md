# Board-protected settings in TunerStudio

Some settings are fixed by your ECU board. The firmware restores these values after every TunerStudio write, so editing them would cause configuration CRC errors. Capoworks ECU marks these settings as protected in TunerStudio.

## What you will see

- Fixed settings are read-only and their controls are disabled in every dialog that shows them, including pinout and feature dialogs.
- Protected settings retain the connected ECU's values when a tune is loaded.
- Free pins and settings that are not board-fixed remain editable as usual.

## Tune import and revision-dependent settings

Some settings are fixed only on certain hardware revisions of a board. On revisions where such a setting is free, TunerStudio still keeps the connected ECU's value when importing a tune because the protection rule uses controller priority on all revisions. The value from the imported tune is not applied to that field.

After importing a tune, connect to the ECU and configure a free revision-dependent setting through its dialog. TunerStudio cannot identify the board revision while offline, so the control's availability may depend on the connection and the connected board revision.

## Battery-divider calibration

Boards with a fixed battery-voltage divider expose an opt-in **Override battery divider coefficient (advanced)** checkbox. With it off, the board applies its fixed divider and the coefficient field is not editable. Enable it only for the rare case that requires manual calibration while connected; clearing it restores the board's nominal coefficient. The coefficient uses controller priority, so a tune import keeps the ECU value even when the checkbox is enabled. Edit the coefficient after connecting to change it. See [Battery Settings](/Sensors-And-Gauges/Driver-Controls-And-Feedback/Battery-Settings) for the calibration procedure and tune migration.

## Notes

These protections do not change configuration offsets or the communication protocol. A fixed setting cannot be edited from TunerStudio. For a revision-dependent setting, whether it can be edited depends on the connected hardware and revision. Some UI controls can be disabled for other reasons, so a greyed-out control alone does not necessarily mean that the board has fixed the setting.
