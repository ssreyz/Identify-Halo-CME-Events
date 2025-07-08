import cdflib
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime, timedelta


def plot_swis_data(filename):
    """
    Plot available data from SWIS CDF file
    Args:
        filename (str): Path to CDF file
    """
    try:
        # Verify file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} not found in {os.getcwd()}")

        # Open CDF file
        cdf = cdflib.CDF(filename)

        # Get variable information
        variables = cdf.cdf_info().zVariables
        print(f"Available variables: {variables}")

        # Extract time data (using the actual epoch variable name)
        if 'epoch_for_cdf_mod' in variables:
            epoch_data = cdf.varget('epoch_for_cdf_mod')
            time_data = cdflib.cdfepoch.to_datetime(epoch_data)
        else:
            raise ValueError("No epoch variable found in CDF file")

        # Extract flux data (using the actual variable names)
        flux_data = {}
        if 'integrated_flux_mod' in variables:
            flux_data['Total Flux'] = cdf.varget('integrated_flux_mod')

        # Extract sector fluxes if available
        for sector in range(9, 12):
            var_name = f'integrated_flux_s{sector}_mod'
            if var_name in variables:
                flux_data[f'Sector {sector} Flux'] = cdf.varget(var_name)

        # Create plots
        plt.figure(figsize=(15, 10))

        # Plot 1: Total Flux (if available)
        if 'Total Flux' in flux_data:
            plt.subplot(2, 1, 1)
            plt.plot(time_data, flux_data['Total Flux'], 'b-', label='Total Integrated Flux')
            plt.ylabel('Flux (particles/cm²/sr/s)')
            plt.title('SWIS Total Particle Flux')
            plt.legend()
            plt.grid(True)

        # Plot 2: Sector Fluxes (if available)
        if len(flux_data) > 1:  # If we have sector data
            plt.subplot(2, 1, 2)
            for label, data in flux_data.items():
                if label != 'Total Flux':
                    plt.plot(time_data, data, label=label)
            plt.ylabel('Sector Flux (particles/cm²/sr/s)')
            plt.title('SWIS Sector Particle Fluxes')
            plt.legend()
            plt.grid(True)

        plt.xlabel('Time')
        plt.tight_layout()
        plt.show()

        # Additional plot for energy spectrum if available
        if 'energy_center_mod' in variables:
            energy_data = cdf.varget('energy_center_mod')
            plt.figure(figsize=(12, 6))
            plt.plot(energy_data, 'ro-')
            plt.xlabel('Energy Channel')
            plt.ylabel('Energy (keV)')
            plt.title('SWIS Energy Channels')
            plt.grid(True)
            plt.show()

    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")


# Example usage
filename = "AL1_ASW91_L2_TH1_20250704_UNP_9999_999999_V02.cdf"
plot_swis_data(filename)

