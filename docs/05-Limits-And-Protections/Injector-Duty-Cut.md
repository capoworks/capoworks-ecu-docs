# Injector Duty Cycle Cut

This feature cuts the injectors in the case that a set duty cycle is exceeded temporarily or for a sustained period. Setting this up can prevent injector damage in the case that the fuel map is asking too much from the injectors.Most injectors shouldn't exceed a duty cycle of ~85-90% temporarily or ~75-85% sustained. The sustained duty cycle delay can be set at ~0.5-1 second as a safe starting point.

## Staged injection

When staged injection is enabled, Capoworks ECU also checks the secondary (stage 2) injector duty cycle. The higher of the primary and stage 2 duty cycles is compared against both the instantaneous and sustained limits, so a stage 2 excursion can trigger the cut even when the primary stage looks safe.

After a cut, fuel resumes only once both active stages fall below 20 percent duty. This forces the driver to lift off the pedal before injection returns.

If staged injection is disabled, only the primary injector duty cycle is checked.

Set the duty limits so they are safe for both injector stages, and confirm the staged injection setting matches the hardware before relying on this protection. The behavior is covered by unit tests but has not been validated on a running engine.
