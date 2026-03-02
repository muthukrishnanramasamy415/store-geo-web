import streamlit as st
import pandas as pd
import zipfile
import os
from geopy.geocoders import Nominatim

# Function to get latitude and longitude from ZIP code
def get_lat_long(zip_code):
    geolocator = Nominatim(user_agent="zip_code_locator")
    location = geolocator.geocode(zip_code)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Streamlit application
def main():
    st.title("ZIP Code Locator")
    st.write("Upload an Excel file containing ZIP codes to get latitude and longitude.")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        if 'ZIP Code' in df.columns:
            st.write("Original Data:")
            st.dataframe(df)

            latitudes = []
            longitudes = []

            for zip_code in df['ZIP Code']:
                lat, long = get_lat_long(zip_code)
                latitudes.append(lat)
                longitudes.append(long)

            df['Latitude'] = latitudes
            df['Longitude'] = longitudes

            st.write("Updated Data:")
            st.dataframe(df)

            # Save the updated file
            updated_file_path = "updated_data.xlsx"
            df.to_excel(updated_file_path, index=False)

            # Provide a download link
            with open(updated_file_path, "rb") as f:
                st.download_button("Download Updated Excel File", f, file_name=updated_file_path)
        else:
            st.warning("The Excel file must contain a 'ZIP Code' column.")

if __name__ == '__main__':
    main()