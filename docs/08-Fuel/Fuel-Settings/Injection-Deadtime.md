# Fuel Injector Dead Time Settings

Injector dead time is the pulse-time offset added after the calculated fuel
pulse. The primary and secondary injector curves each map battery voltage in
volts to dead time in milliseconds. The ECU linearly interpolates the active
curve from measured battery voltage, clamps the calculated fuel pulse to the
configured minimum, then adds dead time. Zero fuel mass still produces a zero
pulse. This dead-time curve is battery-sensitive; the current implementation
does not add a separate pressure axis or rescale dead time from injector
pressure compensation.

Use measured data for the exact injector part and electrical driver at the
injector's physical differential pressure and the vehicle's voltage range. Do
not combine a flow rating from one pressure with a latency curve from another,
and do not transfer a curve merely because two injectors share a flow rating.
Pressure compensation scales injector flow by `sqrt(actual differential
pressure / reference pressure)` but obtains dead time only from the battery
curve ([Fuel Pressure Compensation](/Limits-And-Protections/Fuel-Pressure-Compensation)).

Configure injector flow and its units, the injector reference pressure, the
voltage/dead-time curve, and **Minimum pulse width (pre-deadtime)** together.
The shipped Bosch example curve is a default illustration, not a universal
recommendation for another injector. Validate dead time at low pulse widths,
where its contribution is largest, and use **Fuel: injector lag**, actual
battery voltage, pulse width, and measured lambda. Nonlinear correction is
supported on the primary bank only; see
[Injector configuration](/Fuel/Injectors/Injector-configuration) and
[Small Pulse](/Fuel/Fuel-Settings/Small-Pulse) before combining the two.

## Sources

- [Battery-voltage dead-time lookup](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L155)
- [Minimum-pulse and dead-time calculation order](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L162)
- [Injector flow, curve and minimum-pulse fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L396)
- [Dead-time interpolation tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_injector_model.cpp#L127)
