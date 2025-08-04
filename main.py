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

        # Use an expander to create a dropdown-like container for the checkboxes.
        with st.expander("Select columns to display:", expanded=True):
            select_all = st.checkbox("Select All", value=True)
            
            selected_columns = []
            for column in all_columns:
                if st.checkbox(column, value=select_all, key=f"col_{column}"):
                    selected_columns.append(column)

        # Filter the DataFrame to show only the selected columns.
        if selected_columns:
            df_filtered = df[selected_columns]

            # --- NEW: Dropdown for selecting number of rows ---
            num_rows = st.selectbox(
                "Select number of rows to display:",
                options=[10, 50, 100, "All"],
                index=0  # Default to the first option, which is 10
            )

            # Dynamically create the title and the DataFrame view based on the selection
            if num_rows == "All":
                st.write(f"### Displaying All Rows ({len(df_filtered)})")
                st.dataframe(df_filtered)
            else:
                st.write(f"### First {num_rows} Rows of Selected Data")
                st.dataframe(df_filtered.head(num_rows))
            # --- END OF NEW CODE ---

        else:
            # This message now appears if the user manually unchecks all columns.
            st.warning("Please select at least one column to display.")
