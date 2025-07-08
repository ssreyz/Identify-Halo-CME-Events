import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Load data
data = pd.read_csv("cleanDataset/AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02_cleaned.csv", parse_dates=['time'])
data.set_index('time', inplace=True)

# --- Step 1: Calculate Key ICME Parameters ---
# Expected proton temperature (Lopez, 1987)
data['T_exp'] = 0.5 * data['proton_bulk_speed']**1.58  # in K
data['T_ratio'] = data['proton_thermal'] / data['T_exp']  # ICMEs have T_ratio << 1

# Plasma beta (β = thermal pressure / magnetic pressure)
mu0 = 4 * np.pi * 1e-7  # Permeability of free space (SI)
kB = 1.38e-23  # Boltzmann constant
data['B_mag'] = np.sqrt(data['proton_xvelocity']**2 + data['proton_yvelocity']**2 + data['proton_zvelocity']**2)  # Placeholder for B field (if missing)
data['beta'] = (2 * mu0 * data['proton_density'] * kB * data['proton_thermal']) / (data['B_mag']**2)  # ICMEs have β < 0.3

# --- Step 2: Dynamic Threshold for Shock Detection (Np spike) ---
window = '30T'  # 30-minute rolling window
k = 4  # Multiplier for std deviation
data['np_mean'] = data['proton_density'].rolling(window).mean()
data['np_std'] = data['proton_density'].rolling(window).std()
data['np_threshold'] = data['np_mean'] + k * data['np_std']

# --- Step 3: ICME Detection Criteria ---
# 1. Np spike (shock/sheath)
# 2. Low β (< 0.3)
# 3. Low T_ratio (< 0.5)
# 4. Duration > 3 hours (optional)
data['is_shock'] = (data['proton_density'] > data['np_threshold'])
data['is_low_beta'] = (data['beta'] < 0.3)
data['is_cold'] = (data['T_ratio'] < 0.5)

# Combined ICME flag
data['icme_detected'] = data['is_shock'] & data['is_low_beta'] & data['is_cold']

# --- Step 4: Plot Results ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Plot 1: Proton Density
ax1.plot(data.index, data['proton_density'], label='$N_p$', color='blue')
ax1.plot(data.index, data['np_threshold'], label='Threshold (k=4)', linestyle='--', color='red')
ax1.scatter(data[data['icme_detected']].index, 
            data[data['icme_detected']]['proton_density'], 
            color='red', label='ICME Detected')
ax1.set_ylabel('Density (cm$^{-3}$)')
ax1.legend()
ax1.grid(True)

# Plot 2: Magnetic Field and Beta
ax2.plot(data.index, data['B_mag'], label='|B|', color='green')
ax2.plot(data.index, data['beta'], label='Plasma β', color='purple')
ax2.axhline(0.3, linestyle='--', color='black', label='β = 0.3')
ax2.set_ylabel('|B| (nT) / β')
ax2.legend()
ax2.grid(True)

# Plot 3: Temperature Anomaly
ax3.plot(data.index, data['T_ratio'], label='$T_p / T_{exp}$', color='orange')
ax3.axhline(0.5, linestyle='--', color='black', label='$T_p/T_{exp} = 0.5$')
ax3.set_ylabel('$T_p / T_{exp}$')
ax3.legend()
ax3.grid(True)

# Format x-axis
date_format = DateFormatter('%Y-%m-%d %H:%M')
ax3.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

plt.suptitle('ICME Detection: Multi-Parameter Analysis')
plt.tight_layout()
plt.show()

# --- Step 5: Print Detected ICMEs ---
icme_events = data[data['icme_detected']][['proton_density', 'B_mag', 'beta', 'T_ratio']]
print("Detected ICMEs:")
print(icme_events)
