# Boost pressure limit  

Boost pressure limit can be found under __Base Engine > Limits and fallbacks__.

![image](Boost-Cut/BoostCutPressure.png)

## Boost cut pressure

This setting defines the upper limit of pressure the engine will operate within. If the engine's MAP reading exceeds the value configured in __Boost cut pressure__, Capoworks ECU will cut fuel injection until the MAP reading falls 20kPa below the configured value. The 20kPa hysteresis value is hard-coded.

This value is absolute pressure, so if an engine is running 7 PSIG of boost pressure (~148kPa absolute), this value would need to be set above 150kPa. It is a good idea to allow enough of a margin to prevent unnecessary boost cut on small excursions above the target boost pressure.

Set this value to 0 to disable the boost cut limit.

## Missing or invalid MAP readings

Boost cut needs a valid MAP reading to change state. A missing MAP sensor, an invalid reading, or a non-finite value is treated as neither rising nor falling:

- It cannot start a new boost cut.
- If a boost cut is already active, fuel stays cut until a valid MAP reading falls 20kPa below the configured value.

This keeps the protection engaged if the MAP signal drops out under boost. If fuel stays cut after boost pressure has fallen, check the MAP sensor wiring, the MAP input assignment, and the MAP diagnostics before assuming the boost cut setting is wrong.
