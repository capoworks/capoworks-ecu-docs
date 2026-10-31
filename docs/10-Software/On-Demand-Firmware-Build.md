# On-Demand Firmware Build

Capoworks ECU offers two ways to build a firmware image for one board with a chosen set of optional
modules and calibration table dimensions: the public on-demand firmware builder and a manual GitHub
Actions workflow, **Custom firmware build**. Both are build conveniences: neither flashes an ECU, and
a successful build is not engine or hardware validation.

## Public on-demand firmware builder

The public builder is available at [capoworks.undo.it/firmware](https://capoworks.undo.it/firmware).
Sign in to your account, select a supported board, and choose any opt-in modules and table dimensions
before starting the build. When the build completes, download the matching firmware image and the
generated TunerStudio INI. Each user can run up to six builds per day.

The builder applies the same module catalog, dimension rules, and resource gate described on this
page. Treat the downloaded firmware image and its generated INI as one matching pair, and do not pair
an image with an INI from another board or build.

## Manual workflow request inputs

The **Custom firmware build** workflow takes nine inputs:

| Input | Required | Allowed values | Description |
| --- | --- | --- | --- |
| `request_id` | Yes | Letters, digits, `_`, and `-` | Opaque identifier used in the run name. |
| `source_ref` | No | Raw branch name; default `master` | Firmware source branch to build. Must be a plain branch name, not a `refs/...` path. |
| `source_sha` | No | Empty, or a full 40-character lowercase commit SHA | Exact firmware source commit to build. When set, it takes precedence over `source_ref`. |
| `board` | Yes | One ID from the list below | Board target for the build. |
| `features` | No | Comma-separated opt-in module tokens | Optional modules to add to the base profile. Leave empty for the base profile only. |
| `ve_rpm_count` | No | `16` or `32`; default `16` | RPM points in both the Speed Density and Alpha-N VE tables. The VE load dimension remains 16 points. |
| `airmass_blend_size` | No | `8` or `16`; default `8` | Size of both axes in the SD + Alpha-N authority table. |
| `cylinder_trim_count` | No | `1` through `12`; default `6` | Number of cylinder-trim tables when `cylinder_fuel_trim` is selected. It is ignored and recorded as zero when that module is absent. |
| `engine_presets` | No | Blank for automatic selection, `all`, `none`, or whitespace-separated `engine_type_e` symbols | Engine-specific preset code to expose. Omit the `engine_type_e::` prefix from symbols. |

Omitted dimension inputs use their defaults; explicitly empty or unsupported values are rejected by
the canonical profile resolver. A `32`-point VE RPM axis does not enlarge the shared 16-point lambda,
MAP-estimate, or injection-phase axes.

Under the default `ve_rpm_count=16` and `airmass_blend_size=8` dimensions, a blank `engine_presets`
selects all presets. If either dimension is expanded, a blank value selects no engine-specific presets
and `none` is also valid. Expanded builds reject `all` and every explicit symbol list; symbol lists
must use exact enum names such as `PROTEUS_BMW_M73` separated by whitespace, without mixing `all` or
`none` with other tokens. Expanded tables and a larger trim count also increase calibration size, so
a board's build or resource gate may reject the profile.

Selectable boards:

```text
hellen72 hellen-nb1 hellenNA8_96 hellenNA6 hellen128 mre_f4 mre_f7 proteus_f4 proteus_f7 proteus_h7 stm32f429_nucleo f407-discovery atlas core8
```

## Module profile

The build always includes these base modules:

```text
fan fuel_pump gear_detector tachometer trip_odometer map_averaging
```

These opt-in modules may be requested in `features`:

```text
hella_opst boost engine_sniffer lua emp_pump shock_preload cylinder_fuel_trim
```

Tokens must be exact, lowercase module names separated by commas with no empty or duplicate tokens.
Base modules are mandatory and must not be requested. Unknown, unavailable, or unsupported modules
are rejected before the build starts. The resolved module list is shown in the run summary and
recorded in the build manifest.

### Boost control

See the [Boost Control guide](/Basic-Features/Boost-Control/). The optional `boost` module adds the
boost-control code. Overboost fuel cut is a shared protection and remains available without this
module, so configure and verify a safe cut before tuning solenoid control. A usable build still needs
a calibrated boost source, an assigned control output, and a safe target for the specific hardware.

### Engine sniffer

See [Diagnostic and High Speed Logger](/Basic-Features/Data-Logging/#diagnostic-and-high-speed-logger)
for the logging workflow. The optional `engine_sniffer` module adds the event recorder used for trigger,
injection, and ignition traces. The binary tooth logger and shared RPM threshold remain available
without it. Recording is gated by **Engine Sniffer Threshold** RPM, so choose a threshold that covers
the event being investigated.

### Lua scripting

See the [Lua Scripting guide](/Advanced-Features/Lua-Scripting/). The optional `lua` module adds the
Lua interpreter, stored-script support, and control hooks on supported boards. Lua is unavailable on
`hellen128`, and an explicit `lua` request for that board is rejected. Heap and flash capacity vary by
board; use the firmware and generated INI from the same build.

### Cylinder fuel trim

The optional `cylinder_fuel_trim` module adds one persistent 16x16 fuel-factor table per configured
cylinder. Every table shares the same RPM and load axes. Each cylinder selects its own load coordinate
from **Model default**, measured MAP, TPS, accelerator pedal, cylinder filling, or effective MAP.
Because the axes are shared, cylinders using coordinates with different units require common
breakpoints suitable for the whole mix; changing a cylinder's load source does not retune the axes.

Set `cylinder_trim_count` from 1 through 12 when this module is selected; the default is 6. Whenever
injection is enabled, the count must cover the configured engine cylinder count, so an 8- or
12-cylinder engine needs a count at least that high. The count controls the number of tables and
TunerStudio rows but does not change the global 12-cylinder maximum. Enabling, disabling, or changing
the count changes the persistent configuration layout, and no automatic tune migration is provided.
Use the matching generated INI to preserve or transfer values. See
[Build-time module profiles](../../build-modules/#module-owned-inputs) for the current module details.

If the count is smaller than the default firing order needs, a fresh ECU on the generic
`MINIMAL_PINS` defaults now starts with injection disabled so the default configuration still passes
validation. Explicitly selecting a larger engine preset is not covered by that safety net and still
fails validation until the build capacity is large enough. See
[Cylinder Model Fuel Trim](/Fuel/Fuel-Settings/Cylinder-Fuel-Trim/) for the runtime behavior.

### Hella OPS-T

See the [Hella OPS+T guide](/Sensors-And-Gauges/Oil-Pressure/Hella-OPS-T/) for wiring and calibration.
The optional `hella_opst` module adds a combined oil-pressure and oil-temperature provider. Generic
oil sensor paths remain available without it. The sensor requires one EXTI-capable digital input and
must be assigned as **Hella OPS+T input**. The driver claims only channels that do not already have a
provider, so an existing pressure or temperature assignment takes priority.

### EMP coolant pump

The optional `emp_pump` module adds the EMP CAN coolant-pump protocol, configuration, tables, and
status handling. It requires the base `fan` module because cooling demand is derived from the fan
controller states. Runtime `enableEmpPump` defaults to disabled, so selecting the module does not start
the pump. The CAN bus, pump configuration, and runtime enable must be set deliberately. See
[Build-time module profiles](../../build-modules/#module-owned-inputs) for module ownership and generated
inputs.

### Shock preload

The optional `shock_preload` module adds the shock-preload controller on CAN2. It is accepted only on
`core8`, `atlas`, `proteus_f4`, `proteus_f7`, and `proteus_h7`, and CAN read and write must both be
enabled. Runtime `enableShockPreload` defaults to disabled, so a build selection does not activate the
module. See [Build-time module profiles](../../build-modules/#module-owned-inputs) for the CAN2 integration
boundary.

## Build behavior

The manual workflow first checks out the trusted builder tooling from the workflow revision, then
checks out the selected firmware source. The builder scripts, catalog, and resource policies therefore
come from the trusted tooling revision, not from the branch being built. The workflow installs the
build dependencies and runs the repository's own compile script for the selected board. It then
verifies that the firmware image was produced, checks the generated module profile, extracts resource
evidence, and gates the package against the active board policy.

`source_ref` selects a branch and defaults to `master`. `source_sha` selects an exact commit and takes
precedence over `source_ref` when both are set. The branch name must be a plain branch name; values
that start with `refs/`, start with `-`, contain control characters, or are otherwise not a valid Git
branch name are rejected before the build starts. A `source_sha` must be a full 40-character lowercase
commit SHA, and the checked-out HEAD must match it or the run fails with a source revision mismatch.

Building a branch or commit other than `master` means the firmware source may not match the builder
tooling revision. The resource gate and packaging checks still run, but a successful build does not
establish that the branch has been validated on any board, engine, or wiring setup. Use the local
build instructions in [Build-time module profiles](../../build-modules/) when you need a profile the
workflow does not accept.

## Artifacts

A successful manual run uploads an artifact named `custom-firmware-<board>` containing:

| File | Purpose |
| --- | --- |
| `fome.bin` | Firmware image. |
| `fome_update.srec` | Application update artifact, when the build produces one. |
| `fome_<board>.ini` | Matching TunerStudio definition, when the build produces one. |
| `manifest.json` | Requested and resolved profile, source branch and commit, run identifiers, and SHA-256 and size for each file. |

Artifacts are retained for 14 days. Download them before they expire.

## Limits and safety

- Treat the firmware image and its generated INI as one matching pair. Do not pair an image with an INI from another board or build.
- The manifest records the source branch, source commit, and file hashes for traceability; it is not a cryptographic authenticity guarantee.
- Neither the public builder nor the manual workflow flashes an ECU. Flashing remains a separate, deliberate operation.
- A successful build does not establish that the firmware has been validated on a particular board, engine, sensor, or wiring setup.
- The public builder allows up to six builds per user per day.
