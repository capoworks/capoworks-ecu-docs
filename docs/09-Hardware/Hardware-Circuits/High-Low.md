# High-Low Driver Circuits

High-side, low-side, push-pull, and H-bridge describe current paths, not
interchangeable output-pin names. A high-side switch connects a load to the
positive supply; a low-side switch connects it to ground. Either can turn a
single-ended load on and off, while the opposite end of the load remains tied
to its supply rail.

A push-pull output actively drives high or low. With one switch terminal per
load it can sink or source current, but it is not necessarily a reversible
motor bridge. An H-bridge has two controlled legs and can reverse current
through a motor. Before treating a pair of outputs as a bridge, verify that the
installed board contains the complete bridge, not two unrelated drivers.

Inductive loads also need a defined recirculation path when the switch turns
off. Some smart outputs integrate the clamp; others require an external diode
or suppressor. Switching frequency, continuous current, peak current, thermal
capacity, and PWM suitability are properties of the actual driver and board
revision. Output labels alone do not establish them.

Capoworks operates the selected output through its board pin map and output
mode. `default` and `default inverted` configure an MCU-style push-pull pin;
open-collector modes are also available. A controller command therefore says
nothing about the downstream power stage. For DC motors, the `DcMotor` interface
accepts signed duty and expects an H-bridge-shaped interface. Its two control
schemes are PWM on the direction pins or PWM on an enable pin with binary
direction pins. Each motor channel exposes control, direction, and optional
disable assignments, but only board-routed, PWM-capable pins are valid.

Check the exact board and revision before assigning pins or fitting a load.
Use the board schematic to identify the switch topology, clamp, and enabled
outputs, then select a matching Capoworks pin mode and motor mode. See
[Highside Driver Circuits](/Hardware/Hardware-Circuits/Highsides),
[Lowside Driver Circuits](/Hardware/Hardware-Circuits/Lowsides), and the
[Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout)
when that revision applies.

## Sources

- [High-, low-, push-pull, and half-bridge output descriptions](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/drivers/gpio/tle8888.cpp#L16)
- [DC motor and H-bridge control interface](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/system/dc_motor.h#L58)
- [PWM-enable and PWM-direction pin initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/dc_motors.cpp#L12)
- [Signed motor-output tests in both control modes](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/actuators/test_dc_motor.cpp#L56)
