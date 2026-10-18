# AFR Setting

Capoworks fuel control uses a target lambda table, not an independent AFR
controller. The **Target Gas-Scale AFR** table is an alternate editor over the
same stored table. The runtime loads a target lambda, calculates
`target AFR = target lambda × stoichiometric ratio`, and converts cylinder air
mass to fuel mass using that AFR. Editing either table view changes that shared
target; keep one view selected while tuning.

Set **Stoichiometric ratio** for the primary fuel. When a flex-fuel sensor is
configured, the ECU linearly interpolates between this E0 value and **E100
stoichiometric ratio** using ethanol percentage. A valid live reading is used
first; after a sensor dropout, the last valid percentage in backup RAM is used.
The configured **Failed flex sensor ethanol content** is used only when no valid
reading has ever been stored. Thus flex composition changes the lambda-to-AFR
conversion and fuel mass, while a given lambda target remains a lambda target.

The wideband sensor measures lambda. Analog wideband calibration endpoints in
TunerStudio are gasoline-scale AFR values and are divided by 14.7 to obtain
lambda. The **Air/Fuel Ratio** log channel is measured lambda multiplied by the
active stoichiometric ratio, while **Air/Fuel Ratio (Gas Scale)** always uses
14.7. Neither a table entry nor a wideband reading guarantees the engine
actually reaches target: validate the air-mass model, injector characterization,
fuel pressure, sensor response, and the relevant closed-loop or protection
settings.

After calibration, log **Fuel: target lambda**, **Fuel: target AFR**,
**Fuel: Stoich ratio**, **Lambda 1**, and both AFR channels while holding steady
load points. See [Wideband Oxygen Sensor](/Sensors-And-Gauges/Fuel-Sensors/Wideband)
and [Target table load sources](/Advanced-Features/Override-Table-Axis).

## Sources

- [AFR calculation, target publication and flex stoichiometry](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/fuel_computer.cpp#L55)
- [Stored lambda/AFR target-table union](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1643)
- [Analog wideband AFR-to-lambda conversion](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_lambda.cpp#L69)
- [Flex-fuel and calculation tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_fuel_computer.cpp#L18)
