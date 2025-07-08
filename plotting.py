import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime


def plot_swis_data(filename):
    """
    Plot available data from SWIS CSV file
    Args:
        filename (str): Path to CSV file
    """
    try:
        # Verify file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} not found in {os.getcwd()}")

        # Read CSV file
        df = pd.read_csv(filename)
        
        # Print available columns for debugging
        print(f"Available columns: {df.columns.tolist()}")

        # Convert time column to datetime (using lowercase 'time' as per your data)
        if 'time' not in df.columns:
            raise ValueError("CSV file must contain 'time' column")
        time_data = pd.to_datetime(df['time'])
        
        # Create plots
        plt.figure(figsize=(15, 10))

        # Plot 1: Proton Density and Alpha Density
        plt.subplot(2, 1, 1)
        
        if 'proton_density' in df.columns:
            plt.plot(time_data, df['proton_density'], 'b-', label='Proton Density')
            if 'numden_p_uncer' in df.columns:
                plt.fill_between(time_data, 
                               df['proton_density'] - df['numden_p_uncer'],
                               df['proton_density'] + df['numden_p_uncer'],
                               color='b', alpha=0.2)
        
        if 'alpha_density' in df.columns:
            plt.plot(time_data, df['alpha_density'], 'r-', label='Alpha Density')
            if 'numden_a_uncer' in df.columns:
                plt.fill_between(time_data,
                               df['alpha_density'] - df['numden_a_uncer'],
                               df['alpha_density'] + df['numden_a_uncer'],
                               color='r', alpha=0.2)
        
        plt.ylabel('Density (cm⁻³)')
        plt.title('Solar Wind Ion Densities')
        plt.legend()
        plt.grid(True)

        # Plot 2: Bulk Speeds
        plt.subplot(2, 1, 2)
        
        if 'proton_bulk_speed' in df.columns:
            plt.plot(time_data, df['proton_bulk_speed'], 'b-', label='Proton Bulk Speed')
            if 'bulk_p_uncer' in df.columns:
                plt.fill_between(time_data,
                               df['proton_bulk_speed'] - df['bulk_p_uncer'],
                               df['proton_bulk_speed'] + df['bulk_p_uncer'],
                               color='b', alpha=0.2)
        
        if 'alpha_bulk_speed' in df.columns:
            plt.plot(time_data, df['alpha_bulk_speed'], 'r-', label='Alpha Bulk Speed')
            if 'bulk_a_uncer' in df.columns:
                plt.fill_between(time_data,
                               df['alpha_bulk_speed'] - df['bulk_a_uncer'],
                               df['alpha_bulk_speed'] + df['bulk_a_uncer'],
                               color='r', alpha=0.2)
        
        plt.ylabel('Speed (km/s)')
        plt.title('Solar Wind Ion Bulk Speeds')
        plt.legend()
        plt.grid(True)

        plt.xlabel('Time')
        plt.tight_layout()
        plt.show()

        # Additional plot for thermal speeds if available
        if 'proton_thermal' in df.columns or 'alpha_thermal' in df.columns:
            plt.figure(figsize=(15, 5))
            
            if 'proton_thermal' in df.columns:
                plt.plot(time_data, df['proton_thermal'], 'b-', label='Proton Thermal Speed')
                if 'thermal_p_uncer' in df.columns:
                    plt.fill_between(time_data,
                                   df['proton_thermal'] - df['thermal_p_uncer'],
                                   df['proton_thermal'] + df['thermal_p_uncer'],
                                   color='b', alpha=0.2)
            
            if 'alpha_thermal' in df.columns:
                plt.plot(time_data, df['alpha_thermal'], 'r-', label='Alpha Thermal Speed')
                if 'thermal_a_uncer' in df.columns:
                    plt.fill_between(time_data,
                                   df['alpha_thermal'] - df['thermal_a_uncer'],
                                   df['alpha_thermal'] + df['thermal_a_uncer'],
                                   color='r', alpha=0.2)
            
            plt.ylabel('Thermal Speed (km/s)')
            plt.title('Solar Wind Ion Thermal Speeds')
            plt.legend()
            plt.grid(True)
            plt.xlabel('Time')
            plt.tight_layout()
            plt.show()

    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")


# Example usage
filename = "cleanDataset/AL1_ASW91_L2_BLK_20250630_UNP_9999_999999_V02_cleaned.csv"
plot_swis_data(filename)