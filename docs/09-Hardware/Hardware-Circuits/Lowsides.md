# Lowside Driver Circuits

A low-side output switches the ground-side return of a load while the load's
other terminal remains at its positive supply. When enabled, the output sinks
current to ground; when disabled, it removes that path. A relay coil, solenoid,
or injector therefore needs both a correctly rated positive feed and a
low-side driver.

Turning off an inductive low-side load interrupts stored current. The voltage
rise must be clamped by a diode or suppressor, either within an intelligent
driver or on the board. Clamp placement matters because it determines where
recirculating current flows. Verify that the selected output actually has the
required clamp, especially before moving a load from a documented flywheel-
protected output to a general-purpose one. Supply voltage, current capacity,
PWM frequency, diagnostic behaviour, and protection are board- and
driver-specific.

Capoworks selects the output through its board pin map and commands a state or
duty cycle. The `default` output mode configures an MCU-style push-pull pin;
open-collector modes are also supported. For a smart low-side driver, the
driver controls the power stage and may expose diagnostics. For a direct MCU
logic output, an external driver is still required. Choosing a low-side label
does not establish that the pin can drive a load directly.

Before connection, locate the exact output on the matching board revision,
confirm the load supply and return, and identify the clamp and fuse. Then
select the matching Capoworks output, polarity, and PWM settings. If a command
changes but the load does not, check the output mode, board driver enable,
supply, and load return before changing tuning. If switching causes faults or
spikes, stop and verify the clamp rather than adding duty. The
[Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout)
identifies its revision-specific protected outputs; do not transfer those pin
or protection details to another revision.

## Sources

- [Low-side and clamp-oriented output descriptions](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/drivers/gpio/tle8888.cpp#L21)
- [Open-drain and push-pull electrical setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/system/efi_gpio.cpp#L585)
- [Available output polarity modes](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L290)
- [Driver output-register update path](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/drivers/gpio/tle8888.cpp#L442)
