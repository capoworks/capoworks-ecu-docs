# On-Demand Firmware Build

Capoworks ECU provides a manual GitHub Actions workflow, **Custom firmware build**, that builds a
firmware image for one board with a chosen set of optional modules. It is a build convenience: it does
not flash an ECU, and a successful build is not engine or hardware validation.

## Request inputs

The workflow is started manually and takes three inputs:

| Input | Required | Description |
| --- | --- | --- |
| `request_id` | Yes | An opaque identifier used in the run name. Only letters, digits, underscores, and hyphens are accepted. |
| `board` | Yes | One board from the fixed list below. |
| `features` | No | Comma-separated opt-in module tokens. Leave empty for the base profile only. |

Selectable boards:

```text
hellen72 hellen-nb1 hellenNA8_96 hellenNA6 hellen128 mre_f4 mre_f7 proteus_f4 proteus_f7 proteus_h7 stm32f429_nucleo f407-discovery atlas core8
```

## Module profile

The workflow always includes these base modules:

```text
fan fuel_pump gear_detector tachometer trip_odometer map_averaging
```

These opt-in modules may be requested in `features`:

```text
hella_opst boost engine_sniffer lua emp_pump shock_preload cylinder_fuel_trim
```

Rules enforced before the build starts:

- Tokens must be lowercase module names separated by commas, with no empty or duplicate tokens.
- Base modules are mandatory and must not be requested; requesting one is an error.
- Unknown or unsupported tokens are an error.
- `lua` is rejected on `hellen128`.
- `shock_preload` requires CAN2 and is accepted only on `core8`, `atlas`, `proteus_f4`, `proteus_f7`, and `proteus_h7`.
- The workflow's module list must match the firmware module catalog; if the catalog changes, the workflow fails until it is updated.

The resolved module list is shown in the run summary and recorded in the build manifest.

## Build behavior

The workflow checks out the current `master` source, installs the build dependencies, and runs the
repository's own compile script for the selected board. It then verifies that the firmware image was
produced and that the modules recorded in the generated profile match the requested profile.

Because the source is always `master`, the workflow does not build an arbitrary branch or tag. Use the
local build instructions in [Build-time module profiles](../../build-modules/) when you need a specific
source revision or a profile the workflow does not accept.

## Artifacts

A successful run uploads an artifact named `custom-firmware-<board>` containing:

| File | Purpose |
| --- | --- |
| `fome.bin` | Firmware image. |
| `fome_update.srec` | Application update artifact, when the build produces one. |
| `fome_<board>.ini` | Matching TunerStudio definition, when the build produces one. |
| `manifest.json` | Requested and resolved profile, source commit, run identifiers, and SHA-256 and size for each file. |

Artifacts are retained for 14 days. Download them before they expire.

## Limits and safety

- Treat the firmware image and its generated INI as one matching pair. Do not pair an image with an INI from another board or build.
- The manifest records the source commit and file hashes for traceability; it is not a cryptographic authenticity guarantee.
- The workflow never flashes an ECU. Flashing remains a separate, deliberate operation.
- A successful build does not establish that the firmware has been validated on a particular board, engine, or wiring setup.
