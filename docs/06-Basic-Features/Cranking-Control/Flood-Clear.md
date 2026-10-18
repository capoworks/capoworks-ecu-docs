# Flood clear

Flood clear cuts fuel while the engine is cranking so that a flooded engine can be cleared by holding the accelerator down. It is configured under **Cranking > Advanced** in TunerStudio.

## Enabling flood clear

Enable **Enable flood clear**. When enabled, no fuel is injected while the driver throttle intent is held above 90%.

## Flood clear mode

When flood clear is enabled, **Flood clear mode** selects how the fuel cut behaves through the cranking-to-running transition:

- **Roadside** (default): fuel is restored as soon as the engine reaches running RPM. This is the normal behavior if accidental combustion pushes the engine above the cranking RPM threshold.
- **Service / Workshop**: the fuel cut is latched until the accelerator is released. This lets the starter be used to build oil pressure without enabling injection, even if the engine catches.

## Latch behavior in Service / Workshop mode

The workshop latch is armed only while the engine is stopped or cranking, so selecting this mode cannot cut fuel on an already-running engine. The latch is released when any of the following happens:

- the accelerator is released (driver throttle intent falls to or below 90%);
- flood clear is disabled;
- the mode is changed back to Roadside.

After the latch is released, it is not re-armed while the engine is still running.
