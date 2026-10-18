# Power Supply and References

Capoworks ECU boards normally accept a protected vehicle supply and derive
their own processor, I/O, and sensor rails. The exact input connector, fuse or
main-relay path, reverse-polarity protection, transient protection, regulator
topology, and current budget differ by board and revision. There is no
universal input-voltage or current rating to reuse across revisions.

The main relay may switch the ECU's run supply. On some boards firmware controls
that relay; on others the relay is handled outside the normal output map. The
microRusEFI configuration, for example, documents a battery-sense input fed
from the main relay while the relay itself is controlled by its TLE8888. Do
not assign a main-relay output merely because a connector has a similar label.

The analog sensor reference is also board hardware. Firmware's `adcVcc` is a
measurement-conversion scale, not permission to power a sensor from any nearby
pin. Dedicated sensor 5 V supplies may be loaded by several sensors, so use the
board revision's supply limit. Boards that monitor the 5 V rail register a
`Sensor5vVoltage` channel; the sensor checker reports a fault outside its
implemented window. Header or rail measurements, divider factors, and ADC
channels remain revision-specific.

Keep high-current power returns and sensitive sensor-return paths distinct
unless the board schematic explicitly joins them. A good battery-voltage
reading does not prove the analog reference or a remote sensor ground is
correct. During diagnosis, compare battery voltage, the monitored sensor
supply, and raw ADC/divider information for the same channel. If readings move
together with load current, investigate the ground or supply path rather than
recalibrating the sensor. Consult the [Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas)
or [Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112)
page only when its identity matches the installed board.

## Sources

- [microRusEFI battery divider, ADC scale, and main-relay-fed sense input](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/microrusefi/board_configuration.cpp#L52)
- [Board-monitored 5 V supply in the sensor checker](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/sensor_checker.cpp#L542)
- [Atlas power-rail and sensor-supply monitoring setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/atlas/board_configuration.cpp#L194)
- [ADC supply-scale validation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine_configuration.cpp#L848)
