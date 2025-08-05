import streamlit as st
import pandas as pd
import os

# --- FUNCTION DEFINITION (UNCHANGED) ---
@st.cache_data
def aggregate_routes(uploaded_file) -> pd.DataFrame:
    # ... (function code is exactly the same as before, so it's omitted for brevity)
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ['fpc_reference_product_id', 'fpc_iata_departure', 'fpc_iata_arrival', 'fpc_iata_return']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: The uploaded Product IDs file is missing one or more required columns: {required_cols}")
            return pd.DataFrame()
        df['fpc_reference_product_id'] = df['fpc_reference_product_id'].astype(str)
        route_columns = ['fpc_iata_departure', 'fpc_iata_arrival', 'fpc_iata_return']
        aggregated_data = df.groupby(route_columns)['fpc_reference_product_id'].apply(
            lambda ids: ';'.join(ids.unique())
        ).reset_index()
        aggregated_data['route'] = aggregated_data[route_columns].apply(
            lambda row: '-'.join(row.values.astype(str)),
            axis=1
        )
        aggregated_data.rename(columns={'fpc_reference_product_id': 'product_ids'}, inplace=True)
        final_df = aggregated_data[['route', 'product_ids'] + route_columns]
        return final_df
    except Exception as e:
        st.error(f"An unexpected error occurred during aggregation: {e}")
        return pd.DataFrame()


# --- APP LAYOUT ---
st.header("SearchPattern Updater")
st.markdown(
    "Upload the SP and SKU files for processing. You can find the latest uploaded versions at "
    "[https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r](https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r)"
)

# --- FILE UPLOADERS ---
searchpatterns_csv = st.file_uploader(
    "1. Upload Search Patterns File (CSV)", type="csv", key="uploader1"
)
productid_csv = st.file_uploader(
    "2. Upload Product IDs File (CSV)", type="csv", key="uploader2"
)

# Initialize DataFrames
df_sp = None
aggregated_df = None

# --- DATA LOADING ---
# Load Search Patterns file if uploaded
if searchpatterns_csv:
    try:
        df_sp = pd.read_csv(searchpatterns_csv)
    except Exception as e:
        st.error(f"Error reading Search Patterns file: {e}")

# Load and process Product IDs file if uploaded
if productid_csv:
    aggregated_df = aggregate_routes(productid_csv)

# --- UNIFIED FILTERING AND DISPLAY LOGIC ---
# This main block only runs if the primary Search Patterns file is loaded.
if df_sp is not None:
    st.write("---")
    st.header("Combined Filters")

    # --- DEFINE ALL FILTER WIDGETS ---
    # The Product ID search is now just another filter
    query_id = None
    if aggregated_df is not None and not aggregated_df.empty:
        query_id = st.text_input("Filter by Product ID (optional):")
    
    # Text-based content filters
    departure_filter = st.text_input("Filter by Departure City (text contains):", placeholder="e.g., LON")
    show_blanks_departure = st.checkbox("Also include rows with a blank Departure City", key="blanks_dep")
    
    arrival_filter = st.text_input("Filter by Arrival City (text contains):", placeholder="e.g., LIS")
    show_blanks_arrival = st.checkbox("Also include rows with a blank Arrival City", key="blanks_arr")
    
    provider_filter = st.text_input("Filter by Provider Name (text contains):", placeholder="e.g., Lufthansa")

    # --- APPLY FILTERS SEQUENTIALLY ---
    # Start with a full copy of the data. This will be progressively filtered.
    working_df = df_sp.copy()

    # 1. Apply Product ID filter first (if used). This significantly narrows the search space.
    if query_id:
        with st.spinner(f"Finding patterns for Product ID {query_id}..."):
            id_route_list = aggregated_df[aggregated_df['product_ids'].str.contains(query_id, na=False)].route.unique()
            if len(id_route_list) > 0:
                results_list = []
                for id_route in id_route_list:
                    c1, c2, c3 = id_route[:3], id_route[4:7], id_route[8:]
                    cond1 = (df_sp['Condition Departure Cities'].isna()) | (df_sp['Condition Departure Cities'].str.contains(c1, na=False, case=False))
                    cond2 = (df_sp['Condition Arrival Cities'].isna()) | (df_sp['Condition Arrival Cities'].str.contains(c2, na=False, case=False))
                    cond3 = (df_sp['Condition Departure Cities'].isna()) | (df_sp['Condition Departure Cities'].str.contains(c3, na=False, case=False))
                    results_list.append(df_sp[cond1 & cond2 & cond3])
                
                if results_list:
                    # This becomes the new base DataFrame for further filtering
                    working_df = pd.concat(results_list, ignore_index=True).drop_duplicates()
                else:
                    working_df = pd.DataFrame(columns=df_sp.columns) # No results, create empty df
            else:
                st.warning(f"No routes found for Product ID '{query_id}'. Displaying results for other filters only.")
                working_df = pd.DataFrame(columns=df_sp.columns) # No results, create empty df

    # 2. Apply text-based filters on the (potentially already filtered) working_df
    if departure_filter:
        text_match = working_df["Condition Departure Cities"].str.contains(departure_filter, case=False, na=False)
        if show_blanks_departure:
            is_blank = working_df["Condition Departure Cities"].isna()
            working_df = working_df[text_match | is_blank]
        else:
            working_df = working_df[text_match]

    if arrival_filter:
        text_match = working_df["Condition Arrival Cities"].str.contains(arrival_filter, case=False, na=False)
        if show_blanks_arrival:
            is_blank = working_df["Condition Arrival Cities"].isna()
            working_df = working_df[text_match | is_blank]
        else:
            working_df = working_df[text_match]
            
    if provider_filter:
        working_df = working_df[working_df["Provider Name"].str.contains(provider_filter, case=False, na=False)]

    # --- DISPLAY FINAL, COMBINED RESULT ---
    st.write("---")
    st.header("Filtered Results")
    st.info(f"Displaying **{len(working_df)}** matching rows.")

    # Column selection (operates on the original columns, but displays data from working_df)
    with st.expander("Select columns to display:", expanded=True):
        all_columns = df_sp.columns.tolist()
        select_all = st.checkbox("Select All", value=True)
        selected_columns = [col for col in all_columns if st.checkbox(col, value=select_all, key=f"col_{col}")]

    if selected_columns:
        # Ensure selected columns exist in the final dataframe before displaying
        display_cols = [col for col in selected_columns if col in working_df.columns]
        st.dataframe(working_df[display_cols])
    else:
        st.warning("Please select at least one column to display.")
