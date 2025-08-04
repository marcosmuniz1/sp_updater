import streamlit as st
import pandas as pd

# The main title for the app
st.write("Hello, Welcome")

# Use st.file_uploader to create a file upload widget.
csv_file = st.file_uploader("Choose a CSV file", type="csv")

# Check if a file has been uploaded
if csv_file is not None:
    df = None
    # Attempt to read the file, trying different encodings if the default fails.
    try:
        # Try to read with the default 'utf-8' encoding first.
        df = pd.read_csv(csv_file)

    except UnicodeDecodeError:
        # If a decoding error occurs, try again with 'latin1'.
        st.warning("Could not read file with default encoding, attempting with 'latin1'...")
        # Reset the file pointer to the beginning before trying again.
        csv_file.seek(0)
        try:
            df = pd.read_csv(csv_file, encoding='latin1')
        except Exception as e:
            # If 'latin1' also fails, display a generic error.
            st.error(f"Error: Unable to read the CSV file with 'latin1' encoding either. Details: {e}")
            df = None
    except Exception as e:
        # Catch any other potential errors during the read process.
        st.error(f"Error: Unable to read the CSV file. Details: {e}")
        df = None

    if df is not None:
        st.success("File uploaded successfully!")
        
        # Get the list of all column names from the DataFrame.
        all_columns = df.columns.tolist()

        # Create a multiselect dropdown for the user to choose columns.
        # The 'default' argument ensures all columns are selected initially.
        selected_columns = st.multiselect(
            "Select columns to display:",
            options=all_columns,
            default=all_columns
        )

        # Filter the DataFrame to show only the selected columns.
        if selected_columns:
            df_filtered = df[selected_columns]

            # Display the first 5 rows of the filtered DataFrame.
            st.write("### First 5 Rows of Selected Data")
            st.dataframe(df_filtered.head(5))
        else:
            st.warning("Please select at least one column to display.")

