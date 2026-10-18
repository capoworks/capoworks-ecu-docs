# Fuel Pressure Compensation

Capoworks converts modeled cylinder fuel mass to injector pulse time using the
injector flow at **Injector reference pressure** in kPa. That reference is the
pressure at which the configured flow was measured. Pressure compensation
calculates the injector's differential pressure, then applies:

`flow ratio = sqrt(actual differential pressure / reference pressure)`

The resulting ratio scales the injector flow rate and, on the primary injector,
both slopes of the Ford small-pulse model. Use the injector supplier's rated
pressure only when the corresponding flow data is for those same injectors and
fuel conditions.

Open **Fuel > Injection configuration** and select **Injector flow
compensation mode**. **None** is for a manifold-referenced regulator and
returns a flow ratio of `1.0`. **Fixed rail pressure** represents a regulator
referenced to atmosphere and uses `reference pressure + baro − MAP`.
**Sensed Rail Pressure** uses the selected low or high fuel-pressure sensor.
For a sensed sensor, **Absolute** uses `rail − MAP`, **Gauge** uses `rail +
baro − MAP`, and **Differential** uses the sensor value directly because it
already measures the pressure across the injector.

Configure and verify the sensor first; see
[Fuel Pressure Sensors](/Sensors-And-Gauges/Fuel-Sensors/Fuel-Pressure).
An invalid or out-of-range baro value is replaced by `101.325 kPa`. A missing
or invalid MAP prevents differential pressure in the absolute/gauge sensed
paths, while fixed mode substitutes `101.325 kPa` for invalid MAP.
Compensation returns a neutral `1.0` flow ratio when the configured reference
is below 50 kPa, differential pressure is unavailable, or differential
pressure is zero or negative. P0090 is raised only when compensation is set to
a sensed rail pressure but no fuel-pressure sensor is configured; a configured
sensor that later becomes invalid falls back without P0090. Log
**fuel: Injector pressure delta** and **fuel: Injector pressure ratio** and
reconcile them with a reference gauge.

## Sources

- [Differential-pressure equations and missing-sensor warning](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L67)
- [Reference validation, square-root flow ratio and neutral fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L118)
- [Injector flow and compensation dialog fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2861)
- [Pressure-mode and flow-ratio tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_injector_model.cpp#L153)
