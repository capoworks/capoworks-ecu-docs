# Crankshaft Position

The crankshaft input drives primary trigger decoding. First select the exact trigger pattern or enter the correct custom tooth and gap counts; an incompatible pattern cannot be repaired by edge inversion or timing offset. Assign a board-supported event input as the primary channel and use the secondary channel only when the selected pattern requires it. Start with the hardware-conditioned input intended for crank VR or Hall signals.

The capture layer accepts both signal edges and applies **Invert Primary** in software after capture. Set inversion from the observed waveform and decoder behavior, not by guessing from sensor color codes. Verify the sensor supply, ground, pull-up/down, and input conditioning against the board revision; do not infer input voltage tolerance from the microcontroller alone.

During initial cranking or bench rotation, watch the crank teeth in the engine sniffer. Use `trigger_details` for synchronization messages and `triggerinfo` to inspect sync state, expected-tooth errors, and ordering errors. A repeating edge trace without valid sync is not proof that the wheel definition is usable. Only after stable sync and RPM should you use fixed timing and a timing light to set **global trigger angle offset**. Ensure the commanded timing matches the strobe through the intended range.

Core8 names four VR/Hall event inputs E2-E5, plus digital event inputs; Atlas names two VR and six digital event inputs. Counts and names are target-specific, and a pin may already be reserved by the trigger configuration. Recheck the generated INI and connector for the installed board revision before changing wiring.

## Sources

- [Trigger pattern and primary input configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L541)
- [Primary inversion and trigger input fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L2796)
- [Edge interpretation and synchronization diagnostics](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/trigger/trigger_central.cpp#L385)
- [Core8 crank event inputs](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/config/boards/core8/connectors/main.yaml#L242)
