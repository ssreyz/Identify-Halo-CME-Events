import cdflib
import pandas as pd
import numpy as np
from cdflib.epochs import CDFepoch
import os
from datetime import datetime
import warnings

def convert_swis_cdf_to_csv(cdf_file_path, output_dir=None):
    """
    Convert SWIS CDF file to CSV format with basic structure
    Args:
        cdf_file_path (str): Path to input CDF file
        output_dir (str, optional): Output directory for CSV
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Open CDF file
        cdf = cdflib.CDF(cdf_file_path)
        cdf_info = cdf.cdf_info()
        all_vars = cdf_info.zVariables + cdf_info.rVariables
        
        # Create data dictionary
        data_dict = {}
        
        # 1. Process time variable
        if 'epoch_for_cdf_mod' in all_vars:
            epoch_data = cdf.varget('epoch_for_cdf_mod')
            data_dict['time'] = CDFepoch.to_datetime(epoch_data)
        else:
            raise ValueError("Time variable 'epoch_for_cdf_mod' not found")
        
        # 2. Process all science variables
        science_vars = [
            'proton_density', 'numden_p_uncer', 'proton_bulk_speed', 'bulk_p_uncer',
            'proton_xvelocity', 'proton_yvelocity', 'proton_zvelocity',
            'proton_thermal', 'thermal_p_uncer', 'alpha_density', 'numden_a_uncer',
            'alpha_bulk_speed', 'bulk_a_uncer', 'alpha_thermal', 'thermal_a_uncer',
            'spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos'
        ]
        
        for var in science_vars:
            if var in all_vars:
                data = cdf.varget(var)
                if data is not None:
                    data_dict[var] = np.array(data)
        
        # Create DataFrame
        df = pd.DataFrame(data_dict)
        
        # Set output path
        base_name = os.path.splitext(os.path.basename(cdf_file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.csv") if output_dir else f"{base_name}.csv"
        
        # Save initial CSV
        df.to_csv(output_path, index=False)
        print(f"Initial CSV saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error converting {cdf_file_path}: {str(e)}")
        return None

def clean_swis_data(input_csv, output_csv=None):
    """
    Clean SWIS CSV data with physics-based rules
    Args:
        input_csv (str): Path to input CSV file
        output_csv (str, optional): Path for cleaned output
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    try:
        # Read CSV
        df = pd.read_csv(input_csv)
        
        # Convert time
        df['time'] = pd.to_datetime(df['time'])
        
        # 1. Replace fill values
        fill_values = [-1e31, -9999, -999.99, 999.99, 9999]
        df.replace(fill_values, np.nan, inplace=True)
        
        # 2. Physics-based cleaning
        # Density (must be positive)
        for density in ['proton_density', 'alpha_density']:
            if density in df.columns:
                df[density] = df[density].clip(lower=0, upper=100)
        
        # Temperature (must be positive)
        for temp in ['proton_thermal', 'alpha_thermal']:
            if temp in df.columns:
                df[temp] = df[temp].clip(lower=0, upper=1e5)
        
        # Velocity validation
        if all(v in df.columns for v in ['proton_xvelocity', 'proton_yvelocity', 'proton_zvelocity']):
            speed_mag = np.sqrt(df['proton_xvelocity']**2 + 
                             df['proton_yvelocity']**2 + 
                             df['proton_zvelocity']**2)
            df = df[np.abs(speed_mag - df['proton_bulk_speed']) < 100]
        
        # 3. Time-based cleaning
        df.sort_values('time', inplace=True)
        df.drop_duplicates(subset=['time'], inplace=True)
        
        # 4. Uncertainty filtering
        for param, uncert in [('proton_density', 'numden_p_uncer'),
                             ('proton_bulk_speed', 'bulk_p_uncer'),
                             ('alpha_density', 'numden_a_uncer')]:
            if uncert in df.columns:
                df.loc[df[uncert] > (0.5 * df[param].abs()), param] = np.nan
        
        # 5. Spacecraft position validation
        pos_cols = ['spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos']
        if all(col in df.columns for col in pos_cols):
            pos_diff = df[pos_cols].diff().abs()
            df = df[(pos_diff < 1000).all(axis=1) | (pos_diff.isna().all(axis=1))]
        
        # 6. Time interpolation (small gaps only)
        df.set_index('time', inplace=True)
        df = df.interpolate(method='time', limit=5).reset_index()
        
        # Save cleaned data
        if output_csv:
            df.to_csv(output_csv, index=False)
            print(f"Cleaned data saved to {output_csv}")
        
        return df
        
    except Exception as e:
        print(f"Error cleaning {input_csv}: {str(e)}")
        return None

def process_swis_data(cdf_file_path, output_dir=None):
    """
    Complete processing pipeline: CDF → CSV → Cleaned CSV
    Args:
        cdf_file_path (str): Path to input CDF file
        output_dir (str, optional): Output directory
    Returns:
        tuple: (raw_csv_path, cleaned_csv_path)
    """
    # Convert CDF to CSV
    raw_csv = convert_swis_cdf_to_csv(cdf_file_path, output_dir)
    if raw_csv is None:
        return None, None
    
    # Clean the CSV
    base_name = os.path.splitext(raw_csv)[0]
    cleaned_csv = f"{base_name}_cleaned.csv"
    clean_swis_data(raw_csv, cleaned_csv)
    
    return raw_csv, cleaned_csv

def batch_process_swis_data(cdf_directory, output_dir=None):
    """
    Process all CDF files in a directory
    Args:
        cdf_directory (str): Directory containing CDF files
        output_dir (str, optional): Output directory
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file in os.listdir(cdf_directory):
        if file.endswith('.cdf'):
            cdf_path = os.path.join(cdf_directory, file)
            print(f"\nProcessing {file}...")
            raw_csv, cleaned_csv = process_swis_data(cdf_path, output_dir)
            if cleaned_csv:
                print(f"Successfully processed to {cleaned_csv}")

if __name__ == "__main__":
    # Example usage:
    
    # For processing CDF files in a directory:
    # batch_process_swis_data("path/to/cdf/files", "output_directory")
    
    # For processing individual CSV files (already converted from CDF):
    input_csvs = [
        "csv/AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02.csv",
        "csv/AL1_ASW91_L2_BLK_20250701_UNP_9999_999999_V02.csv",
        "csv/AL1_ASW91_L2_BLK_20250703_UNP_9999_999999_V02.csv",
        "csv/AL1_ASW91_L2_BLK_20250704_UNP_9999_999999_V02.csv",
        "csv/AL1_ASW91_L2_BLK_20250705_UNP_9999_999999_V02.csv"
    ]
    
    for csv_file in input_csvs:
        print(f"\nCleaning {csv_file}...")
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        cleaned_csv = os.path.join("cleanDataset", f"{base_name}_cleaned.csv")
        
        # Create output directory if it doesn't exist
        os.makedirs("cleanDataset", exist_ok=True)
        
        clean_swis_data(csv_file, cleaned_csv)
        print(f"Cleaned data saved to {cleaned_csv}")