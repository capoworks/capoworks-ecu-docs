# Board-protected settings in TunerStudio

Some settings are fixed by your ECU board. The firmware restores these values after every TunerStudio write, so editing them would cause configuration CRC errors. Capoworks ECU marks these settings as protected in TunerStudio.

## What you will see

- Fixed settings are read-only and their controls are disabled in every dialog that shows them, including pinout and feature dialogs.
- When you load a tune, TunerStudio keeps the ECU's values for protected settings instead of the values from the file.
- Free pins and settings that are not board-fixed remain editable as usual.

## Revision-dependent settings

Some settings are fixed only on certain hardware revisions of a board. For these, the control is disabled only on the revisions where the value is fixed. On a revision where the setting is free, configure it through its dialog after importing a tune.

TunerStudio cannot identify the board revision while offline, so connect to the ECU before configuring these settings.

## Notes

These protections do not change configuration offsets or the communication protocol. If a setting appears greyed out, it is enforced by your board and cannot be changed from TunerStudio.
