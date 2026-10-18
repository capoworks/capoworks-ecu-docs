# Brake position and pressure sensing

In this firmware revision, the brake input is a digital pedal-switch state. **Brake pedal switch** selects a `switch_input_pin_e`; **Brake pedal switch inverted** corrects the active level, and **Brake pedal switch mode** selects the input pull configuration ([brake input fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3387)). The default mode is a pull-up input ([default configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine_configuration.cpp#L204)).

Open **Sensors > Misc sensors** to configure it. The state appears as **Brake switch** and in datalogs. Lua scripts can read it with `getDigital(2)`. When the configured pin is valid it has priority; otherwise, selected BMW E90 or MK 100 UHP CAN decoding can supply a fresh brake state, and Lua's `setBrakePedalState` is the final fallback ([input priority](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine.cpp#L144), [CAN timeout](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/can/can_vss.cpp#L223)).

## Limitation and alternative

There is no dedicated proportional brake-position or brake-pressure input channel in this revision; generic analog inputs remain available. The title's “pressure sensing” must not be read as built-in analog brake-pressure support. For an external pressure transducer, use **Sensors > Aux sensors > Aux Linear Sensor 1** or **2** and configure its voltage-to-pressure endpoints. Those channels can be logged and can serve as a General Purpose PWM axis; use a Lua script if additional control logic is required. They do not automatically become a safety or brake-control input.

## Wiring and diagnostics

Wire the brake switch to a board-supported digital input, or use the documented CAN source. Use the switch or vehicle manufacturer's circuit details for polarity and supply; input protection and pin location belong to the selected board revision. The [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) documents six digital inputs for that board only.

Watch the **Brake switch** indicator while pressing and releasing the pedal. If it is reversed, change **inverted** before changing wiring. There is no dedicated brake-switch DTC for this input, so an incorrect state must be found from the indicator, log, and Lua value.

## Sources

- [Brake input fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3387)
- [Brake state selection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine.cpp#L144)
- [Supported CAN brake decoders](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/can/can_vss.cpp#L178)
- [Auxiliary linear inputs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L20)
