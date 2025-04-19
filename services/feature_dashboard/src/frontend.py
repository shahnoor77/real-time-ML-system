# In this file I define the UI and the logic of the dashboard
import streamlit as st
import pandas as pd
from loguru import logger
from time import sleep

from src.backend import get_features_from_the_store
from src.plot import plot_candles
from src.config import config

st.write("""
# OHLC features dashboard
""")

# add a selectbox to the sidebar to switch between the online store
# and the offline store
online_or_offline = st.sidebar.selectbox(
    'Select the store',
    ('online', 'offline')
)

# Challenge: add a time range slider to the sidebar to select the time range for which
# we want to display the data
# Pass this parameter to the get_features_from_the_store function to get the data
with st.container():
    placeholder_chart = st.empty()

while True:
    # Load the data
    data = get_features_from_the_store(online_or_offline)
    logger.debug(f'Received {len(data)} rows of data from the Feature Store')

    # Refresh the chart
    with placeholder_chart:
        st.bokeh_chart(plot_candles(data))

    sleep(15)