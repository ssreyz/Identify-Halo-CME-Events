import numpy as np
import pandas as pd
import cdflib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator

def clean_data(data):
    """Handle fill/missing values in the dataset"""
    # Common fill values in space physics data
    FILL_VALUES = {
        'proton_density': [-1.0e31, 1.0e31],
        'proton_bulk_speed': [-1.0e31, 1.0e31],
        'alpha_density': [-1.0e31, 1.0e31]
    }
    
    # Replace fill values with NaN
    for col, fills in FILL_VALUES.items():
        if col in data.columns:
            for fill in fills:
                data[col] = data[col].replace(fill, np.nan)
    
    # Validate physical ranges
    data['proton_density'] = data['proton_density'].where(
        (data['proton_density'] > 0) & (data['proton_density'] < 100))
    
    data['proton_bulk_speed'] = data['proton_bulk_speed'].where(
        (data['proton_bulk_speed'] > 100) & (data['proton_bulk_speed'] < 1000))
    
    data['alpha_density'] = data['alpha_density'].where(
        (data['alpha_density'] > 0) & (data['alpha_density'] < 1))
    
    # Interpolate small gaps (<5 minutes)
    data = data.interpolate(limit=60)  # 60 points = 5 minutes for 5s resolution
    
    # Drop remaining NA
    return data.dropna()

def detect_halo_cme(data, thresholds=None):
    """Detect Halo CME events with visualization"""
    if thresholds is None:
        thresholds = {
            'speed': 450,
            'density_jump': 1.3,
            'alpha_ratio': 0.15,
            'min_duration': 1
        }
    
    results = {'cme_detected': False, 'events': [], 'statistics': {}}
    
    # Calculate moving averages
    window_size = 30
    data['density_ma'] = data['proton_density'].rolling(window=window_size).mean()
    data['speed_ma'] = data['proton_bulk_speed'].rolling(window=window_size).mean()
    data['alpha_ma'] = data['alpha_density'].rolling(window=window_size).mean()
    
    # Detection criteria
    cme_candidates = (
        (data['proton_bulk_speed'] > thresholds['speed']) &
        (data['proton_density'] > data['density_ma'] * thresholds['density_jump']) &
        (data['alpha_density'] > thresholds['alpha_ratio'])
    )
    
    if cme_candidates.any():
        cme_groups = (cme_candidates != cme_candidates.shift(1)).cumsum()
        for _, group in data[cme_candidates].groupby(cme_groups):
            if len(group) >= thresholds['min_duration']:
                event = {
                    'start_time': group.index[0],
                    'end_time': group.index[-1],
                    'duration': len(group),
                    'max_speed': group['proton_bulk_speed'].max(),
                    'max_density': group['proton_density'].max(),
                    'max_alpha': group['alpha_density'].max()
                }
                results['events'].append(event)
        
        if results['events']:
            results['cme_detected'] = True
            results['statistics'] = {
                'num_events': len(results['events']),
                'avg_duration': np.mean([e['duration'] for e in results['events']]),
                'max_speed': max([e['max_speed'] for e in results['events']]),
                'max_density': max([e['max_density'] for e in results['events']])
            }
    
    return results

