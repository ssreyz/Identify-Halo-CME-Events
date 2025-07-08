import pandas as pd
import numpy as np
from datetime import datetime

def create_cme_dataset(input_csv, output_csv=None):
    """
    Creates a new CSV with CME detection parameters from SWIS data.
    
    Args:
        input_csv (str): Path to input SWIS CSV file
        output_csv (str, optional): Output file path. Defaults to input path + '_cme.csv'
    
    Returns:
        str: Path to created output file
    """
    try:
        # Read input data
        df = pd.read_csv(input_csv)
        
        # Ensure required columns exist
        required_cols = ['time', 'proton_density', 'proton_thermal', 
                        'proton_bulk_speed', 'alpha_density']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert time to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        
        # --- Calculate CME Parameters ---
        # 1. Expected temperature and anomaly
        df['T_exp'] = 5.8e4 * df['proton_bulk_speed']**1.96
        df['T_anomaly'] = df['proton_thermal'] / df['T_exp']
        
        # 2. Alpha-proton ratio (%)
        df['alpha_ratio'] = (df['alpha_density'] / df['proton_density']) * 100
        
        # 3. Dynamic pressure (nPa)
        df['dynamic_pressure'] = 1.67e-6 * df['proton_density'] * (df['proton_bulk_speed']**2)
        
        # 4. Speed changes (km/s)
        df['speed_change'] = df['proton_bulk_speed'].diff()
        
        # 5. CME flags (modify thresholds as needed)
        conditions = (
            (df['proton_density'] > 15) &          # High density threshold
            (df['T_anomaly'] < 0.8) &             # Cool plasma
            (df['alpha_ratio'] > 8) &             # Enhanced alpha particles
            (df['speed_change'].abs() > 50)        # Sudden speed change
        )
        df['CME_flag'] = np.where(conditions, 1, 0)
        
        # 6. CME probability score (simple example)
        df['CME_score'] = (
            0.4 * (df['proton_density'] / 30) +           # Normalized density
            0.3 * (1 - df['T_anomaly']) +                # Temperature anomaly
            0.2 * (df['alpha_ratio'] / 15) +             # Alpha ratio
            0.1 * (df['speed_change'].abs() / 100)       # Speed change
        
        # Select only relevant columns for output
        output_cols = [
            'time', 'proton_density', 'proton_thermal', 'proton_bulk_speed',
            'T_exp', 'T_anomaly', 'alpha_ratio', 'dynamic_pressure',
            'speed_change', 'CME_flag', 'CME_score'
        ]
        cme_df = df[output_cols].copy()
        
        # Set output path
        if output_csv is None:
            base = os.path.splitext(input_csv)[0]
            output_csv = f"{base}_cme.csv"
        
        # Save to CSV
        cme_df.to_csv(output_csv, index=False)
        print(f"Successfully created CME dataset at: {output_csv}")
        print(f"CME events detected: {cme_df['CME_flag'].sum()}")
        
        return output_csv
        
    except Exception as e:
        print(f"Error creating CME dataset: {str(e)}")
        return None

# Example usage:
create_cme_dataset("cleanDataset\AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02_cleaned.csv", "output/cme_parameters.csv")