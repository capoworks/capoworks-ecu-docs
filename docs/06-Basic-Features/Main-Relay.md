# Main Relay Control

Configure the logical **Output** and **Output mode** under _Controller >
Actuator Outputs > Main relay output_. The physical pin and its drive
capability come from the installed board, not from the configuration label.

Main-relay behavior is also a firmware-build feature. The base STM32F4 feature
default is `EFI_MAIN_RELAY_CONTROL = FALSE`; board targets may enable it. On
builds with control disabled, the output is held on except during a relay bench
test. Do not assume battery-voltage-driven shutoff is active on every board.

## Behavior when enabled

Capoworks treats battery voltage above 5 V as ignition voltage. While that
voltage is present, the relay is requested on. After it disappears, the main
relay controller and other engine modules can request delayed shutoff; the
controller's own holdover is one second after the last valid ignition-voltage
sample. The output remains on for a bench request, ignition voltage, or any
module's delayed-shutoff request.

If a **Main Relay Voltage** sensor is configured, the relay output begins on
and the controller waits 0.5 seconds before comparing measured battery and
main-relay voltages. A difference greater than 3 V raises the main-relay fault
warning. Verify that the sensor represents the intended post-relay supply;
otherwise a correct relay can still report a fault.

The **Main Relay** bench command holds a bench request for about one second,
then normal logic evaluates again. Observe the physical relay and the
**Main relay: On** channel. If the channel changes but the relay does not,
check the board output circuit and relay supply. If neither changes, check pin,
output mode, battery-voltage input, and whether this firmware build includes
main-relay control.

## Sources

- [Main-relay state, holdover, and voltage diagnosis](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/main_relay.cpp#L5)
- [Firmware-build gate and default](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/ports/stm32/stm32f4/efifeatures.h#L133)
- [Relay voltage-sense tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/actuators/test_main_relay.cpp#L22)
