# Engine calibration overview

Engine calibration teaches Capoworks how much air each cylinder receives, how
much fuel to add, and when to fire the spark. A calibration is not a set of
generic values to copy between engines: sensor scaling, fuel composition,
injectors, intake and exhaust hardware, combustion chamber, and operating
conditions all affect the result.

## Fuel and air mass

Start with valid airflow information. Capoworks can derive cylinder air mass
from [Speed Density](/Fuel/Fuel-Algorithms/SD), [Alpha-N](/Fuel/Fuel-Algorithms/AlphaN),
[MAF Air Charge](/Fuel/Fuel-Algorithms/MAF), or the supported blended method.
The selected model must match the sensors and intake system actually fitted;
see [Airmass Models and Migration](/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration).

The fuel calculation combines cylinder air mass with the target lambda table
and the configured stoichiometric ratio. Lambda expresses mixture relative to
stoichiometry, while gasoline-scale AFR is a display convention derived from
that ratio. Read [Air Fuel Ratio](/Fundamentals-Of-Tuning/AFR) and
[AFR Setting](/Fuel/Fuel-Settings/AFR-setting) before changing either view.

## Ignition and knock

Ignition timing controls when combustion pressure is produced. The useful
advance at a given speed and load must be found by measurement, not assumed
from another engine. Read [Ignition Timing, MBT and Combustion](/Fundamentals-Of-Tuning/Spark)
and use the [Ignition Advance Table](/Ignition/Ignition-Settings/Ignition-Advance-Table)
to describe the configured curve.

Knock is abnormal combustion that can damage the engine. Detecting it requires
a valid sensor/input path, suitable per-cylinder assignment, and a threshold
that distinguishes noise from knock. The [Knock Detection Setup Guide](/Advanced-Features/Knock-Control)
documents those dependencies and the retard response.

## Transients and validation

Steady-state calibration is the foundation. Throttle changes also alter fuel
film on port walls, sensor response, and air delivery, so verify
[Acceleration Compensation](/Fundamentals-Of-Tuning/Acceleration-Compensation)
and [Wall Wetting](/Fuel/Acceleration/Wall-Wetting) after the base fuel and
ignition behaviour are repeatable. Change one factor at a time, log the
evidence, and recheck limits and protections after every calibration change.

## Sources

- [Airmass-to-lambda-to-fuel calculation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/fuel_computer.cpp#L55)
- [Knock detection and retard response](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/knock_controller.cpp#L44)
- [Wall-wetting adjustment of fuel mass](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/fuel_schedule.cpp#L117)
