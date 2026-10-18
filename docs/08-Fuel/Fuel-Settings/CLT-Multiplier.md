# Coolant Temperature Multiplier

Open **Fuel > CLT multiplier** to edit the running-fuel coolant correction.
The X axis is coolant temperature in °C and the Y axis is a dimensionless fuel
mass multiplier. The ECU interpolates the curve from the current CLT value and
multiplies running fuel by it. A value of `1.0` is neutral, above `1.0` adds
fuel, and below `1.0` removes fuel. If the CLT sensor is invalid, this
correction returns `1.0`; correct the sensor fault rather than tuning around it.

This is a running-fuel correction. It is multiplied with the IAT multiplier,
barometric correction, post-cranking correction, and any enabled antilag or
launch-control fuel coefficient. Cranking has separate **Fuel CLT multiplier**
and flex-fuel cranking curves, so do not use this page expecting it to alter
cranking fuel.

The neutral table is flat at `1.0`. A reset Capoworks configuration does not
start there: its default CLT curve contains progressively larger cold
enrichment and reaches unity at normal operating temperature. Preserve a valid
default as a starting point, then correct it only from stable operating points
and measured lambda after the coolant sensor, air-mass model, injector data,
and fuel pressure are known-good. Compare the **Fuel: CLT correction** channel
with the curve input when diagnosing a mismatch. Changes to coolant
thermistor calibration can shift both the lookup coordinate and the engine's
real warm-up behavior; recheck the [CLT sensor](/Sensors-And-Gauges/Temperature-Sensors/CLT)
before editing this table.

## Sources

- [Running CLT correction lookup and sensor fallback](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L802)
- [Running correction multiplication](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L133)
- [Default coolant-enrichment curve](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/defaults/default_fuel.cpp#L34)
- [CLT curve units and range](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1586)
