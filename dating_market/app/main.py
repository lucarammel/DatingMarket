import streamlit as st
from loguru import logger

from dating_market.market import Market

st.set_page_config(
    page_title="Dating App Simulator",
    page_icon=":two_hearts:",
)

st.title("Dating App Market Simulation")

# Streamlit Sidebar for Parameters
st.sidebar.header("Market Simulation Parameters")

# Select the number of users
n_users = st.sidebar.slider("Number of Users", min_value=10, max_value=1000, value=100, step=10)

# Select male ratio
male_ratio = st.sidebar.slider("Male Ratio", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

# Select the number of days for the simulation
days = st.sidebar.slider("Number of Days", min_value=1, max_value=30, value=10, step=1)

# Run the simulation
if st.sidebar.button("Run Simulation"):
    market = Market(n_users=n_users, male_ratio=male_ratio)

    # Run the market simulation and print logs
    with st.spinner("Running the simulation..."):
        market.run(days=days)

    # Get log outputs
    logs = logger.bind(market=market)
    st.write(logs)

    # Convert the users' data into a DataFrame (polars or pandas)
    df = market.participants.get_users_data()

    # Display the data as a table
    st.write("Simulation data:")
    st.dataframe(df)

    # Plot the scatter plot for visualization
    st.write("User Interaction Visualization:")
    market.plot_scatter(
        df,
        x="attractiveness_score",
        y="match_rate",
        color="gender",
        size="matches",
        title="Attractiveness vs. Match Rate",
        labels={"attractiveness_score": "Attractiveness", "match_rate": "Match Rate"},
    )
