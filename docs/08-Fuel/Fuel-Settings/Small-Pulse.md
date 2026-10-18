# Small Pulse Width Correction

Small-pulse correction adjusts the fuel-pulse calculation near the injector's
nonlinear low-flow region. It runs before the minimum-pulse clamp and dead-time
addition. Use supplier-measured data for the exact injector at its physical
differential pressure and voltage, then use one characterized model
consistently; do not mix polynomial coefficients, slopes, dead time, and flow
ratings measured under different conditions.

## Polynomial

Set **Small pulse correction mode** to **Polynomial** and define the pulse
threshold with **Add nonlinearity below pulse**. At or below that pulse width,
the ECU takes the uncorrected base duration `x` in milliseconds and adds:

`c0 + c1*x + c2*x^2 + ... + c7*x^7`

The eight coefficients are the **constant** through **x^7** fields. Longer
pulses bypass this correction. A supplier polynomial is only valid over its
measured pulse range; polynomial extrapolation can produce implausible pulse
widths, so move the threshold and coefficients only from measured injector
data. Dead time remains a separate battery-voltage curve.

## Ford Two-Slope Method

The **Ford (dual slope)** path models the low-flow kink with two measured
slopes. Set injector flow units to **mass flow**, enter the large-pulse slope
(AHISL) as injector flow in g/s, the small-pulse slope (ALOSL) in g/s, and the
mass breakpoint (FUEL_BKPT) in mg. Below the breakpoint, duration uses the
small slope plus a calculated joining offset; above it, duration uses the large
slope. Pressure compensation scales both slopes by the same flow ratio.

The nonlinear selector is disabled on the secondary injector bank in this
revision, even if staged injection is enabled.

## Sources

- [Nonlinear pulse calculation branches and threshold](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L183)
- [Polynomial coefficient implementation](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel/injector_model.cpp#L214)
- [Polynomial fields and dual-slope injector dialog](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2905)
- [Polynomial and dual-slope unit tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/ignition_injection/test_injector_model.cpp#L66)
