# ECU Simulator

In addition to the supported ECU hardware targets, Capoworks distributions may provide an ECU
Simulator build. The ECU Simulator is a special build of the firmware designed to run on a modern computer. Naturally, many features
are missing as a general computer lacks hardware support, but the core remains. Additionally some functions are adapted
to commonly available features and sensors and outputs are mocked.

ECU Simulator not only aids development by simplifying debugging, but also allows users to become familiar with the
system and tuning without spending any money and dealing with physical hardware.

When included, ECU Simulator is provided in the matching release or snapshot bundle and can be
launched directly from ECU Console or run manually. Inherited packages may retain the executable
name `console/fome_simulator.exe`; use the binary supplied in your active Capoworks artifact.

When available, the inherited ECU Simulator build targets Windows (x86_64). It may also build and
run on other platforms such as Linux or under Wine, but those configurations are not implied to be
prebuilt or supported by every Capoworks release.

## CAN

## Sensors

## Outputs

## Self Stimulation
