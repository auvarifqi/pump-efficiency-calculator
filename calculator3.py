import numpy as np
import matplotlib.pyplot as plt

# Function to calculate efficiency decline over time with overhaul triggered by threshold
def calculate_efficiency_with_threshold(years, initial_efficiency, overhaul_drop, threshold, particle_concentration, ph, chloride_concentration, input_pressure, output_pressure):
    """
    Simulates pump efficiency decline over time with periodic overhaul triggered by threshold.
    
    Args:
        years (int): Total years to simulate.
        initial_efficiency (float): Initial efficiency of the pump (%).
        overhaul_drop (float): Efficiency drop after each overhaul (%).
        threshold (float): Efficiency threshold for triggering overhaul (%).
        particle_concentration (float): Sand particle concentration in fluid (%).
        ph (float): Average pH of fluid.
        chloride_concentration (float): Chloride concentration in ppm.
        input_pressure (float): Input pressure of the pump (psi).
        output_pressure (float): Output pressure of the pump (psi).
    
    Returns:
        list: Efficiency values over the years.
    """
    efficiency = []
    current_efficiency = initial_efficiency
    original_efficiency = initial_efficiency  # Store the original efficiency for resetting after overhaul
    
    # Parameters affecting efficiency decline
    particle_factor = particle_concentration * 0.005  # Effect of sand particles
    ph_factor = abs(7 - ph) * 0.01  # Effect of pH deviation from neutral
    chloride_factor = chloride_concentration * 0.001  # Effect of chloride ions
    pressure_factor = (input_pressure - output_pressure) * 0.0005  # Effect of pressure difference
    
    for year in range(1, years + 1):
        efficiency.append(current_efficiency)
        
        # Apply operational factors (non-linear decay)
        decay_rate = particle_factor + ph_factor + chloride_factor + pressure_factor
        current_efficiency *= np.exp(-decay_rate)  # Exponential decay due to operational factors
        
        # Check if efficiency hits or falls below the threshold
        if current_efficiency <= threshold:
            current_efficiency = original_efficiency * (1 - overhaul_drop / 100)  # Reset efficiency after overhaul
            original_efficiency = current_efficiency  # Update original efficiency for next cycle
    
    return efficiency

# Function to plot efficiency over time
def plot_efficiency(years, efficiency, threshold):
    """
    Plots the efficiency decline over time.
    
    Args:
        years (int): Total years simulated.
        efficiency (list): Efficiency values over the years.
        threshold (float): Efficiency threshold for triggering overhaul (%).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, years + 1), efficiency, marker='o', label="Efficiency (%)")
    plt.axhline(y=threshold, color='r', linestyle='--', label=f"Threshold ({threshold}%)")
    plt.title("Efficiency Decline Over Time with Operational Factors and Overhaul Triggered by Threshold")
    plt.xlabel("Year")
    plt.ylabel("Efficiency (%)")
    plt.xticks(range(1, years + 1, 1))  # Increment x-axis by 1 year
    plt.legend()
    plt.grid()
    plt.show()

# Function to predict time until next failure based on parameters
def predict_time_until_failure(efficiency, threshold):
    """
    Predicts the time until the pump's efficiency falls below the threshold.
    
    Args:
        efficiency (list): List of efficiencies over the years.
        threshold (float): Efficiency threshold for failure (%).
    
    Returns:
        int: Years until failure.
    """
    for year, eff in enumerate(efficiency, start=1):
        if eff <= threshold:
            return year
    return None  # If no failure occurs within the simulation period

# Input parameters
years = 15  # Simulation period in years
initial_efficiency = 85.0  # Initial pump efficiency (%)
overhaul_drop = 10.0  # Efficiency drop after each overhaul (%)
threshold = 40.0  # Efficiency threshold for triggering overhaul (%)

# Operational parameters
particle_concentration = 10.0  # Sand particle concentration in fluid (%)
ph = 8.0  # Average pH level of fluid
chloride_concentration = 50.0  # Chloride concentration in ppm
input_pressure = 100.0  # Input pressure of the pump (psi)
output_pressure = 80.0  # Output pressure of the pump (psi)

# Calculate and plot efficiency decline over time with periodic overhaul triggered by threshold
efficiency = calculate_efficiency_with_threshold(years, initial_efficiency, overhaul_drop, threshold,
                                                 particle_concentration, ph, chloride_concentration,
                                                 input_pressure, output_pressure)
plot_efficiency(years, efficiency, threshold)

# Predict time until next failure based on influencing factors
time_until_failure = predict_time_until_failure(efficiency, threshold)
if time_until_failure:
    print(f"Time until next failure: {time_until_failure} years")
else:
    print("No failure occurs within the simulation period.")

# Display input parameters for reference
print("\n--- Input Parameters ---")
print(f"Initial Efficiency: {initial_efficiency}%")
print(f"Overhaul Drop: {overhaul_drop}%")
print(f"Threshold: {threshold}%")
print(f"Sand Particle Concentration: {particle_concentration}%")
print(f"pH Level: {ph}")
print(f"Chloride Concentration: {chloride_concentration} ppm")
print(f"Input Pressure: {input_pressure} psi")
print(f"Output Pressure: {output_pressure} psi")
