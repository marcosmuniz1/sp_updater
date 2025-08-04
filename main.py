import streamlit as st
import pandas as pd

# The main title for the app
st.write("Hello, Welcome")

# Use st.file_uploader to create a file upload widget.
# 'csv' is specified as the accepted file type.
csv_file = st.file_uploader("Choose a CSV file", type="csv")

# Check if a file has been uploaded
if csv_file is not None:
    # Attempt to read the file, trying different encodings if the default fails.
    try:
        # First, try to read the CSV with the default 'utf-8' encoding.
        df = pd.read_csv(csv_file)

    except UnicodeDecodeError:
        # If a decoding error occurs, it's likely due to the file's encoding.
        # This block will retry with 'latin1', a common alternative encoding.
        st.warning("Could not read file with default encoding, attempting with 'latin1'...")
        # Reset the file pointer to the beginning before trying again.
        csv_file.seek(0)
        try:
            df = pd.read_csv(csv_file, encoding='latin1')
        except Exception as e:
            # If 'latin1' also fails, display a generic error message.
            st.error(f"Error: Unable to read the CSV file with 'latin1' encoding either. Details: {e}")
            df = None
    except Exception as e:
        # Catch any other potential errors during the read process.
        st.error(f"Error: Unable to read the CSV file. Details: {e}")
        df = None

    if df is not None:
        # Display a success message
        st.success("File uploaded successfully! Here are the first 5 rows:")
        
        # Use st.dataframe to display the first 5 rows of the DataFrame
        # The .head(5) method is used to get just the first 5 rows
        st.dataframe(df.head(5))

