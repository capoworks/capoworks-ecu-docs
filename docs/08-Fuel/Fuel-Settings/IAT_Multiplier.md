# Intake Air Temperature Fuel Multiplier

Open **Fuel > IAT multiplier** to edit the running-fuel intake-air correction.
The X axis is IAT in °C and the Y axis is a dimensionless multiplier. The ECU
interpolates this curve at the current IAT and includes the result in total
running-fuel correction. `1.0` is neutral; values above or below it add or
remove modeled fuel. If the IAT sensor is invalid, the lookup returns `1.0`.

The reset IAT curve is flat at `1.0`, using 10 °C-spaced breakpoints from
-40 °C upward. That makes neutral the default rather than an implied hot- or
cold-air correction. Start by validating the [IAT sensor](/Sensors-And-Gauges/Temperature-Sensors/IAT)
and comparing stable-load behavior with [Charge Temperature Estimation](/Advanced-Features/Fuel-Related/Charge-Temp-Estimation),
which is the dedicated air-temperature model for air-mass calculation. This
multiplier is an additional running-fuel term; changing both without
understanding the interaction can compensate the same temperature effect
twice.

Use the **Fuel: IAT correction** channel to confirm the curve output. Diagnose
sensor wiring, calibration, and heat soak before changing the multiplier, and
make changes from repeatable steady-state points. This table does not replace
injector dead time, fuel-pressure compensation, coolant enrichment, or
closed-loop fuel correction. It also does not directly alter cranking fuel.

## Sources

- [IAT correction lookup and sensor fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L815)
- [Neutral IAT default-curve initialization](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine_configuration.cpp#L193)
- [IAT correction tests and curve evaluation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_fuel_map.cpp#L35)
- [IAT curve units and range](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1589)
