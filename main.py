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

        # --- REPLACEMENT FOR st.multiselect ---
        # Use an expander to create a dropdown-like container for the checkboxes.
        # 'expanded=True' makes it open by default.
        with st.expander("Select columns to display:", expanded=True):
            # Add a "Select All" checkbox for convenience. Its value determines the default for others.
            select_all = st.checkbox("Select All", value=True)
            
            selected_columns = []
            # Loop through each column to create a checkbox.
            for column in all_columns:
                # The 'value' of each checkbox is controlled by the 'Select All' checkbox.
                # A unique 'key' is essential for each widget created in a loop.
                if st.checkbox(column, value=select_all, key=f"col_{column}"):
                    selected_columns.append(column)
        # --- END OF REPLACEMENT ---

        # Filter the DataFrame to show only the selected columns.
        if selected_columns:
            df_filtered = df[selected_columns]

            # Display the first 5 rows of the filtered DataFrame.
            st.write("### First 5 Rows of Selected Data")
            st.dataframe(df_filtered.head(5))
        else:
            # This message now appears if the user manually unchecks all columns.
            st.warning("Please select at least one column to display.")
