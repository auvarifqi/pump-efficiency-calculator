import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(
    page_title="Wip Performance Calculator",
    page_icon="🔄",
    layout="wide"
)

# Title and description
st.title("Wip Performance Calculator")
st.markdown("""
This application simulates pump efficiency decline over time with periodic overhauls triggered by threshold.
Enter your parameters in the sidebar and view the results.
""")

# Function to calculate efficiency decline over time with overhaul triggered by threshold
def calculate_efficiency_with_threshold(years, initial_efficiency, bep_ratio_drop, threshold, 
                                       particle_concentration, ph, chloride_concentration, 
                                       input_pressure, output_pressure, flow_rate):
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

# Sidebar for input parameters
st.sidebar.header("Input Parameters")

with st.sidebar.form("input_form"):
    years = st.slider("Simulation Period (Years)", 1, 30, 10)
    initial_efficiency = st.slider("Initial Pump Efficiency (%)", 50.0, 100.0, 85.0)
    bep_ratio_drop = st.slider("BEP Ratio Drop After Overhaul (%)", 0.0, 20.0, 5.0)
    threshold = st.slider("Efficiency Threshold for Overhaul (%)", 40.0, 80.0, 60.0)
    
    st.subheader("Operational Parameters")
    particle_concentration = st.slider("Sand Particle Concentration in Fluid (%)", 0.0, 5.0, 1.0, 0.1)
    ph = st.slider("Average pH Level of Fluid", 1.0, 14.0, 7.0, 0.1)
    chloride_concentration = st.slider("Chloride Concentration (ppm)", 0.0, 5000.0, 1000.0, 100.0)
    input_pressure = st.slider("Input Pressure of the Pump (psig)", 0.0, 1000.0, 200.0)
    output_pressure = st.slider("Output Pressure of the Pump (psig)", 0.0, 1000.0, 400.0)
    flow_rate = st.slider("Flow Rate of the Pump (usgpm)", 0.0, 10000.0, 2000.0)
    
    submit_button = st.form_submit_button(label="Calculate")

if submit_button or 'efficiency' in st.session_state:
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
    
    # Store in session state
    st.session_state.efficiency = efficiency
    st.session_state.yearly_drops = yearly_drops
    st.session_state.replace_year = replace_year
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Plot efficiency decline with a single threshold line
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(1, years + 1), efficiency[:years], marker='o', label="Efficiency (%)")
        ax.axhline(y=threshold, color='r', linestyle='--', label=f"Overhaul Threshold ({threshold}%)")
        
        ax.set_title("Efficiency Decline Over Time with Operational Factors")
        ax.set_xlabel("Year")
        ax.set_ylabel("Efficiency (%)")
        ax.set_xticks(range(1, years + 1, max(1, years // 10)))
        ax.legend()
        ax.grid(True)
        
        st.pyplot(fig)
    
    with col2:
        # Predict time until next failure and overhaul
        time_until_failure = predict_time_until_failure(efficiency, threshold)
        
        st.subheader("Analysis Results")
        
        if time_until_failure:
            st.info(f"Time until next overhaul (below {threshold}%): {time_until_failure} years")
        else:
            st.success(f"No overhaul needed within the simulation period.")
        
        # Predict when pump should be replaced
        if replace_year:
            st.error(f"Pump should be replaced at year: {replace_year}")
        else:
            st.success("Pump does not need replacement within the simulation period.")
    
    # Display yearly drops in efficiency as a dataframe
    st.subheader("Yearly Efficiency Analysis")
    
    # Create a DataFrame for the results
    data = {
        "Year": list(range(1, len(efficiency) + 1)),
        "Efficiency (%)": [round(eff, 2) for eff in efficiency],
        "Yearly Drop (%)": [round(drop, 2) for drop in yearly_drops] if yearly_drops else []
    }
    
    # Add empty values if lengths don't match
    max_len = max(len(data["Year"]), len(data["Efficiency (%)"]), len(data["Yearly Drop (%)"]))
    for key in data:
        while len(data[key]) < max_len:
            data[key].append(None)
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Display a download button for the data
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="pump_efficiency_analysis.csv",
        mime="text/csv",
    )
    
    # Display input parameters for reference
    st.subheader("Input Parameters Summary")
    
    params_data = {
        "Parameter": [
            "Initial Efficiency", 
            "BEP Ratio Drop After Overhaul", 
            "Threshold for Overhaul",
            "Sand Particle Concentration", 
            "pH Level", 
            "Chloride Concentration",
            "Input Pressure", 
            "Output Pressure", 
            "Flow Rate"
        ],
        "Value": [
            f"{initial_efficiency}%",
            f"{bep_ratio_drop}%",
            f"{threshold}%",
            f"{particle_concentration}%",
            f"{ph}",
            f"{chloride_concentration} ppm",
            f"{input_pressure} psig",
            f"{output_pressure} psig",
            f"{flow_rate} usgpm"
        ]
    }
    
    st.table(pd.DataFrame(params_data))

# Add footer
st.markdown("---")
st.markdown("© 2025 Wip Performance Calculator | All Rights Reserved")