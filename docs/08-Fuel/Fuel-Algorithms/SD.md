# Speed Density Strategy

Speed density is one of the most commonly used fuelling strategies in modified cars and ECU tuning. It estimates the amount of air entering the engine from engine speed (RPM), manifold absolute pressure (MAP), and intake air temperature. Instead of directly measuring airflow like a MAF sensor, the ECU calculates airmass using a volumetric efficiency (VE) model of the engine. This approach responds quickly and can suit aggressive camshafts or installations where a MAF sensor is impractical, but its accuracy depends on appropriate VE calibration.

For Capoworks-specific details about the current calibration, selectable temperature source, and measured-MAP versus MAP-estimate policy, see [Airmass Models and Migration](/Fuel/Fuel-Algorithms/Airmass-Models-and-Migration/).

Information on the equations used for speed density tuning can be found [at the following link explaining it](https://www.mathworks.com/help/autoblks/ug/compression-ignition-engine-speed-density-breathing-model.html).
