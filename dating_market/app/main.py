import threading
import time
from io import StringIO

import streamlit as st
from loguru import logger

from dating_market.market import Market

st.set_page_config(
    page_title="Dating App Simulator",
    page_icon=":two_hearts:",
)

st.title("Dating App Market Simulation")

logger.remove()
log_buffer = StringIO()

logger.add(log_buffer, format="{time} {level} {message}", level="DEBUG")
log_display = st.empty()

if "market" not in st.session_state:
    st.session_state.market = None

# Streamlit Sidebar for Parameters
st.sidebar.header("Market Simulation Parameters")

# Select the number of users
n_users = st.sidebar.slider("Number of Users", min_value=10, max_value=1000, value=100, step=10)

# Select male ratio
male_ratio = st.sidebar.slider("Male Ratio", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

# Select the number of days for the simulation
days = st.sidebar.slider("Number of Days", min_value=1, max_value=30, value=10, step=1)


def run_process(n_users, male_ratio):
    global log_buffer
    log_buffer.truncate(0)  # Clear buffer
    log_buffer.seek(0)

    result_container = []

    def process_thread(n_users, male_ratio):
        market = Market(n_users=n_users, male_ratio=male_ratio)
        result_container.append(market.run)

    thread = threading.Thread(target=process_thread, daemon=True)
    thread.start()

    while thread.is_alive():  # Keep updating UI while process runs
        log_display.text_area("Logs", log_buffer.getvalue(), height=200, key="log_area")
        time.sleep(0.5)

    # Final update to capture last logs
    log_display.text_area("Logs", log_buffer.getvalue(), height=200, key="log_area")

    if result_container:
        st.session_state.process_result = result_container[0]

    return ()


if st.sidebar.button("Run Simulation"):
    run_process(n_users, male_ratio)

    market = st.session_state.process_result[0]

    df = market.participants.get_users_data()

    # Display the data as a table
    st.write("Simulation data:")
    st.dataframe(df)

    # Plot the scatter plot for visualization
    st.write("User Interaction Visualization:")
    market.participants.plot_scatter(
        df,
        x="attractiveness_score",
        y="match_rate",
        color="gender",
        size="matches",
        title="Attractiveness vs. Match Rate",
        labels={"attractiveness_score": "Attractiveness", "match_rate": "Match Rate"},
    )
