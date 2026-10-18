# Fuel Pressure Sensors

The firmware provides separate low-pressure and high-pressure fuel sensor inputs. Both use a two-point linear calibration: raw voltage against known pressure at each endpoint ([fluid-pressure initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L35)). Open **Sensors > Fuel pressure** and assign **Fuel low pressure ADC input** or **Fuel high pressure ADC input**, then enter their voltage and pressure points ([fuel-pressure dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3655)).

Use the sensor datasheet or a trusted pressure reference. A reversed sensor is supported by entering its endpoints in the corresponding order. Verify **Raw Low Fuel Pressure** and the scaled low-pressure gauge first. High pressure is configured the same way but is displayed in bar; the HPFP controller consumes the high-pressure channel in kPa for closed-loop target control ([HPFP feedback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/high_pressure_fuel_pump.cpp#L97)).

## Rail-pressure selection

In **Fuel > Injection configuration**, **Fuel rail pressure sensor** selects which sensor represents injector pressure, and injector compensation can be set to sensed rail pressure. **Sensor type** in the fuel-pressure dialog distinguishes **Absolute**, **Gauge**, and **Differential** for the low-pressure/injector differential calculation. Absolute requires MAP. Gauge requires MAP plus barometric pressure, but a missing or out-of-range baro value is substituted with 101.325 kPa; differential is already a pressure difference ([injector pressure math](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L67)).

## Wiring and diagnostics

The signal must use a board-supported analog input and the supply, ground, and interface required by the sensor. Do not assume that a generic analog pin accepts the transducer without board-level signal conditioning. Confirm the exact connector and revision from the board documentation.

The low-pressure input uses a 10 Hz filter; the high-pressure input uses 100 Hz. P0090 is emitted only when injector compensation is set to use a sensed rail pressure but the chosen fuel-pressure sensor has not been configured. If a configured sensor returns an invalid reading, the differential-pressure calculation returns no value and injector compensation falls back to 1.0 without that warning ([missing-sensor warning](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L81), [flow-ratio fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L118)). This revision does not map either fuel-pressure sensor to the normal value-based Sensor Checker DTC set; inspect raw voltage, scaled pressure, sensor supply, and calibration directly.

## Sources

- [Fuel-pressure dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3655)
- [Linear pressure sensor setup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_fluid_pressure.cpp#L35)
- [Injector differential-pressure calculation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L67)
- [HPFP pressure feedback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/high_pressure_fuel_pump.cpp#L97)
