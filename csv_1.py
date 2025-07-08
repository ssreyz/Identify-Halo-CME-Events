import cdflib
import pandas as pd
import numpy as np
from cdflib.epochs import CDFepoch
import os

def convert_swis_cdf_to_csv(cdf_file_path, output_dir=None):
    """
    Converts a SWIS CDF file to CSV format with all requested variables.
    
    Args:
        cdf_file_path (str): Path to the input CDF file
        output_dir (str, optional): Directory to save CSV files. Defaults to same as input file.
    
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Open the CDF file
        cdf = cdflib.CDF(cdf_file_path)
        
        # Get information about variables in the file
        cdf_info = cdf.cdf_info()
        all_vars = cdf_info.zVariables + cdf_info.rVariables
        print(f"\nProcessing {os.path.basename(cdf_file_path)}")
        print("Available variables:", all_vars)
        
        # Create a dictionary to store the data
        data_dict = {}
        
        # List of required variables
        required_vars = [
            'epoch_for_cdf_mod', 
            'proton_density', 'numden_p_uncer',
            'proton_bulk_speed', 'bulk_p_uncer',
            'proton_xvelocity', 'proton_yvelocity', 'proton_zvelocity',
            'proton_thermal', 'thermal_p_uncer',
            'alpha_density', 'numden_a_uncer',
            'alpha_bulk_speed', 'bulk_a_uncer',
            'alpha_thermal', 'thermal_a_uncer',
            'spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos'
        ]
        
        # 1. Process time variable
        if 'epoch_for_cdf_mod' in all_vars:
            time_var = cdf.varget('epoch_for_cdf_mod')
            try:
                # Convert CDF epoch time to datetime
                data_dict['time'] = CDFepoch.to_datetime(time_var)
            except Exception as e:
                print(f"Warning: Could not convert time variable: {str(e)}")
                data_dict['time'] = time_var
        else:
            raise ValueError("Required time variable 'epoch_for_cdf_mod' not found")
        
        # 2. Process all other required variables
        for var in required_vars:
            if var == 'epoch_for_cdf_mod':
                continue  # Already processed
                
            if var in all_vars:
                data = cdf.varget(var)
                if data is not None:
                    # Convert to numpy array and flatten if necessary
                    data = np.array(data).flatten()
                    data_dict[var] = data
                else:
                    print(f"Warning: {var} exists but contains no data")
            else:
                print(f"Warning: Required variable {var} not found in CDF file")
                data_dict[var] = np.nan  # Fill with NaN if missing
        
        # Create DataFrame
        df = pd.DataFrame(data_dict)
        
        # Determine output path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(cdf_file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}.csv")
        else:
            output_file = os.path.splitext(cdf_file_path)[0] + '.csv'
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Successfully exported data to {output_file}")
        
        # Show a preview of the data
        print("\nData preview:")
        print(df.head())
        print(f"\nData shape: {df.shape}")
        
        return output_file

    except Exception as e:
        print(f"Error processing {cdf_file_path}: {str(e)}")
        return None

# Batch processing function
def batch_convert_swis_cdf(input_dir, output_dir):
    """
    Processes all SWIS CDF files in a directory
    Args:
        input_dir (str): Directory containing CDF files
        output_dir (str): Directory to save CSV files
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory {input_dir} not found")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for file in os.listdir(input_dir):
        if file.endswith('.cdf'):
            cdf_path = os.path.join(input_dir, file)
            convert_swis_cdf_to_csv(cdf_path, output_dir)

# Example usage for single file
# convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02.cdf", "csv")

# Example usage for batch processing
# batch_convert_swis_cdf("input_cdf_directory", "output_csv_directory")

# Process your specific files
convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02.cdf", "csv")
convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250701_UNP_9999_999999_V02.cdf", "csv")
convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250703_UNP_9999_999999_V02.cdf", "csv")
convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250704_UNP_9999_999999_V02.cdf", "csv")
convert_swis_cdf_to_csv("AL1_ASW91_L2_BLK_20250705_UNP_9999_999999_V02.cdf", "csv")