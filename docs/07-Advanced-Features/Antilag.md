# Antilag

Antilag (ALS) adds fuel and retards or alters ignition while the engine is off-throttle to keep the turbocharger spooled. It is configured under **Base Engine** in TunerStudio. Antilag produces high exhaust temperatures and pressure; use it only with hardware and a tune prepared for it.

## Arming conditions

Capoworks ECU activates antilag only while all of the following are true:

- **Enable antilag** is on.
- **ALS max duration** is greater than zero.
- Engine speed is above **ALS min RPM** and below **ALS max RPM**.
- Coolant temperature is above **ALS min CLT** and below **ALS max CLT**.
- Driver throttle intent is below **ALS max TPS**. If the throttle-intent sensor is missing or reports a non-finite value, antilag does not arm.
- The activation switch condition is met. In **Always on** mode this is always true; in **Switch input** mode the configured **ALS activate pin** must be active, respecting the inversion setting.

## Continuous activation timeout

**ALS max duration** limits how long antilag may stay active in one continuous activation. The timer starts when the arming conditions first become true and antilag turns off once the elapsed time reaches **ALS max duration**.

After the timeout expires, antilag does not restart while the arming conditions remain true. The conditions must clear and then re-apply before antilag can activate again. For example, releasing the throttle-intent condition, leaving the RPM or coolant window, turning antilag off, or releasing the switch input re-arms the timer on the next activation.

A value of zero or a negative value inhibits antilag entirely. Set a positive duration.

## Defaults and migration

The default **ALS max duration** is 3 seconds. Existing tunes keep their stored value; check it after updating firmware. If a tune was saved with a non-positive duration, antilag will no longer activate until a positive value is entered.

## Safety boundaries

The timeout is a firmware timer, not a substitute for correct hardware protection. Confirm the duration, arming conditions, and resulting exhaust temperatures on the bench and under controlled conditions before relying on antilag. The unit tests cover the timeout boundary, re-arm behavior, and inhibition for non-positive durations; they do not validate behavior on an engine.

## Sources

- [Antilag update and timeout logic](https://github.com/capoworks/capoworks-ecu/blob/10e7ca7ccd2d6fd4cc10d3a6cf63beff72c2aa07/firmware/controllers/algo/antilag_system.cpp)
- [Antilag arming conditions](https://github.com/capoworks/capoworks-ecu/blob/10e7ca7ccd2d6fd4cc10d3a6cf63beff72c2aa07/firmware/controllers/algo/antilag_system.cpp#L74)
- [Default ALS max duration](https://github.com/capoworks/capoworks-ecu/blob/10e7ca7ccd2d6fd4cc10d3a6cf63beff72c2aa07/firmware/controllers/algo/defaults/default_base_engine.cpp#L141)
- [Antilag timeout unit tests](https://github.com/capoworks/capoworks-ecu/blob/10e7ca7ccd2d6fd4cc10d3a6cf63beff72c2aa07/unit_tests/tests/actuators/test_antilag.cpp)
