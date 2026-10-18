# Ignition Modules

Use this page as an interface-matching guide, not as an endorsement list. An ignition module or
coil is suitable only when its trigger input, output device, supply, polarity, dwell requirements
and protection match the exact board revision and connector.

## Match the electrical interface

Smart coils include the igniter and expect a logic-level trigger. They must be connected to an
output rated for that logic interface. Dumb coils require an external IGBT or ignition module
capable of switching the coil primary; do not connect a coil primary directly to a 5 V logic
output or a general-purpose low-side output.

The existing board guides expose different proven interfaces. The
[Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas/) documents twelve 5 V push-pull ignition outputs,
which can drive compatible smart coils or an external IGBT for dumb coils. The
[Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112/) documents eight
logic-level ignition outputs and eight IGBT drivers with shared function but independent output
pins. Those are board capabilities, not permission to mix their connector pins or assume another
revision is identical.

## Configure the intended outputs

Enable ignition, choose **Mode**, and assign each used **Ignition cylinder** output under
**Ignition > Ignition Settings**. Set **Ignition Output Mode** to match the board circuit.
Single-coil, wasted-spark and individual-coil modes change which configured output is driven;
they do not change the electrical interface.

Configure the dwell table and voltage correction from the coil or module manufacturer's data.
The firmware calculates and schedules charge time, but it has no universal safe dwell value.

## Diagnostics and limits

Before running an engine, verify output polarity, idle level, supply and driver type with the
coil disconnected. The **Ignition > Ignition coil test** path refuses commands while the engine
is running and reports dwell accuracy and invalid-dwell warnings during normal operation, but
that is not a hardware safety interlock. Isolate ignition power and prevent fuel delivery during
bench checking.

No model name alone proves compatibility, and this page does not include a shopping list of
known-good modules. Check the module's trigger specification against the selected board output.

## Source references

- [Ignition mode to output mapping](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/spark_logic.cpp#L23-L51)
- [Ignition enable and limp-manager gate](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/spark_logic.cpp#L123-L127)
- [Dwell calculation and invalid-dwell warning](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/ignition/ignition_state.cpp#L268-L292)
- [Ignition output and mode fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2728-L2752)
