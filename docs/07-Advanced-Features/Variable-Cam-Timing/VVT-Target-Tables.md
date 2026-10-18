# VVT Target Tables

Capoworks provides one 8 x 8 intake target table and one 8 x 8 exhaust target table. Intake controllers on both banks share the intake table, and exhaust controllers share the exhaust table. The table value is the requested decoder-relative VVT angle; RPM is one axis and an independently selectable load source is the other.

## Axes and limits

The RPM bins cover 0-18000 RPM and the load bins cover 0-1000 in the configuration format. Target cells are signed values configured within -125 to 125, but that numeric range does not guarantee mechanical travel or safe operation for an engine. Use only targets supported by the cam mechanism, oil system, decoder range and measured response.

Select intake and exhaust load sources in **VVT Configuration & PID**. A source value of `Zero` means use the model's default fuel load, not an axis fixed at zero. If the selected source is invalid or unavailable, the target becomes invalid and VVT output turns off. The intake and exhaust sources remain independent.

The sign must agree with the reported angle and the configured control direction. Changing the VVT mode, offset or direction does not make an existing table valid for another installation; recheck zero, reachable angle and direction after those changes.

## Ramping and tuning

Once arming conditions are satisfied, the controller ramps from zero to the table target over two seconds. Targets near the rest position disable control using the hysteresis described on [On/Off VVT control](/Advanced-Features/Variable-Cam-Timing/On-Off-VVT). The **VVT Testing** target bump adds the configured offset for two seconds and is useful for checking response at a steady operating point.

Populate the table from controlled steady-state or dyno measurements, not copied values. First complete [VVT PID control](/Advanced-Features/Variable-Cam-Timing/VVT-PID) tuning at a reachable nonzero target. Then log RPM, selected load source, target, measured position, output and engine result while moving through each region. Smooth interpolation between measured cells reduces abrupt demand changes.

## Sources

- [VVT table dimensions, value range and axes](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L1616-L1622)
- [Target lookup, axis override and near-rest disable](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L86-L129)
- [Intake/exhaust table assignment](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/actuators/vvt.cpp#L242-L251)
- [Independent axes and stale-load behavior tests](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/unit_tests/tests/actuators/test_vvt.cpp#L41-L80)
