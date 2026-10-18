# MAF Fuelling Strategy

MAF-based fuelling is an engine management strategy that calculates fuel delivery using a mass air flow (MAF) sensor's measurement of the air entering the engine. A valid MAF reading can account for air-density changes and some airflow changes directly, but it does not guarantee correct fuelling after every intake or engine modification. The sensor installation, transfer function, and trim calibration still need to suit the engine.

## MAF fuel setup and tuning

To tune a Capoworks ECU using MAF, you need a working MAF sensor and a suitable transfer function that converts its raw signal into kilograms per hour (kg/h). Details on setting up the sensor and its transfer function are on the [MAF sensor page](/Sensors-And-Gauges/General-Sensors/MAF). For model selection and migration guidance, see [Airmass Models and Migration](/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/).

Start with the **MAF Trim** table at 100 percent. The current firmware provides an 8x8 trim table with engine speed on the X axis and pre-trim standardized cylinder-filling percentage on the Y axis. Adjust the trim where a correctly operating, steady-state combination of RPM and airflow does not meet its target; use the AFR or lambda target table when you want a different target air-fuel ratio.

## MAF airmass calculation

The MAF sensor produces a raw signal, which the MAF transfer function converts into airflow in kg/h. The MAF airmass model then converts that measured flow and engine speed into airmass per cylinder:

```text
airflow_g_per_s = maf_kg_per_h / 3.6
air_per_revolution = airflow_g_per_s / (rpm / 60)
cylinder_airmass = air_per_revolution / (cylinder_count / 2)
```

The divisor `cylinder_count / 2` reflects the half of the cylinders that take in air during one revolution of a four-stroke cycle. See the [implemented conversion](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb/firmware/controllers/algo/airmass/maf_airmass.cpp?plain=1#L105-L124) in the pinned firmware source.

## Standardized cylinder filling and MAF Trim

To produce a load value for tables and corrections, the model compares the measured cylinder airmass with a standard charge for one cylinder:

```text
standard_charge = ideal_gas_law(displacement / cylinder_count, 101.325 kPa, 293.15 K)
air_charge_load_percent = 100 * cylinder_airmass / standard_charge
```

The standard pressure is 101.325 kPa and the standard temperature is 293.15 K (20 degrees C). The ideal-gas calculation uses the gas constant and molar mass of air rather than a fixed air-density constant. See the [standard-charge calculation](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb/firmware/controllers/algo/airmass/maf_airmass.cpp?plain=1#L105-L124) in the firmware source.

`air_charge_load_percent` is the standardized amount of air in a cylinder before trim is applied. It is not a percentage of the MAF sensor's output. The MAF Trim table uses this pre-trim filling percentage on its Y axis and engine speed on its X axis:

```text
trim_percent = MAF_Trim_table(RPM, air_charge_load_percent)
corrected_cylinder_airmass = cylinder_airmass * trim_percent / 100
```

A trim of 100 percent leaves the calculated airmass unchanged. Values above 100 percent increase the airmass used for fuelling, and values below 100 percent reduce it. The trim table is separate from the VE table. The configuration template defines it as an 8x8 table, and the model applies it after calculating `air_charge_load_percent`; see the [table definition](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb/firmware/integration/fome_config.txt?plain=1#L1637-L1641) and the [trim calculation](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb/firmware/controllers/algo/airmass/maf_airmass.cpp?plain=1#L129-L140).

## Two MAF sensors

When a secondary MAF sensor is configured:

- If both sensors provide valid readings, their airflows are added.
- If only one sensor is valid, the model uses twice that sensor's reading. This is a fallback and the airmass evaluation is marked degraded.
- If neither sensor is valid, the model does not produce an airmass result.

The active behavior is visible in the pinned [dual-MAF handling](https://github.com/capoworks/capoworks-ecu/blob/8f4fcfb/firmware/controllers/algo/airmass/maf_airmass.cpp?plain=1#L7-L35).

At this level, the MAF calculation is a conversion from measured mass airflow and engine speed to corrected cylinder airmass. Fuel delivery then uses that corrected airmass through the normal fuelling calculation.

For those interested, [this link](https://www.efunda.com/designstandards/sensors/hot_wires/hot_wires_theory.cfm) details the MAF sensor equations in more detail.
