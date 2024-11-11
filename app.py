import streamlit as st
import pandas as pd

# Load the CSV file
@st.cache
def load_data():
    return pd.read_csv('deals.csv')

# Display data based on selected site
def display_site_data(site_name, data):
    site_data = data[data['Site'] == site_name]
    st.write(f"**Deals for site: {site_name}**")
    st.dataframe(site_data)

# Main Streamlit app
def main():
    st.title("Deals Dashboard")
    st.write("Choose a site to see all available deals.")

    # Load data
    data = load_data()

    # Select site
    site_names = data['Site'].unique()
    selected_site = st.selectbox("Select a site", site_names)

    # Display data for selected site
    if selected_site:
        display_site_data(selected_site, data)

if __name__ == '__main__':
    main()
