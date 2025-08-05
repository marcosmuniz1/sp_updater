import streamlit as st
import pandas as pd
import os

# The main title for the app
st.header("SearchPattern Updater")

st.markdown(
    "Upload the SP and SKU files for processing. You can find the latest uploaded versions at "
    "[https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r](https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r)"
)

# --- FUNCTION DEFINITION ---
# Place the function here and add the @st.cache_data decorator.
@st.cache_data
def aggregate_routes(uploaded_file) -> pd.DataFrame:
    """
    Loads flight data from an uploaded file, groups by route, and aggregates product IDs.
    """
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ['fpc_reference_product_id', 'fpc_iata_departure', 'fpc_iata_arrival', 'fpc_iata_return']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: The uploaded Product IDs file is missing one or more required columns: {required_cols}")
            return pd.DataFrame()

        # Ensure the product ID column is treated as a string for aggregation.
        df['fpc_reference_product_id'] = df['fpc_reference_product_id'].astype(str)

        # Define the columns that constitute a unique route.
        route_columns = ['fpc_iata_departure', 'fpc_iata_arrival', 'fpc_iata_return']

        # Group by the unique route combination and aggregate the product IDs.
        aggregated_data = df.groupby(route_columns)['fpc_reference_product_id'].apply(
            lambda ids: ';'.join(ids.unique())
        ).reset_index()

        # For clarity, create a single 'route' column by joining the IATA codes.
        aggregated_data['route'] = aggregated_data[route_columns].apply(
            lambda row: '-'.join(row.values.astype(str)),
            axis=1
        )

        # Rename the aggregated product ID column for clarity.
        aggregated_data.rename(columns={'fpc_reference_product_id': 'product_ids'}, inplace=True)

        # Select and reorder the final columns for the output.
        final_df = aggregated_data[['route', 'product_ids'] + route_columns]

        return final_df

    except Exception as e:
        # Use st.error to display errors in the Streamlit UI
        st.error(f"An unexpected error occurred during aggregation: {e}")
        return pd.DataFrame()


# --- FILE UPLOADERS ---
searchpatterns_csv = st.file_uploader(
    "1. Upload Search Patterns File (CSV)", 
    type="csv", 
    key="uploader1"
)

productid_csv = st.file_uploader(
    "2. Upload Product IDs File (CSV)", 
    type="csv", 
    key="uploader2"
)


# --- PROCESS THE SEARCH PATTERNS FILE ---
if searchpatterns_csv is not None:
    # Renamed DataFrame to df_sp (for Search Patterns)
    df_sp = None
    # Attempt to read the file
    try:
        df_sp = pd.read_csv(searchpatterns_csv)
    except UnicodeDecodeError:
        searchpatterns_csv.seek(0)
        try:
            df_sp = pd.read_csv(searchpatterns_csv, encoding='latin1')
        except Exception as e:
            st.error(f"Error: Unable to read the Search Patterns CSV file with 'latin1' encoding either. Details: {e}")
            df_sp = None
    except Exception as e:
        st.error(f"Error: Unable to read the Search Patterns CSV file. Details: {e}")
        df_sp = None

    if df_sp is not None:
        st.success("Search Patterns file uploaded successfully!")
        
        st.write("---") 
        st.write("### Content Filters for Search Patterns File")

        # Start with a copy of the original DataFrame to apply filters to.
        df_content_filtered = df_sp.copy()

        # Filter for Departure Cities
        if "Condition Departure Cities" in df_sp.columns:
            departure_filter = st.text_input(
                "Filter by Departure City (text contains):",
                placeholder="e.g., LON"
            )
            show_blanks_departure = st.checkbox(
                "Also include rows with a blank Departure City", key="blanks_dep"
            )
            if departure_filter:
                text_match = df_content_filtered["Condition Departure Cities"].str.contains(departure_filter, case=False, na=False)
                if show_blanks_departure:
                    is_blank = df_content_filtered["Condition Departure Cities"].isna()
                    df_content_filtered = df_content_filtered[text_match | is_blank]
                else:
                    df_content_filtered = df_content_filtered[text_match]

        # Filter for Arrival Cities
        if "Condition Arrival Cities" in df_sp.columns:
            arrival_filter = st.text_input(
                "Filter by Arrival City (text contains):",
                placeholder="e.g., LIS"
            )
            show_blanks_arrival = st.checkbox(
                "Also include rows with a blank Arrival City", key="blanks_arr"
            )
            if arrival_filter:
                text_match = df_content_filtered["Condition Arrival Cities"].str.contains(arrival_filter, case=False, na=False)
                if show_blanks_arrival:
                    is_blank = df_content_filtered["Condition Arrival Cities"].isna()
                    df_content_filtered = df_content_filtered[text_match | is_blank]
                else:
                    df_content_filtered = df_content_filtered[text_match]
        
        # Filter for Provider Name
        if "Provider Name" in df_sp.columns:
            provider_filter = st.text_input(
                "Filter by Provider Name (text contains):",
                placeholder="e.g., Lufthansa"
            )
            if provider_filter:
                df_content_filtered = df_content_filtered[df_content_filtered["Provider Name"].str.contains(provider_filter, case=False, na=False)]

        # Select columns to display
        all_columns = df_sp.columns.tolist()
        with st.expander("Select columns to display:", expanded=True):
            select_all = st.checkbox("Select All", value=True)
            
            selected_columns = []
            for column in all_columns:
                if st.checkbox(column, value=select_all, key=f"col_{column}"):
                    selected_columns.append(column)

        # Create the final display view
        if selected_columns:
            df_display = df_content_filtered[selected_columns]

            st.write("---")
            
            num_rows = st.selectbox(
                "Select number of rows to display:",
                options=[10, 50, 100, "All"],
                index=3 
            )

            if num_rows == "All":
                st.write(f"### Displaying All Matching Rows ({len(df_display)})")
                st.dataframe(df_display)
            else:
                st.write(f"### First {num_rows} Matching Rows")
                st.dataframe(df_display.head(num_rows))
        else:
            st.warning("Please select at least one column to display.")


# --- PROCESS THE PRODUCT IDS FILE ---
if productid_csv is not None:
    st.write("---")
    st.write("### Product IDs File Processing")
    
    # Use a spinner to provide feedback during the computation
    with st.spinner('Aggregating routes... This may take a moment.'):
        # Call the cached function with the uploaded file object
        aggregated_df = aggregate_routes(productid_csv)

    # Display the results after the spinner is done
    if not aggregated_df.empty:
        st.success("No issues when aggregating Product IDs")
        
        # Optional: Add a download button for the result
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        csv_output = convert_df_to_csv(aggregated_df)
        
        st.download_button(
           label="Download Aggregated Data as CSV",
           data=csv_output,
           file_name='aggregated_routes.csv',
           mime='text/csv',
        )
    else:
        # This message will show if the function returned an error or an empty result
        st.warning("Aggregation resulted in an empty table.")
