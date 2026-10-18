# Analogue Input Settings

The pinned Capoworks build applies two scaling stages to analogue inputs that use the default ADC-subscription scaling: the MCU ADC reference converts ADC counts to pin volts, then the board divider converts pin volts to external sensor volts. A subscriber can override the second stage. Battery sensing explicitly passes an ADC-to-input factor of `1.0f` and applies `vbattDividerCoeff` in its own `LinearFunc`; the ADC subscription substitutes the board divider only when a subscriber passes `0`. These are calibration factors, not the sensor's own transfer function.

## ADC V-Ref

**ADC vRef voltage** (`adcVcc`) is the firmware's assumed full-scale MCU reference. Core8 fixes it to 3.3 V and exposes it read-only in TunerStudio. Verify it with a known stable input: if raw ADC volts track the measured reference but reconstructed input volts do not, investigate the divider instead of increasing `adcVcc`. Do not infer a safe input rating from the processor family or from another board.

## Analogue Divider

**Analog divider ratio** compensates the board's resistor network. Core8 declares a 1.56 ratio for its 5.6 kΩ/10 kΩ network and also locks the value. Battery sensing uses the separate `vbattDividerCoeff`; do not reuse that coefficient for generic inputs. Pinned console diagnostics report raw ADC volts, reconstructed input volts, and the applied divider, which helps separate an ADC/reference fault from incorrect board scaling. Confirm safe voltage range, divider, and connector against the exact board revision.

## Smoothing Factor

There is no general ADC smoothing factor in this INI. Filtering is software and assigned by each sensor implementation; Aux Linear inputs use a 10 Hz low-pass. Do not use smoothing to hide clipping, poor grounding, or a wrong divider. Too much filtering delays response, while too little exposes real noise. If a TunerStudio build has no smoothing field, report the sensor and installed INI rather than guessing a hidden setting.

## Sources

- [Core8 ADC reference and divider](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/core8/board_configuration.cpp#L64)
- [Battery ADC subscription and divider](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_vbatt.cpp#L19)
- [Default ADC divider substitution](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/adc/adc_subscription.cpp#L75)
- [ADC counts to MCU voltage](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/ports/stm32/stm32_adc_v4.cpp#L266)
- [ADC input-voltage diagnostics](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/adc/adc_subscription.cpp#L163)
- [Aux Linear filter bandwidth](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L32)
