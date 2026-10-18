# Low-Z Injector Driver

Low-impedance injectors need a current-controlled peak-and-hold driver. A saturated low-side
output left on for the injection pulse can overheat the injector, so it is not a substitute for
a dedicated driver with boost, peak, transition and hold control.

## Support and board matching

At this release, the controller path is compiled by `EFI_MC33816`. STM32F4 defaults it enabled;
the F7 feature header inherits F4 and disables it, and H7 inherits that disabled setting. A board
target can override the default, so inspect its build configuration rather than assuming that a
processor family or the presence of the menu proves support.

The source file is named `mc33816.cpp`, its class uses `Pt2001Base`, and TunerStudio calls the
screen **PT2001 control**. That naming is historical and does not establish that MC33816 and
PT2001 are interchangeable. Match the exact fitted controller and external boost/current-control
hardware to its schematic and NXP documentation. Existing board guides such as
[Atlas](/Hardware/Brain-Boards/Atlas/FOME-Atlas/) and
[Universal 112](/Hardware/Base-Boards/Polygonus-Universal-112/Universal-112/) describe interfaces,
not universal PT2001 support.

## Configuration

Open **Fuel > PT2001 control**. Its fields include SPI chip select and device, reset, optional
`FLAG0`, boost voltage, boost/peak/hold current targets, phase timings, bypass and maximum
injection duration. `DRIVEN` must also be a valid pin, but it is not exposed in this release's
dialog; board configuration must supply it. At initialization, invalid chip-select, reset or
`DRIVEN` assignments cause the driver to return without starting.

Derive every electrical and timing value from the injector datasheet, driver limits and measured
current waveform. The firmware does not provide safe universal settings.

## Diagnostics and limits

Monitor battery voltage and the serial console for `PT2001 error` messages. `FLAG0` is optional;
if assigned it is read by the driver library. A low battery voltage can leave the controller
uninitialized until voltage recovers. Bench validation should use an isolated injector and a
current probe, checking boost, peak, transition and hold rather than only whether the valve
clicks.

## Source references

- [F4 defaults and F7 override for the driver path](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/ports/stm32/stm32f7/efifeatures.h#L13-L18)
- [Initialization gates and controller binding](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/hw_layer/mc33816.cpp#L153-L210)
- [TunerStudio driver fields](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L3356-L3375)
- [NXP application note for MC33816 versus PT2000 differences](https://www.nxp.com/docs/en/application-note/AN5203.pdf)
