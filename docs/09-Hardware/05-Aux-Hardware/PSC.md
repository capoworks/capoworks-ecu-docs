# Power Steering Controller

At this release, the Capoworks ECU firmware does not implement a dedicated power-steering
controller. It has no steering-angle, pressure, vehicle-speed or actuator-target strategy, and no
dedicated power-steering CAN protocol or actuator channel. The **PSC** name is therefore best read
as a harness/interface topic, not as an enabled closed-loop feature.

## Switch inputs

Some board connector definitions label a pin as **Power Steering Switch** or **Steering Pressure
Switch**. That pin is a switch-status input. It can be observed and logged, but observing it does
not mean the ECU is controlling an external steering pump or valve.

For a generic input path, select the exact board pin under **Lua Digital Aux Inputs**. Set its
input mode to match the switch circuit, then read it in Lua with `getAuxDigital(index)`;
Digital #1 is index `0`. Use the exact board connector and pinout, such as the
[Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas/) or
[Universal 112 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/), and
confirm pull-up/pull-down and active polarity. See the [Lua scripting guide](/Advanced-Features/Lua-Scripting/)
for the input API.

## Output and safety limits

An external steering controller must provide its own power stage, current limiting, fault
handling and fail-safe behavior. Do not infer a dedicated controller from a connector label, and
do not use a generic logic or low-side output as a steering-motor control output without a
documented, validated external driver design. The switch input is a slow digital input, not a
high-frequency sensor.

## Diagnostics

With the engine stopped, operate the steering-pressure switch and compare its electrical state
with the selected Lua input and the logged value. If it does not change, check switch supply and
ground, polarity, input mode, connector pin, and board input protection. There is no dedicated PSC
fault code in this implementation, so a board-label match is not proof that control logic exists.

## Source references

- [Generic slow switch-input type](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L278-L286)
- [Lua auxiliary digital input implementation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/lua/lua_hooks.cpp#L306-L333)
- [TunerStudio auxiliary input selectors](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4642-L4651)
- [Example board connector labeled as a steering switch](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/hellen/hellen-nb1/connectors/main.yaml#L33-L40)
