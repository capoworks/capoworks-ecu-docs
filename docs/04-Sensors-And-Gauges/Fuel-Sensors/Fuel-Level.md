# Fuel Level Sensing

The fuel-level input converts an analog sender voltage into a percentage with an eight-point calibration curve. In TunerStudio, open **Sensors > Fuel level sensor**, assign **Input channel**, and edit the **Fuel Level** voltage-to-percentage curve ([fuel-level dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3402)). The curve voltage points must be ascending.

The sensor subscribes to the ADC with a 2 Hz low-pass filter and has a 500 ms timeout ([sensor initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fuel_level.cpp#L16)). This smoothing reduces sender and fuel-motion noise but also makes the displayed level respond slowly.

## Calibration

Use the vehicle manufacturer's sender curve, or obtain voltage-versus-level points from a safe bench sweep of the sender with a board-compatible interface. Enter monotonic voltage bins and the corresponding percentages, including useful intermediate points if the tank shape is nonlinear. Verify that the curve is not extrapolating a flat or reversed section. Do not use the analog temperature input circuit as an assumed fuel-sender interface unless the board documentation confirms that its bias circuit is suitable.

## Diagnostics and wiring

Compare **Fuel level** with **Raw fuel level**. A raw voltage that remains sensible while percentage is wrong points to the curve; a missing or stuck raw voltage points to the sender, supply, ground, input channel, or board interface. The status channel uses `getOrZero`, so a timed-out sensor can appear as 0% rather than as an explicit error ([status publication](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/status_loop.cpp#L292)).

This revision has no fuel-level entry in the normal Sensor Checker list, so a 0% display is not by itself proof of an empty tank. Select the input from the exact board target. For a Universal 112 v1.2, use one of the documented analog-voltage pins in the [revision-specific pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout/).

## Sources

- [Fuel-level dialog and curve](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3402)
- [Fuel-level sensor setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fuel_level.cpp#L16)
- [Fuel-level output channel](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/console/status_loop.cpp#L292)
- [Eight-point table definition](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L179)
