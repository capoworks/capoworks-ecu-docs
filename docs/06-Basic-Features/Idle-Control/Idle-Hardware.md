# Idle Control Hardware

Open _Idle > Idle hardware_. Enable **Use Stepper** only for a stepper motor.
Hardware changes require an ECU reboot. Pin selectors are not a universal
wiring diagram; use the installed board and revision documentation.

## Solenoids

### Single wire

Select one board-supported PWM output as **Idle Solenoid Primary output**. Open
loop, adders, and feedback corrections produce its commanded percentage. With
the engine stopped and no idle bench test active, both solenoid channels are
commanded to zero.

### Dual wire

Enable **Double Solenoid Mode** and configure **Idle Solenoid Secondary
output**. Both outputs use the idle frequency and are driven in complementary
directions as position changes. The runtime raises a configuration error if the
secondary output is missing.

### PWM frequency

**Idle Solenoid Frequency** applies to both solenoid outputs at hardware
initialisation and requires the indicated ECU restart. Use the valve or driver
manufacturer's supported frequency.

## Stepper Motors

The final idle percentage becomes a target from zero to **Stepper total steps**.
Select one of these driver paths:

### Dedicated stepper hardware

Leave both **Drive stepper with dual H bridges** and **Drive stepper with
PushPull outputs** disabled. Configure **Idle Stepper Step Pin**, **Idle
Stepper Dir Pin**, their modes, and the optional enable input in **Stepper
Controller Hardware**.

For STEP/DIR drivers, Capoworks ECU keeps the enable output asserted between
steps instead of releasing it after every pulse. After the driver is enabled,
the firmware waits a fixed 2 ms before the first STEP edge so the driver and
winding current can settle. This delay is independent of the configured step
reaction time. The driver is released after five seconds without movement, and
any further step re-enables it and repeats the 2 ms delay.

The driver is also released, and no step is taken, when main-relay power is off
or battery voltage is below the minimum stepper voltage. This check is repeated
during the 2 ms enable delay, so a supply loss at that moment does not produce a
step. Confirm the enable polarity for the installed board and set the minimum
stepper voltage to match the hardware before relying on this release.

### Dual H bridge

Enable **Drive stepper with dual H bridges** and configure the two
**Stepper H-Bridge Hardware** channels. Each channel uses its direction pins
and optional disable output. Inversion and micro-stepping controls apply only
when supported by that hardware.

### PushPull outputs

Enable **Drive stepper with PushPull outputs** and assign **Stepper A+**,
**A-**, **B+**, and **B-**. The runtime groups A+/A- and B+/B- as two phases.
Verify the board's output circuit and current path before connecting external
hardware.

The [Universal 112 v1.2 pinout](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112-Pinout)
documents that revision's onboard stepper driver and outputs unavailable while
it is used. Other boards and revisions need their own documentation.

## Sources

- [Solenoid and zero-RPM behavior](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/idle_hardware.cpp#L30)
- [Three stepper hardware initialisation paths](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/idle_hardware.cpp#L89)
- [Idle hardware configuration controls](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3837)
- [Idle output and actuator application](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/idle_thread.cpp#L289)
- [STEP/DIR enable retention, 2 ms settle delay, and power-loss release](https://github.com/capoworks/capoworks-ecu/blob/8a9878bd55d31d648b42a4504a7eac35928238da/firmware/hw_layer/stepper.cpp)
- [Stepper enable-timeout regression tests](https://github.com/capoworks/capoworks-ecu/blob/8a9878bd55d31d648b42a4504a7eac35928238da/unit_tests/tests/actuators/test_stepper.cpp)
