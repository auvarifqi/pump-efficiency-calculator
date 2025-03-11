import numpy as np
import matplotlib.pyplot as plt

# Function to calculate flow rate decline over time with periodic overhaul and operational factors
def calculate_flow_rate(years, initial_flow_rate, overhaul_drop, overhaul_interval, particle_concentration, ph):
    """
    Simulates pump flow rate decline over time with periodic overhaul and operational parameters.
    
    Args:
        years (int): Total years to simulate.
        initial_flow_rate (float): Initial flow rate of the pump (usgpm).
        overhaul_drop (float): Flow rate drop after each overhaul (%).
        overhaul_interval (int): Number of years between overhauls.
        particle_concentration (float): Sand particle concentration in fluid (%).
        ph (float): Average pH of fluid.
    
    Returns:
        list: Flow rate values over the years.
    """
    flow_rate = []
    current_flow_rate = initial_flow_rate
    
    # Parameters affecting efficiency decline
    particle_factor = particle_concentration * 0.005  # Effect of sand particles
    ph_factor = abs(7 - ph) * 0.01  # Effect of pH deviation from neutral
    
    for year in range(1, years + 1):
        flow_rate.append(current_flow_rate)
        
        # Check if it's time for an overhaul
        if year % overhaul_interval == 0:
            current_flow_rate *= (1 - overhaul_drop / 100)  # Reduce flow rate by overhaul drop percentage
        
        # Apply additional operational factors (non-linear decay)
        decay_rate = particle_factor + ph_factor
        current_flow_rate *= np.exp(-decay_rate)  # Exponential decay due to operational factors
    
    return flow_rate

# Function to plot flow rate over time
def plot_flow_rate(years, flow_rate):
    """
    Plots the flow rate decline over time.
    
    Args:
        years (int): Total years simulated.
        flow_rate (list): Flow rate values over the years.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, years + 1), flow_rate, marker='o', label="Flow Rate (usgpm)")
    plt.title("Flow Rate Decline Over Time with Operational Factors and Periodic Overhaul")
    plt.xlabel("Year")
    plt.ylabel("Flow Rate (usgpm)")
    plt.xticks(range(1, years + 1, 1))  # Increment x-axis by 1 year
    plt.legend()
    plt.grid()
    plt.show()

# Function to predict time until next failure based on parameters
def predict_time_until_failure(flow_rate, threshold):
    """
    Predicts the time until the pump's flow rate falls below the threshold.
    
    Args:
        flow_rate (list): List of flow rates over the years.
        threshold (float): Flow rate threshold for failure (usgpm).
    
    Returns:
        int: Years until failure.
    """
    for year, rate in enumerate(flow_rate, start=1):
        if rate <= threshold:
            return year
    return None  # If no failure occurs within the simulation period

# Input parameters
years = 15  # Simulation period in years
initial_flow_rate = 2800.0  # Initial pump flow rate (usgpm)
overhaul_drop = 10.0  # Flow rate drop after each overhaul (%)
overhaul_interval = 5  # Interval between overhauls (years)
threshold = 1500.0  # Flow rate threshold for failure (usgpm)

# Operational parameters
particle_concentration = 10.0  # Sand particle concentration in fluid (%)
ph = 8.0  # Average pH level of fluid

# Calculate and plot flow rate decline over time with periodic overhaul and operational factors
flow_rate = calculate_flow_rate(years, initial_flow_rate, overhaul_drop, overhaul_interval,
                                particle_concentration, ph)
plot_flow_rate(years, flow_rate)

# Predict time until next failure based on influencing factors
time_until_failure = predict_time_until_failure(flow_rate, threshold)
if time_until_failure:
    print(f"Time until next failure: {time_until_failure} years")
else:
    print("No failure occurs within the simulation period.")

# Display input parameters for reference
print("\n--- Input Parameters ---")
print(f"Initial Flow Rate: {initial_flow_rate} usgpm")
print(f"Overhaul Drop: {overhaul_drop}%")
print(f"Overhaul Interval: {overhaul_interval} years")
print(f"Threshold: {threshold} usgpm")
print(f"Sand Particle Concentration: {particle_concentration}%")
print(f"pH Level: {ph}")
