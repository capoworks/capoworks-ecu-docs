---
sidebar_position: 1
---

# USB Mass Storage

Some Capoworks firmware builds expose a read-only FAT volume over USB. The volume contains the
TunerStudio INI that matches the firmware, so a build can provide this drive without compiling SD-card
logging or the target-side FatFS stack.

This guide is pinned to firmware source commit
`8f4fcfb40135fe7e5f15b280f7e05d9863b60f52`. Branch heads move, so check the flags and artifacts from
the source revision that produced your firmware.

:::note

USB mass storage is a build feature, not a universal Capoworks ECU feature. A board or release exposes
the drive only when its firmware was compiled with USB mass storage and an embedded INI image. Do not
infer support from the USB connector alone.

:::

## What the drive contains

When an INI image is embedded, logical unit 0 (LUN 0) is reported as `INI Drive`. Its
volume label is `FOME EFI`, and the inherited `FOME` device name remains a technical identifier.
The image contains:

- `fome.ini.zip`, which contains the TunerStudio INI for that firmware build;
- dated usage/readme text;
- links to the project wiki, Discord and releases.

The target serves a prebuilt, read-only image. It does not need an SD card or a writable FatFS volume
to expose these files. The host computer still mounts the image as FAT.

With SD logging compiled in, LUN 1 is the SD-card volume. The INI drive and SD-card volume are separate:
the INI drive never contains the SD card's logs, tune files or other user files.

## Build configuration

The relevant settings are compiled into the firmware:

| Setting | Effect |
| --- | --- |
| `EFI_USB_MSD` | Enables USB mass storage when USB serial is also enabled. It defaults to `EFI_FILE_LOGGING`, preserving existing builds that did not opt in explicitly. |
| `EFI_FILE_LOGGING` | Compiles SD-card logging, the SD driver and the SD-card LUN. It remains independent of an INI-only mass-storage configuration. |
| `EFI_EMBED_INI_MSD` | Embeds the read-only FAT image used for LUN 0. |
| `HAL_USE_USB_MSD` | Derived as `EFI_USB_MSD && EFI_USB_SERIAL`; this is not a separate user switch. |
| USB OTG configuration | The target must have an enabled USB OTG peripheral. |

The resulting layouts are:

| Firmware build | USB LUNs | Host-visible storage |
| --- | --- | --- |
| Logging and mass storage with an embedded image | 2 | LUN 0: matching INI drive; LUN 1: SD-card slot |
| Mass storage without logging, with an embedded image | 1 | LUN 0: matching INI drive |
| Mass storage disabled | 0 from this feature | No drive; SD logging may still exist if compiled |
| Mass storage enabled but no valid embedded image | 1 or 2, depending on logging | LUN 0 is null; an SD-card slot may still exist |

For an INI-only build, the firmware definition needs `EFI_USB_MSD=TRUE`,
`EFI_FILE_LOGGING=FALSE` and `EFI_EMBED_INI_MSD=TRUE`; it must also have USB serial and USB OTG
available. No board defaults were changed by the decoupling. The exact syntax for adding definitions
depends on the board makefile.

When SD logging is compiled in, changing `EFI_USB_MSD` does not itself change logging behavior.
`EFI_FILE_LOGGING` still controls the SD driver and logger, and a build with both features continues to
expose two LUNs. An INI-only build has no SD filesystem to expose at all.

The image generator uses one 512-byte sector per cluster for the small FAT image. USB mass-storage
sectors are also fixed at 512 bytes, including when SD support is absent.

## TunerStudio settings are not build switches

There is no TunerStudio setting that turns an INI-only USB drive on. Its presence is decided when the
firmware is compiled.

If the matching TunerStudio definition includes the **SD Card Logger** dialog, its **Enable SD Card**
field controls the runtime SD-logging setting. That setting cannot add an SD driver, add a filesystem or
create USB mass storage in a firmware build that omitted them. Turning SD logging off also does not
change the compiled LUN count or convert a two-LUN build into an INI-only build.

The `SD: MSD` indicator in TunerStudio reports the SD-card mass-storage attachment. It is not proof that
LUN 0 contains the embedded INI, especially in an INI-only build.

## Access the embedded INI

1. Power the ECU in the way required for its USB port. For example, connecting an SD-logging ECU by
   USB normally makes its SD card available to the host.
2. Connect a data-capable USB cable to the host computer.
3. Wait for the host to mount a read-only volume labelled `FOME EFI`. A two-LUN build may show two
   volumes; use the one containing `fome.ini.zip` and the documentation files.
4. Copy or extract `fome.ini.zip` on the host, then use its INI with the matching firmware. Do not
   attempt to edit or save files on the read-only ECU volume.
5. Eject or safely remove the volume before unplugging the ECU.

The volume's files can be copied while the direct USB console is also present. Use the INI from the
same release or build as the firmware; an INI from another target or revision may have an incompatible
signature and tune layout.

## If no usable drive appears

- The firmware may not have been built with USB mass storage.
- The target may not have USB OTG or USB serial enabled.
- LUN 0 may be the null placeholder because the build has no embedded INI image.
- The image generator may have emitted `RAMDISK_INVALID`. Direct Cygwin/MinGW and macOS builds take
  this fallback path; Linux and WSL image generation needs `dosfstools`, `mtools`, `zip` and `xxd`.
- The host may have mounted only the SD-card LUN in a two-LUN build. Check both volumes for
  `fome.ini.zip`.
- A build with an empty or unformatted-looking placeholder does not provide access to SD files. SD
  file access requires the SD logging/filesystem feature, a usable card and the SD-card LUN.

## Pinned source references

These links are pinned to the firmware revision used for this page:

- [Mass-storage initialization and LUN layout](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/hw_layer/mass_storage/mass_storage_init.cpp)
- [Mass-storage interface guards](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/hw_layer/mass_storage/mass_storage_init.h)
- [USB MSD, LUN count and HAL conditions](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/hw_layer/ports/rusefi_halconf.h)
- [STM32F4 defaults for logging, USB MSD and the embedded INI](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/hw_layer/ports/stm32/stm32f4/efifeatures.h)
- [Embedded FAT image generator](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb40135fe7e5f15b280f7e05d9863b60f52/firmware/hw_layer/mass_storage/create_ini_image.sh)
- [Decoupling change `17a70bec`](https://github.com/capoworks/capoworks-ecu/commit/17a70bec29072107d2a77ec918c453097bf8da21)
- [512-byte cluster change `7202950e`](https://github.com/capoworks/capoworks-ecu/commit/7202950e5e5c7860f02869bd9804fa3c312c725b)
