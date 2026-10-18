# Alpha-N Strategy

Alpha-N in Capoworks ECU calculates cylinder air mass from RPM, throttle
position (TPS), air temperature and a dedicated Alpha-N filling table. It is
useful where TPS is a more reliable load indication than MAP, such as some
individual-throttle-body or high-overlap-camshaft installations.

## How Alpha-N works

Select **Fuel strategy > Alpha-N** in **Base Engine > Base Engine Settings**.
Open **Fuel > Alpha-N filling** to tune the 16x16 TPS/RPM table.

The table value is Alpha-N cylinder filling at the configured reference
pressure and selected air temperature. It is not a Speed Density VE percentage
and it is not a fuel pulse width. The firmware combines that filling with
engine displacement and temperature to calculate cylinder air mass before the
normal fuel corrections are applied.

TPS and RPM breakpoints must be finite, non-negative and strictly increasing.
The TPS axis must remain within `0` to `100`, and the RPM axis must end at or
below `18000` RPM. Duplicate adjacent breakpoints are invalid. The supplied
table values are initialization data, not a validated calibration.

## Air-mass policies

Use **Fuel > Air mass model settings** to choose the temperature and pressure
behavior:

- **Air temperature source** selects **Tcharge** or **IAT**.
- **Standalone Alpha-N: multiply MAP** makes standalone Alpha-N use effective
  MAP as the pressure in its cylinder-air-mass calculation instead of the
  reference pressure. Configure a usable measured MAP source or, when enabled,
  the MAP estimate policy.
- **Alpha-N barometric compensation** corrects the pressure calculation with
  measured BARO relative to the calibration reference. Its **Alpha-N
  calibration reference pressure** must match the pressure used when the
  filling table was produced.

If the separate idle VE table is enabled, configure **Idle VE load source** for
the idle overlay. The choices are model default, measured MAP, TPS, or
effective MAP. For model default, Alpha-N uses TPS.

## Combining Alpha-N with Speed Density

Use **Fuel strategy > SD + Alpha-N** when both models should contribute. Its
authority table mixes their calculated cylinder air masses: `0%` uses Speed
Density only and `100%` uses Alpha-N only. The authority table can be indexed
by TPS or by strictly valid measured MAP.

The separate **VE blend tables** do not select between SD and Alpha-N and do
not perform this air-mass blend. See
[SD + Alpha-N Air Mass Blending](/Fuel/Fuel-Algorithms/Blended) for the current
menu, policies, fallback behavior, diagnostics and manual tune-transfer
requirements.

## Firmware and tune compatibility

Use the matching generated TunerStudio INI for the installed Capoworks
firmware. The current air-mass layout uses flash data version `20032`; older
binary tunes are not migrated automatically. Back up the old tune, transfer
values manually with the matching generated INI, and recreate former 4x4
cylinder fuel trims in the appropriate SD or Alpha-N 16x16 model family.