def plot_cme_events(data, events):
    """Plot the detected CME events"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot speed
    ax1.plot(data.index, data['proton_bulk_speed'], label='Solar Wind Speed', color='tab:blue')
    ax1.axhline(y=450, color='r', linestyle='--', label='CME Threshold (450 km/s)')
    ax1.set_ylabel('Speed (km/s)')
    ax1.legend(loc='upper right')
    
    # Plot density
    ax2.plot(data.index, data['proton_density'], label='Proton Density', color='tab:orange')
    ax2.plot(data.index, data['density_ma'], label='30-point MA', color='tab:green', linestyle='--')
    ax2.set_ylabel('Density (cm$^{-3}$)')
    ax2.legend(loc='upper right')
    
    # Plot alpha ratio
    ax3.plot(data.index, data['alpha_density'], label='Alpha/Proton Ratio', color='tab:red')
    ax3.axhline(y=0.15, color='purple', linestyle='--', label='CME Threshold (15%)')
    ax3.set_ylabel('Alpha Ratio')
    ax3.legend(loc='upper right')
    
    # Highlight CME events
    for event in events:
        ax1.axvspan(event['start_time'], event['end_time'], color='red', alpha=0.3)
        ax2.axvspan(event['start_time'], event['end_time'], color='red', alpha=0.3)
        ax3.axvspan(event['start_time'], event['end_time'], color='red', alpha=0.3)
    
    # Format x-axis
    date_form = DateFormatter("%m-%d %H:%M")
    ax3.xaxis.set_major_formatter(date_form)
    plt.xlabel('Time')
    plt.suptitle('Halo CME Detection - May 25, 2025', y=0.98)
    plt.tight_layout()
    plt.savefig('halo_cme_detection.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    cdf_file = "AL1_ASW91_L2_BLK_20250525_UNP_9999_999999_V02.cdf"
    
    try:
        print(f"Loading CDF file: {cdf_file}")
        cdf = cdflib.CDF(cdf_file)
        
        # First print all available variables
        print("\nAvailable variables in CDF file:")
        cdf_info = cdf.cdf_info()
        for var in cdf_info.rVariables + cdf_info.zVariables:
            print(f"- {var}")
        
        # Manually specify variable names based on your CDF file
        var_mapping = {
            'time': 'epoch_for_cdf_mod',
            'density': 'proton_density',
            'speed': 'proton_bulk_speed',
            'alpha': 'alpha_density'
        }
        
        # Extract data
        time = cdflib.cdfepoch.to_datetime(cdf.varget(var_mapping['time']))
        data = pd.DataFrame({
            'time': time,
            'proton_density': cdf.varget(var_mapping['density']),
            'proton_bulk_speed': cdf.varget(var_mapping['speed']),
            'alpha_density': cdf.varget(var_mapping['alpha'])
        }).set_index('time')
        
        # Clean data
        print("\nData cleaning in progress...")
        clean_data = clean_data(data)
        print(f"Retained {len(clean_data)/len(data):.1%} of data after cleaning")
        
        # Run detection with relaxed thresholds
        print("\nRunning CME detection...")
        results = detect_halo_cme(clean_data, {
            'speed': 420,  # Reduced from 450
            'density_jump': 1.2,  # Reduced from 1.3
            'alpha_ratio': 0.12,  # Reduced from 0.15
            'min_duration': 1  # Allow single-point detections
        })
        
        # Output results
        print("\n=== Halo CME Detection Report ===")
        print(f"Time Period: {clean_data.index[0]} to {clean_data.index[-1]}")
        print(f"Data Resolution: {(clean_data.index[1]-clean_data.index[0]).total_seconds()} seconds")
        
        if results['cme_detected']:
            print(f"\nDetected {results['statistics']['num_events']} event(s):")
            for i, event in enumerate(results['events'], 1):
                print(f"\nEvent {i}:")
                print(f"  Time Range: {event['start_time']} to {event['end_time']}")
                print(f"  Duration: {event['duration']} time steps")
                print(f"  Max Speed: {event['max_speed']:.1f} km/s")
                print(f"  Max Density: {event['max_density']:.1f} cm^-3")
                print(f"  Max Alpha Ratio: {event['max_alpha']:.2%}")
            
            # Generate plot
            plot_cme_events(clean_data, results['events'])
            print("\nSaved visualization: 'halo_cme_detection.png'")
        else:
            print("\nNo CME events detected with current thresholds")
            print("\nRecommendations:")
            print("1. Check raw data plots for anomalies")
            print("2. Consider adjusting thresholds further if expecting events")
            print("3. Verify instrument operation during this period")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify CDF file exists at the specified path")
        print("2. Check the printed variable names match your expectations")
        print("3. Manually specify variable names in the code if needed")
