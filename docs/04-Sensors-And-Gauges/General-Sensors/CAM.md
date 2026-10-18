# Camshaft position

A camshaft input can provide engine-phase information for sequential operation or measure VVT angle; some trigger patterns instead use the cam as the primary wheel. Configure the correct trigger pattern first, assign the physical cam input, and select which cam supplies engine sync. Use an event-conditioned input named by your board target, not an arbitrary GPIO.

The hardware capture path receives both edges. **Invert cam inputs** changes the logical rising/falling interpretation in software, while Hall/VR conditioning and pull-up/down selection belong to the board circuit. Choose them from the exact board revision and sensor type. Inversion can correct an inverted waveform, but cannot repair a weak, clipped, or noisy signal.

With the engine safely cranked or the wheel driven on a bench, enable the engine sniffer and inspect CAM/VVT edges against the crank pattern. Enable `vvt_details` for decoder messages and run `triggerinfo` to check crank synchronization and error counters. A visible cam trace alone does not prove phase sync; require valid synchronization and expected sequential behavior before enabling fuel and spark. For VVT, verify the configured offset only after the CAM decoder reports an angle, with the control solenoid disabled so the measured zero is meaningful.

Core8 exposes four VR/Hall event inputs (E2-E5) in addition to digital event inputs, but the configured trigger pattern may reserve one for the crank or secondary wheel. Check the target's generated INI before assigning pins. Keep CAM and crank signal grounds and conditioning requirements board-specific; do not apply generic processor voltage limits.

## Sources

- [CAM input, inversion, and phase configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L566)
- [TunerStudio CAM and VVT fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2811)
- [CAM edge inversion and sniffer logging](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_central.cpp#L222)
- [Core8 event-input names](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/core8/connectors/main.yaml#L242)
