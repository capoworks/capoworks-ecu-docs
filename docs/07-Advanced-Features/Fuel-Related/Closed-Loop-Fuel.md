# Closed Loop Fuel Correction

Closed-loop fuel correction trims delivered fuel toward the target lambda. Enable
it with `fuelClosedLoopCorrectionEnabled`, then configure **Fuel > Closed loop
fuel correction**. This is transient short-term trim, not an automatic
recalibration of the VE, MAF, Alpha-N, lambda-target, or ignition tables.

Correction is allowed only while the engine is running, after
`stft_startupDelay`, and when coolant is valid and at or above `stft_minClt`.
Each cylinder uses `cylinderBankSelect` to choose a bank. Bank 1 reads `Lambda1`,
bank 2 reads `Lambda2`, and so on. The selected load coordinate comes from
`stftLoadSource`; `stft_maxOverrunLoad` and `stft_minPowerLoad` separate the idle,
overrun, power, and main regions.

Each region has `stft_cellCfgsN_timeConstant`, `stft_cellCfgsN_maxAdd`, and
`stft_cellCfgsN_maxRemove`. The controller integrates lambda error toward the
commanded target. `stftIgnoreErrorMagnitude` selects constant-rate adjustment.
The current implementation clamps the effective trim to plus or minus 25 percent.

Correction pauses, without clearing that region's accumulated trim, when the
lambda reading is missing or outside `stft_minLambda` to `stft_maxLambda`. It also
pauses for `noFuelTrimAfterDfcoTime` after DFCO and for two seconds after another
fuel or spark cut. If the feature itself is disabled, or its running, startup, or
CLT gate fails, the returned bank multipliers are `1.0`.

Do not interpret a failed sensor or a paused trim as successful calibration. A
dead sensor produces no new lambda error, and the cell can retain its previous
correction when correction resumes. Inspect the lambda channel, fault state,
`fuelClosedLoopBinIdx`, bank trim, target lambda, and recent cut state together.
Run open-loop calibration separately, establish a valid target and sensor
reading, then enable closed loop and verify each bank and region.

## Source references

- [Closed-loop admission and sensor/cut pauses](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/math/closed_loop_fuel.cpp#L52-L143)
- [Bounded integrator and failed-sensor error handling](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/controllers/math/closed_loop_fuel_cell.cpp#L15-L88)
- [Region and limit configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/integration/fome_config.txt#L229-L244)
- [TunerStudio labels](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/firmware/tunerstudio/tunerstudio.template.ini#L4197-L4210)
