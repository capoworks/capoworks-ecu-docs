# High Pressure Fuel Pump

Capoworks ECU controls a camshaft-driven, constant-displacement high-pressure pump whose
electronically controlled valve sets the delivered fraction of each stroke. This is not a
generic pump-output table and does not make every GDI pump compatible.

`EFI_HPFP` is enabled in the STM32F4 feature defaults, inherited by F7/H7, and may be disabled by
a board target such as the small CAN board. Pump menus require a nonzero lobe count. Match the
board's valve output, protection, rail-pressure input and connector to the exact board revision.

## Pump, cam and stroke configuration

Set **Number of lobes**, the VVT-driven intake or exhaust cam source, and **Angle of first lobe**.
Successive peaks are spaced around the 720-degree cycle and include the selected VVT position.
Set **Pump volume** from actual chamber displacement. Required fuel per cycle becomes a percentage
of that displacement; the lobe profile converts it to activation angle.

Valve setup includes **Valve Pin**, **Valve Pin Mode**, peak and hold current, hold-off time,
maximum hold time, minimum and activation angles, and battery-voltage dead time. These are
hardware-specific. Use pump/valve data and measured current and pressure response; there are no
safe generic calibration values.

## Rail feedback and scheduling

The pressure loop requires a valid **Fuel Pressure High** sensor. Without one, the proportional
and integral contribution is zero. The RPM/load target, limited by a configured decay rate, is
compared with measured high pressure. The valve opens at the next lobe peak minus requested angle
and dead time, then closes after dead time plus activation angle. Below the minimum angle it skips
that opening and advances to the next lobe.

The controller is inactive below 60 RPM or when lobe count, pump volume, target load or valve pin
is invalid. A production build requires more than six trigger teeth per pump lobe. On engine stop,
future scheduling is cancelled, but an already armed close still runs.

## Diagnostics

Log `HPFP duration`, fuel-requested percentage, PI contribution, `isHpfpInactive`, `noValve`,
`angleAboveMin`, `di_nextStart` and rail pressure. Verify cam phase and pressure feedback before
changing gains. Unit tests cover lobe angle, PI, scheduling and stop/restart behavior; they do not
validate a pump, rail, driver or wiring installation.

## Source references

- [HPFP feature block, lobe timing, feedback and valve scheduling](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/high_pressure_fuel_pump.cpp#L34-L235)
- [Configuration fields and units](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1296-L1314)
- [TunerStudio pump and target configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L5263-L5283)
- [HPFP scheduling unit tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/test_hpfp.cpp#L343-L366)
