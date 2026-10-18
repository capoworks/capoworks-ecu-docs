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
