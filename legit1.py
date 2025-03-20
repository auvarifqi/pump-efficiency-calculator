# -*- coding: utf-8 -*-
"""legit1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Xy9rTPDHvhwLTT5enTMBqbMa4B28zF_5
"""

import numpy as np
import matplotlib.pyplot as plt

# Function to calculate efficiency decline over time with overhaul triggered by threshold
def calculate_efficiency_with_threshold(years, initial_efficiency, bep_ratio_drop, threshold, particle_concentration, ph, chloride_concentration, input_pressure, output_pressure, flow_rate):
    """
    Simulates pump efficiency decline over time with periodic overhaul triggered by threshold.

    Args:
        years (int): Total years to simulate.
        initial_efficiency (float): Initial efficiency of the pump (%).
        bep_ratio_drop (float): BEP ratio drop after each overhaul (%).
        threshold (float): Efficiency threshold for triggering overhaul (%).
        particle_concentration (float): Sand particle concentration in fluid (%).
        ph (float): Average pH of fluid.
        chloride_concentration (float): Chloride concentration in ppm.
        input_pressure (float): Input pressure of the pump (psig).
        output_pressure (float): Output pressure of the pump (psig).
        flow_rate (float): Flow rate of the pump (usgpm).

    Returns:
        list: Efficiency values over the years.
        list: Yearly efficiency drops.
        int: Year when pump should be replaced.
    """
    efficiency = []
    yearly_drops = []
    current_efficiency = initial_efficiency
    original_efficiency = initial_efficiency
    replace_year = None

    # Parameters affecting efficiency decline
    particle_factor = particle_concentration * 0.005
    ph_factor = abs(7 - ph) * 0.01
    chloride_factor = chloride_concentration * 0.001
    pressure_factor = abs(input_pressure - output_pressure) * 0.0005
    flow_factor = flow_rate * 0.0001

    for year in range(1, years + 1):
        if current_efficiency <= threshold:
            post_overhaul_efficiency = original_efficiency * (1 - bep_ratio_drop / 100)
            if post_overhaul_efficiency < 50:
                replace_year = year
                break
            current_efficiency = post_overhaul_efficiency
            original_efficiency = current_efficiency

        efficiency.append(current_efficiency)

        # Adjust decay rate dynamically based on operational parameters
        base_factor = 0.10  # Adjusted base factor to target 9-11% range
        decay_factor = base_factor + particle_factor + ph_factor + chloride_factor + pressure_factor + flow_factor

        # Calculate percentage drop (between 9-11%)
        percent_drop = max(9.0, min(11.0, decay_factor * 100))

        # Calculate actual drop amount based on percentage
        yearly_drop = current_efficiency * (percent_drop / 100)
        yearly_drops.append(yearly_drop)

        current_efficiency -= yearly_drop

        if current_efficiency < 0:
            current_efficiency = 0

    while len(efficiency) < years:
        efficiency.append(efficiency[-1])

    return efficiency[:years], yearly_drops[:years], replace_year

# Function to plot efficiency over time with a single threshold line
def plot_efficiency_with_threshold(years, efficiency, threshold):
    """
    Plots the efficiency decline over time with a single threshold line for overhaul.

    Args:
        years (int): Total years simulated.
        efficiency (list): Efficiency values over the years.
        threshold (float): Efficiency threshold for triggering overhaul (%).
    """
    plt.figure(figsize=(10, 6))

    plt.plot(range(1, years + 1), efficiency[:years], marker='o', label="Efficiency (%)")
    plt.axhline(y=threshold, color='r', linestyle='--', label=f"Overhaul Threshold ({threshold}%)")  # Single threshold line

    plt.title("Efficiency Decline Over Time with Operational Factors and Overhaul Triggered by Threshold")
    plt.xlabel("Year")
    plt.ylabel("Efficiency (%)")
    plt.xticks(range(1, years + 1))
    plt.legend()
    plt.grid()
    plt.show()

# Function to predict time until next failure based on parameters
def predict_time_until_failure(efficiency, threshold=50.0):
    """
    Predicts the time until the pump's efficiency falls below the threshold.

    Args:
        efficiency (list): List of efficiencies over the years.
        threshold (float): Efficiency threshold for failure (%). Defaults to 50.0.

    Returns:
        int: Years until failure.
    """
    for year, eff in enumerate(efficiency, start=1):
        if eff <= threshold:
            return year
    return None

# Input parameters
years = int(input("Simulation Period (Years): "))
initial_efficiency = float(input("Initial Pump Efficiency (%): "))
bep_ratio_drop = float(input("BEP Ratio Drop After Overhaul (%): "))
threshold = float(input("Efficiency Threshold for Overhaul (%): "))  # Single input for one threshold
particle_concentration = float(input("Sand Particle Concentration in Fluid (%): "))
ph = float(input("Average pH Level of Fluid: "))
chloride_concentration = float(input("Chloride Concentration in ppm: "))
input_pressure = float(input("Input Pressure of the Pump (psig): "))
output_pressure = float(input("Output Pressure of the Pump (psig): "))
flow_rate = float(input("Flow Rate of the Pump (usgpm): "))

# Simulate efficiency decline and yearly drops
efficiency, yearly_drops, replace_year = calculate_efficiency_with_threshold(
    years,
    initial_efficiency,
    bep_ratio_drop,
    threshold,
    particle_concentration,
    ph,
    chloride_concentration,
    input_pressure,
    output_pressure,
    flow_rate,
)

# Plot efficiency decline with a single threshold line
plot_efficiency_with_threshold(years, efficiency, threshold)

# Predict time until next failure and overhaul
time_until_failure = predict_time_until_failure(efficiency)

if time_until_failure:
    print(f"Time until next failure (below {threshold}%): {time_until_failure} years")
else:
    print(f"No failure occurs within the simulation period.")

# Predict when pump should be replaced
if replace_year:
    print(f"Pump should be replaced at year: {replace_year}")
else:
    print("Pump does not need replacement within the simulation period.")

# Display yearly drops in efficiency
print("\nYearly Efficiency Drops:")
for year in range(1, len(yearly_drops) + 1):
    print(f"Year {year}: {yearly_drops[year - 1]:.2f}%")

# Display input parameters for reference
print("\n--- Input Parameters ---")
print(f"Initial Efficiency: {initial_efficiency}%")
print(f"BEP Ratio Drop After Overhaul: {bep_ratio_drop}%")
print(f"Threshold for Overhaul: {threshold}%")
print(f"Sand Particle Concentration: {particle_concentration}%")
print(f"pH Level: {ph}")
print(f"Chloride Concentration: {chloride_concentration} ppm")
print(f"Input Pressure: {input_pressure} psig")
print(f"Output Pressure: {output_pressure} psig")
print(f"Flow Rate: {flow_rate} usgpm")