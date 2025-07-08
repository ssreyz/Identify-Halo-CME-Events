import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Load data (replace with your file)
data = pd.read_csv("cleanDataset\AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02_cleaned.csv", parse_dates=['time'])

# Ensure 'time' is the index
data.set_index('time', inplace=True)

window = '30T'  # 30-minute window
k = 2           # Multiplier for standard deviation

# Calculate rolling mean and std
data['np_mean'] = data['proton_density'].rolling(window).mean()
data['np_std'] = data['proton_density'].rolling(window).std()

# Threshold = mean + k*std
data['threshold'] = data['np_mean'] + k * data['np_std']

# Flag CME events (Np > threshold)
data['cme_detected'] = data['proton_density'] > data['threshold']

fig, ax = plt.subplots(figsize=(12, 6))

# Plot proton density and threshold
ax.plot(data.index, data['proton_density'], label='Proton Density ($N_p$)', color='blue')
ax.plot(data.index, data['threshold'], label='Threshold', linestyle='--', color='red')

# Highlight CME events
cme_events = data[data['cme_detected']]
ax.scatter(cme_events.index, cme_events['proton_density'], color='red', label='CME Detected')

# Format plot
ax.set_title('CME Detection: Proton Density ($N_p$) and Threshold (30-min window, k=2)')
ax.set_ylabel('Density (cm$^{-3}$)')
ax.set_xlabel('Time')
ax.legend()
ax.grid(True)

# Format x-axis for dates
date_format = DateFormatter('%Y-%m-%d %H:%M')
ax.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

plt.tight_layout()
plt.show()

# Extract CME events with timestamps
cme_events = data[data['cme_detected']][['proton_density', 'threshold']]
print("Detected CME Events:")
print(cme_events)