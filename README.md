# 🌞 Identifying Halo CME Events Based on Particle Data from SWIS-ASPEX Payload onboard Aditya-L1

Our project focuses on identifying **Halo Coronal Mass Ejections (CMEs)** by analyzing in-situ **particle and plasma data** collected by the **SWIS-ASPEX payload** onboard India's first solar mission, **Aditya-L1**. It employs key interplanetary CME (ICME) signatures to isolate and classify potential Halo CME events.

---

<details>
<summary>📌 Project Overview</summary>

### Objective
- Detect and analyze **Halo CMEs** using parameters from **solar wind and particle data**.
- Correlate in-situ observations with known ICME signatures.
- Enhance prediction and space weather modeling by leveraging real-time payload data.

### Relevance
- Halo CMEs directed toward Earth can cause geomagnetic storms.
- Early detection is crucial for satellite safety, power grids, and communication systems.

</details>

---

<details>
<summary>📡 Data Source: SWIS-ASPEX on Aditya-L1</summary>

### SWIS-ASPEX Payload
- **SWIS**: Solar Wind Ion Spectrometer
- **ASPEX**: Aditya Solar wind Particle Experiment

These instruments measure:
- Proton and alpha particle flux
- Ion composition
- Energy spectra

Data format: `.csv` or `.cdf` (as applicable)

</details>

---

<details>
<summary>🧾 ICME Detection Parameters</summary>

| Parameter             | ICME Signature                   | Typical Threshold/Behavior              |
|-----------------------|----------------------------------|------------------------------------------|
| **Proton Temperature \(T_p\)** | Low \(T_p\)                      | \(I_{th} > 1\) or \(T_p\) below ambient [1] |
| **Plasma Beta (\(\beta\))**   | Low                              | \(\beta < 0.5\) [3]                       |
| **Proton Density (\(n_p\))**  | Enhanced/Variable               | Spikes at sheath/leading edge [4][5]     |
| **Solar Wind Speed (\(V_{sw}\))** | Sudden increase/expansion     | Step or ramp up [4][6]                   |
| **Particle Flux**             | Enhanced (protons, alphas)      | Sudden rise near shock [7]              |
| **Alpha/Proton Ratio**        | Elevated                        | \(\text{He}^{2+}/\text{H}^+ > 0.08\) [1] |
| **Ion Charge States**         | Enhanced (e.g., O\(^{7+}\)/O\(^{6+}\)) | Above solar wind norm [1][8]         |

</details>

---

<details>
<summary>🛠️ Methodology</summary>

1. **Dataset processing**:  
   - Taking datasets SWIS-ASPEX data in form of cdf file.
   - Convert the cdf file into csv file.

1. **Preprocessing**:  
   - Scale and normalize SWIS-ASPEX data.
   - Align timestamps and interpolate missing and the duplicate values.

2. **Feature Extraction**:  
   - Extract ICME-related parameters.
   - Calculate thresholds using scientific references.

3. **Event Identification**:  
   - Apply threshold filters.
   - Detect ICME intervals indicating Halo CMEs.
   - Use Random Forest algorithm to train the model for efficient analysing.

4. **Validation**:  
   - Compare the data from CACTus to check the icme events and validate it with our data

</details>

---

<details>
<summary>📊 Output & Visualization</summary>

- Time series plots of particle flux and plasma parameters
- Detected CME intervals highlighted
- Annotated plots with threshold crossings
- Correlation with cataloged CME events

> _Sample visualizations will be available in the `results/` folder._

</details>

---

<details>
<summary>📁 Repository Structure</summary>

