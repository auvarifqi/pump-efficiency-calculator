import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(
    page_title="Pump Flow Rate Calculator Reka",
    page_icon="💧",
    layout="wide"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .info-text {
        background-color: #0D47A1;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Pump Flow Rate Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p class='info-text'>This application simulates pump flow rate decline over time considering periodic overhauls and operational factors.</p>", unsafe_allow_html=True)

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

# Create sidebar for input parameters
st.sidebar.markdown("<h2 class='sub-header'>Simulation Parameters</h2>", unsafe_allow_html=True)

# Basic parameters
with st.sidebar.expander("Basic Parameters", expanded=True):
    years = st.slider("Simulation Period (Years)", min_value=1, max_value=30, value=15, step=1)
    initial_flow_rate = st.number_input("Initial Pump Flow Rate (usgpm)", min_value=500.0, max_value=5000.0, value=2800.0, step=100.0)
    threshold = st.number_input("Flow Rate Threshold for Failure (usgpm)", min_value=500.0, max_value=3000.0, value=1500.0, step=100.0)

# Overhaul parameters
with st.sidebar.expander("Overhaul Parameters", expanded=True):
    overhaul_interval = st.slider("Interval Between Overhauls (Years)", min_value=1, max_value=10, value=5, step=1)
    overhaul_drop = st.slider("Flow Rate Drop After Each Overhaul (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

# Operational parameters
with st.sidebar.expander("Operational Parameters", expanded=True):
    particle_concentration = st.slider("Sand Particle Concentration (%)", min_value=0.0, max_value=20.0, value=10.0, step=0.5)
    ph = st.slider("Average pH Level", min_value=1.0, max_value=14.0, value=8.0, step=0.1)

# Main content area - split into two columns
col1, col2 = st.columns([2, 1])

# Calculate flow rate based on user inputs
flow_rate = calculate_flow_rate(years, initial_flow_rate, overhaul_drop, overhaul_interval,
                                particle_concentration, ph)

# Create and display the plot in the first column
with col1:
    st.markdown("<h2 class='sub-header'>Flow Rate Decline Over Time</h2>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(1, years + 1), flow_rate, marker='o', linestyle='-', color='#1976D2', linewidth=2, markersize=6)
    
    # Mark overhaul years with vertical lines
    for year in range(overhaul_interval, years + 1, overhaul_interval):
        ax.axvline(x=year, color='red', linestyle='--', alpha=0.5)
    
    # Mark threshold
    ax.axhline(y=threshold, color='red', linestyle='-', label=f"Failure Threshold ({threshold} usgpm)")
    
    ax.set_title("Pump Flow Rate Decline Over Time", fontsize=16)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Flow Rate (usgpm)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(1, years + 1, 1 if years <= 15 else 2))
    ax.legend()
    
    st.pyplot(fig)

    # Display data table
    st.markdown("<h3 class='sub-header'>Year-by-Year Data</h3>", unsafe_allow_html=True)
    df = pd.DataFrame({
        'Year': range(1, years + 1),
        'Flow Rate (usgpm)': [round(rate, 2) for rate in flow_rate],
        'Overhaul Year': ['Yes' if year % overhaul_interval == 0 else 'No' for year in range(1, years + 1)]
    })
    st.dataframe(df, hide_index=True)

# Results and analysis in the second column
with col2:
    st.markdown("<h2 class='sub-header'>Results & Analysis</h2>", unsafe_allow_html=True)
    
    # Calculate time until failure
    time_until_failure = predict_time_until_failure(flow_rate, threshold)
    
    # Create a metrics container
    st.markdown("### Key Metrics")
    metric_col1, metric_col2 = st.columns(2)
    
    with metric_col1:
        st.metric(
            label="Initial Flow Rate",
            value=f"{initial_flow_rate} usgpm"
        )
        
        st.metric(
            label="Final Flow Rate",
            value=f"{round(flow_rate[-1], 2)} usgpm",
            delta=f"{round((flow_rate[-1] - initial_flow_rate) / initial_flow_rate * 100, 2)}%",
            delta_color="inverse"
        )
    
    with metric_col2:
        # Display failure prediction
        if time_until_failure:
            st.metric(
                label="Time Until Failure",
                value=f"{time_until_failure} years"
            )
        else:
            st.metric(
                label="Time Until Failure",
                value="No failure detected"
            )
        
        # Total flow rate drop
        st.metric(
            label="Total Flow Rate Drop",
            value=f"{round(100 - (flow_rate[-1] / initial_flow_rate * 100), 2)}%"
        )
    
    # Show efficiency impact factors
    # st.markdown("### Efficiency Impact Factors")
    
    # # Calculate impact percentages
    # particle_impact = particle_concentration * 0.005 * 100
    # ph_impact = abs(7 - ph) * 0.01 * 100
    
    # # Create a horizontal bar chart for impact factors
    # impact_data = {
    #     'Factor': ['Sand Particles', 'pH Deviation'],
    #     'Impact (% per year)': [particle_impact, ph_impact]
    # }
    # impact_df = pd.DataFrame(impact_data)
    
    # fig, ax = plt.subplots(figsize=(8, 3))
    # bars = ax.barh(impact_df['Factor'], impact_df['Impact (% per year)'], color=['#FFA726', '#42A5F5'])
    # ax.set_xlabel('Efficiency Impact (% per year)')
    # ax.grid(axis='x', alpha=0.3)
    
    # # Add value labels to bars
    # for bar in bars:
    #     width = bar.get_width()
    #     ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', 
    #             va='center', fontsize=10)
    
    # st.pyplot(fig)
    
    # Recommendations section
    # st.markdown("### Recommendations")
    
    # if time_until_failure and time_until_failure < years:
    #     st.warning(f"⚠️ Pump will reach failure threshold in year {time_until_failure}. Consider the following actions:")
    #     if overhaul_interval > 2:
    #         st.info(f"🔧 Decreasing overhaul interval from {overhaul_interval} to {max(1, overhaul_interval - 2)} years may extend pump life.")
    # else:
    #     st.success("✅ Pump is projected to maintain adequate flow throughout the simulation period.")
    
    # # Display operational insights
    # if particle_concentration > 5:
    #     st.info(f"🔍 High sand particle concentration ({particle_concentration}%) is significantly impacting pump life.")
    
    # if abs(7 - ph) > 2:
    #     st.info(f"🔍 pH level of {ph} deviates significantly from neutral (7.0), accelerating degradation.")

# Add download capability for the results
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name="pump_flow_rate_simulation.csv",
    mime="text/csv",
)