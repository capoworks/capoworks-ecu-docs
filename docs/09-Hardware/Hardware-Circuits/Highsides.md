# Highside Driver Circuits

A high-side output switches the positive side of a load. When enabled, the
driver connects the output to its supply; the load's return remains connected
to ground. This differs from a low-side output, which switches the return path.
Do not infer that a connector labelled as a high side can be grounded as if it
were a low side.

An inductive load stores energy while current flows. When a high-side device
turns off, the current needs a controlled recirculation path. The driver may
contain an internal clamp, while another board may depend on an external
freewheel diode or suppressor. Verify that path in the exact board schematic.
Also verify the driver's permitted supply, continuous and peak current, PWM
frequency, and diagnostics before selecting a load. Those are device and
revision facts, not Capoworks settings.

In Capoworks, choose an output exposed by the installed board target and assign
it to the required function. The board pin map names high-side, low-side,
ignition, and generic outputs; the firmware does not create a high-side power
stage from an MCU pin. Output-mode settings can invert the command or select an
open-collector-style pin, but they do not change the external topology.
Controllers publish a requested state or duty cycle, and the board output
stages perform the switching.

For commissioning, confirm the chosen output and mode, command a safe
no-load state, and check the corresponding output command and board supply
path. If a small pilot device works but the intended inductive load does not,
stop and inspect the clamp and driver rating rather than increasing duty.
Repeated driver faults or unexpected turn-off spikes may indicate a missing or
incorrect recirculation path. Grounds, connector pin numbers, and protection
components must come from the matching revision documentation. The
[Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas) and
[Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112)
pages describe only their documented boards.

## Sources

- [High-side and push-pull output-stage definitions](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/drivers/gpio/tle8888.cpp#L16)
- [High-side mode selection in the output update path](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/drivers/gpio/tle8888.cpp#L422)
- [Configured output-state translation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L290)
- [Output pin electrical-mode initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/system/efi_gpio.cpp#L585)
