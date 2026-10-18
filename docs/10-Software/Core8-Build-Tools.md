---
sidebar_position: 2
---

# Core8 Build Tools

The Capoworks firmware repository includes a Core8 build helper for Linux and WSL. The helper makes a
Core8 firmware build its default operation, uses the bundled ARM binutils for artifact checks, and
leaves hardware programming as a separate explicit choice.

This guide is pinned to firmware source commit
`8f4fcfb40135fe7e5f15b280f7e05d9863b60f52`, which includes the Core8 tooling change
`034ec75bc1e9bf7391eeb0050b13038c0f60e3d7`. Use the scripts and board files from the source revision
that produced your firmware.

## Prerequisites

Run the helper from a Linux or WSL checkout with:

- Git submodules initialized: `git submodule update --init`;
- Bash, `make` and a C/C++ build toolchain;
- Java 21 for the repository's configuration/build tooling;
- `gcc-multilib` and `g++-multilib`;
- `mtools`, `dosfstools`, `zip`, `xxd` and `rsync`;
- the bundled ARM toolchain at
  `firmware/ext/build-tools/arm-gnu-toolchain-11.3.rel1-x86_64-arm-none-eabi/bin`.

The helper needs the bundled `arm-none-eabi-objcopy` and `arm-none-eabi-objdump`. Their directory is
selected to match `firmware/use_arm_gcc.mk`; it must remain aligned when the bundled compiler changes.
The INI-image step also needs the host FAT tools above. The pinned script emits `RAMDISK_INVALID` on
Cygwin/MinGW and macOS, which disables the embedded INI drive. On Linux, a missing FAT tool makes that
step fail instead. Use Linux or WSL for the documented build path.

## Build Core8

From the repository root:

```bash
bash .vscode/scripts/core8_dfu.sh
```

The no-argument form is a build. The equivalent VS Code task is **Core8: Build firmware**, the default
build task. Both resolve paths from the repository and helper location rather than from fixed
drive-letter paths.

For WSL, run the command in a WSL terminal or open the repository in a VS Code WSL/Remote window.
The Core8 task invokes `bash` without a Windows-specific `wsl` override, so a task run from an ordinary
Windows terminal is not guaranteed to reach the WSL shell.

The build intentionally:

1. Cleans the firmware and bootloader outputs for `PROJECT_BOARD=core8` and
   `PROJECT_CPU=ARCH_STM32F4`.
2. Deletes shared PCH files under `firmware/pch/pch.h.gch`.
3. Creates local aliases under the ignored `build/core8-binutils/` directory and prepends that
   directory to `PATH` for the helper process only.
4. Runs `firmware/config/boards/core8/compile_core8.sh`.
5. Checks for a non-empty BIN, ELF and Core8 INI, prints the BIN SHA-256, and verifies their signatures.

The clean steps mean this is not a board-preserving incremental build. They prevent objects, PCH data
or deliverables from another target being reused. Do not run this build concurrently with another
board build or local check in the same worktree because generated files and outputs are shared.

The PATH change is local to the helper: it does not permanently change the user's shell. The
`build/core8-binutils/` symlinks are ignored build state and may be recreated on every build.

## Artifacts

After a successful build, the principal outputs are:

| Path | Purpose |
| --- | --- |
| `firmware/deliver/fome.bin` | Combined Core8 image; the flash helper writes this image at `0x08000000`. |
| `firmware/build/fome.elf` | ELF used for symbols and firmware-signature checking. |
| `firmware/tunerstudio/generated/fome_core8.ini` | Matching TunerStudio definition. |
| `firmware/deliver/fome_update.srec` | Application update artifact checked by the local CI harness. |
| `firmware/deliver/fome_bl.srec` | Bootloader artifact checked by the local CI harness. |
| `firmware/build/fome.list` | Firmware listing checked by the local CI harness. |

The helper itself requires the first three paths. The broader Core8 check also requires the SREC
artifacts and `fome.list`. Existing artifacts in `firmware/deliver/` are replaced by a build.

The build prints `Build complete`, the BIN path, its SHA-256 and the matching signature. These are
build-artifact checks only. They are not hardware validation.

## Match TunerStudio to the build

Show the generated INI path and verify its signature:

```bash
bash .vscode/scripts/core8_dfu.sh ini
```

This is also the **Core8: Show TunerStudio INI** VS Code task. Use
`firmware/tunerstudio/generated/fome_core8.ini` with the produced firmware. If `wslpath` is available,
the helper also prints a Windows path for that file.

The helper reads the INI's `signature` field and the `rusEFI (FOME)` signature strings from the ELF and
BIN. It requires all three values to match, requires the firmware signature to contain `.core8.`, and
checks the image against the INI. Do not pair the image with an INI copied from another board or
build.

## Optional USB DFU programming

The helper never flashes as part of a build. Programming requires a deliberate second operation after
the build has completed:

```bash
bash .vscode/scripts/core8_dfu.sh flash
```

The equivalent VS Code task is **Core8: Flash firmware (USB DFU)**. It is not the default task.
The pinned helper does not ask an interactive yes/no question; the `flash` argument or selecting that
task is the explicit opt-in. There is no separate `--confirm` flag. Only use it when you intend to
overwrite the connected Core8 and accept the hardware operation.

Before calling the programmer, the helper:

- requires the BIN, ELF and INI to exist and verifies their signatures;
- uses the `STM32_PROGRAMMER_CLI` environment variable when set and rejects a missing path or command name; the specified CLI must also be runnable,
  otherwise searches `PATH` and then `misc/install/STM32_Programmer_CLI/bin`;
- requires exactly one DFU device, with a detected port and serial number;
- requires the Core8 device ID `0x0413`;
- converts the BIN path with `wslpath -w` when invoking a Windows `.exe` programmer from WSL.

For a vendor STM32CubeProgrammer installation, make its `bin` directory available on `PATH`. When that
programmer is a Windows executable in WSL, `wslpath` is required.

With those checks satisfied, the helper writes `fome.bin` at `0x08000000` using the programmer's `-v`
verification option, starts execution at the same address with `-g`, and checks that the device has left
DFU mode. Signature equality is not a cryptographic authenticity check.

No build or hardware operation was performed while producing this documentation. Build success and the
programmer checks above do not establish that a particular Core8 board, bootloader, USB cable or host
setup has been validated in hardware.

## Further tooling references

- The local check harness can run the Core8 build and artifact checks with
  `bash misc/ci/capoworks-checks.sh core8`. Its Linux package list and artifact coverage are in the
  [Capoworks checks README](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/misc/ci/README.md?plain=1).
- The helper's own developer notes are in the
  [Core8 developer helper README](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/.vscode/scripts/README.md?plain=1).

## Pinned source references

These links are pinned to the firmware revision used for this page:

- [Core8 build and DFU helper](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/.vscode/scripts/core8_dfu.sh)
- [Core8 VS Code tasks](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/.vscode/tasks.json)
- [Core8 board definitions](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/config/boards/core8/board.mk)
- [ARM compiler selection](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/use_arm_gcc.mk)
- [Core8 tooling change `034ec75b`](https://github.com/capoworks/capoworks-ecu/commit/034ec75bc1e9bf7391eeb0050b13038c0f60e3d7)
