# Fuel Injection Mode

Injection mode determines which injector outputs fire and how many pulses carry
each cylinder's fuel. Configure running operation with `injectionMode` and
cranking separately with `crankingInjectionMode`; TunerStudio shows the running
choice as **Fuel > Injection configuration > Mode**.

**Simultaneous** strikes all injector outputs together. The scheduler divides the
cylinder's cycle fuel among the cylinder count, so the channel duration is
shorter, and each injector is scheduled cylinder-count times per engine cycle.
**Sequential** strikes one configured injector per cylinder, once per cycle, and
requires unique outputs plus enough engine-phase information to identify the
cycle. **Batch** fires each injector twice per cycle and uses half the sequential
pulse mass per event. Its output mask combines that cylinder's injector with the
injector half the firing order away, so a paired-wire output can be driven twice
while separately wired outputs still receive the batch schedule.

`Single Point` is also present in the current enum. It uses the common
single-point injector while preserving the cycle-fuel accounting used by the
other modes.

The effective running mode can differ from the configured mode. If sequential is
selected but phase is not synchronized and the trigger system expects to resolve
it later, the current mode temporarily falls back to batch. Starting also uses
`crankingInjectionMode`, so check `currentInjectionMode` rather than assuming the
configured value is active.

Before changing mode, verify firing order, injector output assignments, and
whether outputs are individually wired or shared. Do not change wiring solely
from an enum name. Use injector pulse width and duty-cycle diagnostics to confirm
that the mass split matches the physical arrangement; mode changes alter pulse
duration even when the requested cycle fuel is unchanged.

## Source references

- [Mode names and configuration fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L476-L479)
- [Pulse count and duration multipliers](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/fuel_math.cpp#L712-L758)
- [Sequential, batch, and simultaneous output masks](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/engine_cycle/fuel_schedule.cpp#L69-L98)
- [Cranking and phase-dependent effective mode](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/algo/engine.cpp#L430-L453)
