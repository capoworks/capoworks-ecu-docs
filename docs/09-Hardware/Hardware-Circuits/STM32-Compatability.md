# STM32 Compatibility with Capoworks ECU

Capoworks ECU source contains hardware ports for STM32F4, STM32F7, and STM32H7
families, plus a simulator target. That list describes firmware build paths; it
does not make every STM32F4, F7, or H7 device, clone, or custom board compatible.
A supported board target supplies startup files, pin maps, board support,
default connector names, and the matching TunerStudio definition.

The build selects `PROJECT_BOARD`, reads that board's configuration files, and
then chooses the CPU port from `PROJECT_CPU`. The default board is
`f407-discovery` with the F4 port. Proteus has explicit F4, F7, and H7 build
variants, while the Nucleo H743 and Core48 examples show that board support is
maintained through concrete configurations rather than MCU-family detection.
Changing only the MCU family in a build does not create the missing board
hardware definitions.

Before building or flashing, select the Capoworks board target named for the
installed board and revision. Confirm that the package, generated INI, and
pinout match that target. Check clock, flash, ADC, timer/PWM, SPI, CAN, USB, and
bootloader requirements in the actual board configuration rather than assuming
they follow from the STM32 part number. The board's connector map remains the
authority for physical pins.

Useful diagnostics are the configured target and CPU printed by the build, a
successful matching-firmware build, and agreement between the firmware target,
delivered INI, and board revision. A bootloader failure, absent peripheral, or
undefined pin usually indicates a target/board mismatch. Do not cross-flash an
F4 image onto an F7 or H7 board. For the two documented hardware lines, see
[Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas) and
[Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112).

## Sources

- [Default board and CPU selection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/rusefi.mk#L20)
- [Supported CPU-port branches and startup selection](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/rusefi.mk#L45)
- [Proteus F4/F7/H7 board variants](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/proteus/board.mk#L4)
- [Concrete STM32H743 Nucleo board configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/nucleo_h743/board.mk#L3)
