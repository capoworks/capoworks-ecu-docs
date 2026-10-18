# AUX Sensor Inputs

Capoworks exposes four linear analogue AUX sensors and two frequency AUX inputs. Each linear sensor has an ADC channel plus low/high voltage and output-value points, so it can represent pressure, position, or another monotonic quantity. The output has no unit label; record its intended unit in the tune notes.

## Aux Speed Sensor

`Aux Speed 1` and `Aux Speed 2` accept frequency and publish frequency without a pulses-per-revolution conversion. Assign board-supported event inputs, then verify a known-frequency square wave and confirm the corresponding AUX frequency gauge. Aux Speed 1 uses `auxFrequencyFilter`; Aux Speed 2 has a fixed 0.05 filter. An unsupported or edge-free input remains inactive.

## Aux linear sensor

For each linear input, select the ADC channel, then enter two datasheet points in either order. Use a high-voltage point below the board input's measured clipping limit; the INI's 10 V entry range is not a safe board rating. Compare connector voltage with raw AUX output, then use a second known point to check slope. Configured outputs range from -100000 to 100000. At initialization, the implementation sets output bounds from -5 through the larger configured endpoint; `LinearFunc::convert` rejects a mapped result outside those bounds as invalid instead of clamping it. The returned `Low` or `High` diagnostic is selected from the sign of the line's slope, so reversing the endpoint order also reverses which input-voltage side is reported.

## Aux sensor serial comms settings

The pinned INI has no generic auxiliary serial-sensor protocol selector or configurable UART frame, so this page does not prescribe RS-232, UART, or proprietary framing. Use the implemented analogue or frequency paths above, or an already-supported CAN path. The target's generated INI is authoritative for ADC and event pins. Core8, for example, lists four VR/Hall and several digital event inputs.

## Sources

- [AUX linear sensor configuration fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1325)
- [Linear AUX sensor bounds and filtering](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L44)
- [Linear out-of-range invalidation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/sensors/converters/linear_func.cpp#L16)
- [AUX frequency sensor setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_aux_speed_sensor.cpp#L20)
- [Core8 target input names](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/generated/fome_core8.ini#L89)
