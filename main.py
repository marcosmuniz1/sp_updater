import streamlit as st
import pandas as pd

# The main title for the app
st.write("Searchpattern Viewer V1")

# Use st.file_uploader to create a file upload widget.
# 'csv' is specified as the accepted file type.
csv_file = st.file_uploader("Choose a CSV file", type="csv")

# Check if a file has been uploaded
if csv_file is not None:
    # Read the uploaded file into a pandas DataFrame.
    # The file is a file-like object, which pandas can read directly.
    try:
        df = pd.read_csv(csv_file)

        # Display a success message
        st.success("File uploaded successfully! Here are the first 5 rows:")

        # Use st.dataframe to display the first 5 rows of the DataFrame
        # The .head(5) method is used to get just the first 5 rows
        st.dataframe(df.head(5))

    except Exception as e:
        st.error(f"Error: Unable to read the CSV file. Details: {e}")

