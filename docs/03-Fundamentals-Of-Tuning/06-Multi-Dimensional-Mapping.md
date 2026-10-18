# Multi-Dimensional Mapping

A conventional fuel or ignition table has two axes, RPM and load. The table output is a VE value or ignition angle. A multi-dimensional blend adds one more input: a selected operating signal controls how much of a second correction table is applied at each point in the base map.

Capoworks firmware exposes four VE blends and four ignition blends. The current source lists `IGN_BLEND_COUNT` and `VE_BLEND_COUNT` as four each in
[`fome_config_shared.txt`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config_shared.txt#L31).
Each blend has a source, an RPM versus load correction table, and a bias curve that converts the selected source into a percentage. The source might be ethanol content, intake temperature, TPS, battery voltage, a Lua gauge, or another supported channel.

The correction is neutral where either the correction table or bias curve is zero. VE blends are percentage corrections and stack multiplicatively. Ignition blends are timing offsets measured in degrees and stack by addition. These are not substitutes for choosing a fuel strategy or blending Speed Density with Alpha-N.

## Choosing an input

Available source choices are defined in the
[`gppwm_channel_e` enum](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L296).
They include throttle, MAP, coolant and intake temperatures, fuel and ignition load, auxiliary temperatures and linear inputs, accelerator pedal, electrical voltage, VVT positions, ethanol percentage, GPPWM outputs, Lua gauges, RPM, detected gear, barometric pressure, EGT, vehicle speed, oil pressure and temperature, and air-conditioning state. `Zero` disables a blend.

Use a source that is valid and meaningful throughout the region where the overlay is needed. A sensor that is merely present is not enough: its units must match the bias breakpoints, and its fault behavior must be acceptable.

## A practical workflow

1. Build and validate the base fuel or ignition table first.
2. Select one blend source and keep the other blends disabled.
3. Define the source-to-percentage bias curve. Neutral regions should normally command `0%`.
4. Fill the correction table in the correct units: percent for VE, degrees for ignition.
5. Confirm the live parameter, bias and output diagnostics before enabling another overlay.
6. Add further blends one at a time when their interactions are understood.

The formulas, exact axes, fault behavior, stacking rules and diagnostics are documented in [Advanced Multi-Dimensional Mapping](/Advanced-Features/Multi-Dimensional-Mapping). For the separate Speed Density plus Alpha-N fuel strategy, see [SD + Alpha-N Air Mass Blending](/Fuel/Fuel-Algorithms/Blended).
