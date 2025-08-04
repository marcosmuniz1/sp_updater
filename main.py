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
            st.error(f"Error: Unable to read the CSV file with 'latin1' encoding either. Details: {e}")
            df = None
    except Exception as e:
        st.error(f"Error: Unable to read the CSV file. Details: {e}")
        df = None

    if df is not None:
        st.success("File uploaded successfully!")
        
        all_columns = df.columns.tolist()

        with st.expander("Select columns to display:", expanded=True):
            select_all = st.checkbox("Select All", value=True)
            
            selected_columns = []
            for column in all_columns:
                if st.checkbox(column, value=select_all, key=f"col_{column}"):
                    selected_columns.append(column)

        if selected_columns:
            df_filtered = df[selected_columns]
            
            # --- NEW: Text-based filters for specific columns ---
            st.write("---") # Visual separator
            st.write("### Text Filters")

            # Create a copy to apply text filters on
            df_text_filtered = df_filtered.copy()

            # Filter for Departure Cities (only if the column was selected by the user)
            if "Condition Departure Cities" in df_text_filtered.columns:
                departure_filter = st.text_input(
                    "Filter by Departure City (text contains):",
                    placeholder="e.g., London"
                )
                if departure_filter:
                    # Apply a case-insensitive 'contains' filter. na=False handles missing values gracefully.
                    df_text_filtered = df_text_filtered[df_text_filtered["Condition Departure Cities"].str.contains(departure_filter, case=False, na=False)]

            # Filter for Arrival Cities (only if the column was selected by the user)
            if "Condition Arrival Cities" in df_text_filtered.columns:
                arrival_filter = st.text_input(
                    "Filter by Arrival City (text contains):",
                    placeholder="e.g., Paris"
                )
                if arrival_filter:
                    df_text_filtered = df_text_filtered[df_text_filtered["Condition Arrival Cities"].str.contains(arrival_filter, case=False, na=False)]
            
            st.write("---") # Visual separator
            # --- END OF NEW CODE ---


            # Dropdown for selecting number of rows, now operates on the text-filtered dataframe
            num_rows = st.selectbox(
                "Select number of rows to display:",
                options=[10, 50, 100, "All"],
                index=0
            )

            # Display logic now uses df_text_filtered
            if num_rows == "All":
                st.write(f"### Displaying All Matching Rows ({len(df_text_filtered)})")
                st.dataframe(df_text_filtered)
            else:
                st.write(f"### First {num_rows} Matching Rows")
                st.dataframe(df_text_filtered.head(num_rows))

        else:
            st.warning("Please select at least one column to display.")
