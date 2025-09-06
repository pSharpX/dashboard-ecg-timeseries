import streamlit as st
import pandas as pd
import numpy as np

# Define the pages
page_3 = st.Page("ecg_page.py", title="Dashboard", icon="🌎")

# Set up navigation
pg = st.navigation([page_3])

# Run the selected page
pg.run()

