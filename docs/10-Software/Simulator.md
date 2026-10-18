# ECU Simulator

The Capoworks ECU Simulator is a desktop build of a subset of the firmware. It is useful for development, practicing tuning and testing control logic without energized engine hardware. It is not a model of a complete vehicle or a substitute for bench and vehicle validation.

The simulator build uses `EFI_SIMULATOR=1`, `EFI_PROD_CODE=0` and `EFI_UNIT_TEST=0`. The Makefile produces `fome_simulator` on POSIX systems and `fome_simulator.exe` on Windows. POSIX builds currently request 32-bit compilation; the Windows toolchain is `i686-w64-mingw32`
([`Makefile`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/simulator/Makefile#L15)).
Availability in a Capoworks artifact is build-specific.

ECU Console can launch the simulator from its startup screen and then connects through TCP to localhost port `29001`
([`SimulatorHelper.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/SimulatorHelper.java#L24)).
The simulator can also be started directly. Configuration writes are persisted in the simulator's working directory as sector files such as `flash1.bin` and `flash2.bin`, not in physical ECU flash
([`main.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/simulator/main.cpp#L227)).

## CAN

On Linux, the simulator CAN driver binds a SocketCAN device named `can0` through an `AF_CAN` raw socket. Missing interfaces or bind failures leave the socket unopened. This is real host CAN traffic, but there is one simulated CAN driver and no userspace bitrate configuration in this layer
([`hal_can_lld.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/simulator/simulator/can/hal_can_lld.cpp#L87)).
The pinned simulator configuration disables CAN on Windows.

## Sensors

The desktop board has no ADC hardware, so physical analog inputs cannot be read. The simulator supplies a mock battery-voltage sensor at 14 V so normal controller startup can proceed
([`rusEfiFunctionalTest.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/simulator/simulator/rusEfiFunctionalTest.cpp#L322)).
Other sensor values can be injected with firmware console commands: `set_sensor_mock <sensor-name> <value>`, `reset_sensor_mocks`, `show_sensors` and `show_sensor <index>`
([`init_sensors.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/init/sensor/init_sensors.cpp#L89)).
These are mocked values in the sensor registry, not readings from an attached sensor.

## Outputs

Output pins retain logical state, and simulator builds write their electrical state into an in-memory mock-pin table. No MCU GPIO, injector, ignition coil or relay is driven
([`io_pins.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/io_pins.cpp#L168)
and [`efi_gpio.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/system/efi_gpio.cpp#L448)).
Bench-test controls can therefore exercise firmware state transitions, but success says nothing about wiring, driver current, coil dwell or actuator health.

## Self-stimulation

The simulator enables direct trigger self-stimulation during initialization and starts at 1200 RPM
([`rusEfiFunctionalTest.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/simulator/simulator/rusEfiFunctionalTest.cpp#L232)).
The trigger emulator feeds decoded crank and cam behavior directly into the trigger handlers rather than requiring a physical wheel. The `rpm <value>` command changes the emulated speed; `rpm 0` stops the simulated trigger frequency
([`trigger_emulator_algo.cpp`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_emulator_algo.cpp#L87)).

## Limits

The compiled simulator disables ADC, USB serial, OpenBLT, EGT, software knock and onboard GPIO-expander counts. Linux CAN is real host I/O; everything described as a sensor mock or output state is virtual. Changing a tune or exercising a benchmark in the simulator does not establish compatibility or safety on real Capoworks hardware.
