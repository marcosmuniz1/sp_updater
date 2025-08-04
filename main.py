import streamlit as st
import pandas as pd

# The main title for the app
st.subheader("SearchPattern Updater")

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
        # If a decoding error occurs, silently try again with 'latin1'.
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
            
            st.write("---") 
            st.write("### Content Filters")

            df_text_filtered = df_filtered.copy()

            # Filter for Departure Cities
            if "Condition Departure Cities" in df_text_filtered.columns:
                departure_filter = st.text_input(
                    "Filter by Departure City (text contains):",
                    placeholder="e.g., LON"
                )
                show_blanks_departure = st.checkbox(
                    "Also include rows with a blank Departure City", key="blanks_dep"
                )

                if departure_filter:
                    text_match = df_text_filtered["Condition Departure Cities"].str.contains(departure_filter, case=False, na=False)
                    if show_blanks_departure:
                        is_blank = df_text_filtered["Condition Departure Cities"].isna()
                        df_text_filtered = df_text_filtered[text_match | is_blank]
                    else:
                        df_text_filtered = df_text_filtered[text_match]

            # Filter for Arrival Cities
            if "Condition Arrival Cities" in df_text_filtered.columns:
                arrival_filter = st.text_input(
                    "Filter by Arrival City (text contains):",
                    placeholder="e.g., LIS"
                )
                show_blanks_arrival = st.checkbox(
                    "Also include rows with a blank Arrival City", key="blanks_arr"
                )

                if arrival_filter:
                    text_match = df_text_filtered["Condition Arrival Cities"].str.contains(arrival_filter, case=False, na=False)
                    if show_blanks_arrival:
                        is_blank = df_text_filtered["Condition Arrival Cities"].isna()
                        df_text_filtered = df_text_filtered[text_match | is_blank]
                    else:
                        df_text_filtered = df_text_filtered[text_match]
            
            # Filter for Provider Name
            if "Provider Name" in df_text_filtered.columns:
                provider_filter = st.text_input(
                    "Filter by Provider Name (text contains):",
                    placeholder="e.g., Lufthansa"
                )
                if provider_filter:
                    df_text_filtered = df_text_filtered[df_text_filtered["Provider Name"].str.contains(provider_filter, case=False, na=False)]

            st.write("---")

            # The default is now the 4th item in the list (index 3), which is "All"
            num_rows = st.selectbox(
                "Select number of rows to display:",
                options=[10, 50, 100, "All"],
                index=3 
            )

            if num_rows == "All":
                st.write(f"### Displaying All Matching Rows ({len(df_text_filtered)})")
                st.dataframe(df_text_filtered)
            else:
                st.write(f"### First {num_rows} Matching Rows")
                st.dataframe(df_text_filtered.head(num_rows))

        else:
            st.warning("Please select at least one column to display.")
