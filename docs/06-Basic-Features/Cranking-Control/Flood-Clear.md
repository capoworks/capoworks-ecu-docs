# Flood clear

Flood clear can cut fuel during starting so that a flooded engine can be cleared by holding the accelerator down. It is configured under **Cranking > Advanced** in TunerStudio.

## Enabling flood clear

Enable **Enable flood clear**. Flood clear is requested only when this setting is enabled and the driver throttle intent is strictly greater than 90%; at exactly 90% or below, it is not requested. If `DriverThrottleIntent` is unavailable, the firmware treats it as 0 for this check, so a missing throttle intent does not request flood clear.

## Flood clear mode

When flood clear is requested, **Flood clear mode** selects how the fuel cut behaves according to engine state:

- **Roadside** (default): fuel is cut only while the engine is cranking. Fuel is restored as soon as the engine reaches running RPM, which is the normal behavior if accidental combustion pushes the engine above the cranking RPM threshold.
- **Service / Workshop**: a request made while the engine is not running latches the fuel cut. The latch remains active through the cranking-to-running transition until the accelerator is released. This lets the starter be used to build oil pressure without enabling injection, even if the engine catches.

## Latch behavior in Service / Workshop mode

The workshop latch is armed only while the engine is stopped or cranking, so selecting this mode cannot cut fuel on an already-running engine. The latch is released when any of the following happens:

- the accelerator is released (driver throttle intent falls to or below 90%);
- flood clear is disabled;
- the mode is changed back to Roadside.

After the latch is released, it is not re-armed while the engine is still running.
