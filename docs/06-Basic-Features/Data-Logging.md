# Data Logging Settings

Capoworks ECU and TunerStudio provide two complementary logs. TunerStudio
records live channels over the laptop connection; supported ECUs can also log
onboard to an SD card for later analysis.

## Basic TunerStudio logging settings

The TS logging settings can be found in the __Data Logging__ tab up the top.

### Start & Stop Logging

Logging can be started and stopped with CTRL+L & CTRL+K respectively. 

### Logging Profiles

Custom logging profiles can be configured to add or take away specific parameters. Typically the default profile is acceptable as it logs all parameters.

### Triggered Logging

Triggered logging is useful in that it allows the user to set the conditions of when a log should begin. The manual setting has the logs started and stopped by the user. The simple settings allow for logging to be started and stopped when a parameter is above, below or equal to a user-specified value e.g. start logging when CLT is above 75. Expressions are more complex but allow for a series of conditions to be used e.g. [RPM] > 6000 && [TPS] > 90 will activate when the TPS is over 90% and the RPM is over 6000.

### Data Logging Preferences

The preferences allow for the data log formatting and naming to be modified. Typically these can be left as the default settings of MLG format and naming on log start with the tune saved to the log.

### Other Settings

By pressing ALT+V, the log can be opened in MegaLogViewer for analysis.

By pressing ALT+L, the selected data log folder will be shown.

## SD card logging

At startup, the logger waits briefly for the USB stack. If a card and USB host
are present, the card is handed to USB mass storage and internal logging does
not run. Otherwise the firmware attempts to mount the card and log internally.
A missing card or mount failure produces no internal log.

### Data Rate

In TunerStudio, the polling rate can be set under
__Communications > Data Rate__. This controls how often the PC requests live
data; it does not increase the firmware's calculation rate. Use a rate that the
connection and selected channel set can sustain, and confirm the log contains
regular samples before relying on a transient capture.

### SD logging settings

The SD logging settings are found under __Controller > SD Card Logger__.
Although the INI exposes a rate up to 250 Hz, the firmware clamps the normal
logger to 1-100 Hz. Each record snapshots the output-channel space and writes
the defined log fields from that snapshot. Higher rates increase card traffic
and file size; the logger prints its field count, bytes per record, effective
rate, and calculated bytes per second at startup.

The file is synchronised every two seconds. An abrupt power loss can therefore
leave the card's directory length behind the data that was written since the
last sync. A write error or full card stops the logger and raises a warning; it
does not retry continuously.

For the __SD logger mode__, __Normal__ writes an MLG file from the configured
output channels. __Trigger__ writes a `.teeth` composite trigger log and does
not use the normal SD rate. Trigger mode generates much more event data and
uses the shared composite-logger buffer.

## Diagnostic and High speed logger

__Trigger Logger__ records primary and cam edge state for each logged tooth
event. It only records while the engine sniffer is enabled, which in turn is
gated by __Engine Sniffer Threshold__ RPM. A 250-entry buffer is published when
full, or on the next logged event after five seconds. If no buffer is ready,
TunerStudio receives an out-of-range response, not an empty sample set.

__Trigger Oscilloscope__ is different: it samples dedicated analog trigger
inputs at 8-bit resolution and is available only in builds compiled with
`TRIGGER_SCOPE`. Channel names and input pins are board-specific. Use the INI
and pinout for the exact board target rather than assuming universal channels.

At higher RPM the firmware deliberately stops adding events to the sniffer
path. Adjust __Engine Sniffer Threshold__ to cover the event being investigated;
a missing trace above that limit is not proof that the trigger stopped.

## Sources

- [SD card mount and USB mass-storage handoff](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/mmc_card_mount.cpp#L26)
- [SD logger acquisition, rate clamp, triggering, and write limits](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/binary_log/sd_file_log.cpp#L11)
- [Composite trigger buffering and five-second flush](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/binary/tooth_logger.cpp#L182)
- [TunerStudio logger definitions and data-ready conditions](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L107)
