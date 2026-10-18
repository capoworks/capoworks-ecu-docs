# Fuel TPS Multiplier

**Cranking > Fuel TPS multiplier** applies a TPS-dependent multiplier to
cranking fuel. Its X axis is driver throttle intent in percent and its Y axis
is a dimensionless multiplier. Cranking fuel is calculated as base cranking
fuel × duration coefficient × coolant coefficient × TPS coefficient. A reset
curve is flat at `1.0`, so it begins neutral. If the throttle-intent sensor is
invalid, the firmware uses `1.0` instead of applying the curve.

Use this curve only if throttle opening changes the fuel needed during
cranking. Confirm the throttle input and cranking fuel source first, then use
repeated cranking observations with a stable battery supply. Do not copy a
curve from another engine: manifold filling, throttle leakage, injector size,
and starting strategy all change the result. Check the **Fuel: cranking TPS
mult** channel while cranking and verify that flood clear and other ignition-off
fuel-cut behavior still work as intended.

This setting is not an Alpha-N fuel map, VE blend, target-table load source, or
TPS acceleration enrichment. Alpha-N and VE blends change how running air mass
or modeled fuel is calculated. [TPS/TPS acceleration enrichment](/Fuel/Acceleration/TPS-Based)
adds a pulse-width-based quantity during a throttle transient. This multiplier
instead scales the cranking fuel calculation only. See
[Alpha-N filling](/Fuel/Fuel-Algorithms/AlphaN) and
[Load Sources](/Fuel/Fuel-Settings/Load-Sources) for those separate controls.

## Sources

- [Cranking TPS lookup and multiplication](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L91)
- [TPS coefficient definition and units](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1535)
- [Neutral default TPS multiplier](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/defaults/default_cranking.cpp#L34)
- [Cranking menu placement](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2274)
