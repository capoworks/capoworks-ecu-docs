# Discrete VR Sensor Inputs

A variable-reluctance (VR) sensor produces an alternating signal whose
amplitude changes with speed and gap. Its raw two-wire waveform is not a logic
signal and should not be connected directly to an MCU trigger pin. A
conditioner converts the positive and negative crossings into defined logic
edges. Zero-crossing, threshold, filtering, and protection circuitry are
board-revision details.

Some Capoworks boards implement a discrete threshold input. The firmware's
`vrThreshold` settings select, for each channel, a board-supported PWM pin and
an RPM-indexed threshold-voltage curve. Because VR amplitude rises with speed,
this table can command a higher threshold at higher RPM. The controller maps
the requested threshold to a PWM duty cycle, using a 3.3 V default or a
board-defined supply voltage. It does not measure or condition the VR waveform
itself.

The conditioned output still enters the normal trigger path: select the crank
or cam input supported by that board, then configure trigger decode and
polarity to match the conditioner. Board pull-up options are not universal;
for example, AlphaX applies configured pull-ups around its discrete VR input.
Only enable those options where the installed revision provides them.

Before first crank, verify the exact board revision, sensor polarity, trigger
pin, and conditioner schematic. If RPM remains zero, observe the raw sensor at
the conditioner, then the conditioned MCU-side edge. Move the threshold curve
only within the conditioner's documented range. A signal present at the sensor
but absent after conditioning points to the threshold, polarity, supply, or
conditioner circuit, not trigger decoding. Use the
[Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout)
only when that revision matches the installed hardware.

## Sources

- [Discrete VR threshold-to-PWM controller](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/vr_pwm.cpp#L13)
- [VR and Hall board configuration fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L918)
- [AlphaX-discrete VR pull-up application](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/hellen/alphax-4chan/board_configuration.cpp#L124)
- [Conditioned trigger edge capture](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/digital_input/trigger/trigger_input_exti.cpp#L43)
