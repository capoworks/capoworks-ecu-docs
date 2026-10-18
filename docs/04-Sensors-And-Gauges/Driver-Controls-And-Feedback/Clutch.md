# Clutch Position Sensing

The supported clutch inputs are digital switches, not a continuous position sensor: **Clutch Down**, **Clutch Up**, their inverted flags, and input modes ([clutch fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3380)). Configure them in **Sensors > Misc sensors**. Both default to pull-up inputs ([default modes](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine_configuration.cpp#L204)).

**Clutch Down** can activate Launch Control when its activation mode is set to clutch switch. **Clutch Up** can be used by Deceleration Fuel Cutoff: enable **Disable fuel cut on clutch** when the clutch must inhibit DFCO during a shift ([DFCO condition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/dfco.cpp#L37)). If the up-switch pin is unassigned, the state falls back to a Lua-provided value; the down switch has no equivalent built-in fallback ([switch state logic](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine.cpp#L137)).

## Wiring and calibration

Wire each switch to a board-supported digital input and select the matching input mode. A normally open switch needs a defined pull-up or pull-down path; a switch that switches supply must be matched to the input's permitted circuit. Consult the exact board or harness document rather than reusing a pin from another revision. The [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/) is specific to that board.

Calibration is polarity checking rather than a voltage curve. Watch the **Clutch: up** and **Clutch: down** indicators and toggle each switch. If a state is reversed, use the matching **inverted** setting.

## Limitation and diagnostics

There is no proportional clutch-position channel and no clutch-switch DTC in this revision. For a clutch-position gauge or another analog strategy, use an Aux Linear input and document its voltage-to-position curve. The stock switches remain the correct source for Launch Control and the built-in DFCO option. Lua can read the processed states with `getDigital(0)` and `getDigital(1)`.

## Sources

- [Clutch input fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3380)
- [Clutch state logic](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine.cpp#L137)
- [Launch-control clutch use](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/launch_control.cpp#L32)
- [DFCO clutch condition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/dfco.cpp#L37)
