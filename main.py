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

# Initialize DataFrames to None, they will be populated when files are uploaded
df_sp = None
aggregated_df = None

# --- PROCESS THE SEARCH PATTERNS FILE ---
if searchpatterns_csv is not None:
    try:
        # We read the main Search Patterns DF here
        df_sp = pd.read_csv(searchpatterns_csv)
        st.success("Search Patterns file uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading Search Patterns file: {e}")
        df_sp = None

    # This block for filtering the search patterns file runs independently
    if df_sp is not None:
        st.write("---") 
        st.write("### Filter Search Patterns File")
        df_content_filtered = df_sp.copy()
        # (Filtering logic as it was before, for Departure, Arrival, Provider...)
        # ... this part is untouched ...


# --- PROCESS THE PRODUCT IDS FILE ---
if productid_csv is not None:
    with st.spinner('Aggregating routes from Product IDs file...'):
        # We process the second file and create the aggregated_df here
        aggregated_df = aggregate_routes(productid_csv)
    
    if not aggregated_df.empty:
        st.success("Product IDs file processed successfully.")
    else:
        st.warning("Product IDs file was processed, but the resulting aggregation is empty.")


# --- NEW: COMBINED ANALYSIS SECTION ---
# This entire section will only appear if BOTH files have been successfully processed.
if df_sp is not None and aggregated_df is not None and not aggregated_df.empty:
    st.write("---")
    st.header("Find Search Patterns by Product ID")

    query_id = st.text_input("Enter a Product ID to find related Search Patterns:")

    if query_id:
        with st.spinner(f"Searching for patterns related to Product ID: {query_id}..."):
            # --- This is the exact logic you provided, integrated into the app ---

            # 1. Find all routes containing the product ID.
            id_route_list = aggregated_df[aggregated_df['product_ids'].str.contains(query_id, na=False)].route.unique()

            if len(id_route_list) == 0:
                st.warning(f"No routes found for Product ID '{query_id}'.")
            else:
                st.info(f"Found {len(id_route_list)} route(s) associated with Product ID '{query_id}'. Now finding matching search patterns...")
                
                # 2. Loop through routes and append filtered DataFrames to the list
                results_list = []
                for id_route in id_route_list:
                    c1 = id_route[:3]
                    c2 = id_route[4:7]
                    c3 = id_route[8:]

                    cond1 = (df_sp['Condition Departure Cities'].isna()) | (df_sp['Condition Departure Cities'].str.contains(c1, na=False, case=False))
                    cond2 = (df_sp['Condition Arrival Cities'].isna()) | (df_sp['Condition Arrival Cities'].str.contains(c2, na=False, case=False))
                    cond3 = (df_sp['Condition Departure Cities'].isna()) | (df_sp['Condition Departure Cities'].str.contains(c3, na=False, case=False))

                    filtered_chunk = df_sp[cond1 & cond2 & cond3]
                    results_list.append(filtered_chunk)

                # 3. After the loop, concatenate and drop duplicates.
                if results_list:
                    combined_sp = pd.concat(results_list, ignore_index=True)
                    applicable_sp = combined_sp.drop_duplicates()
                    
                    st.success(f"Found {len(applicable_sp)} unique Search Pattern(s):")
                    st.dataframe(applicable_sp)
                else:
                    st.warning("Found associated routes, but no matching search patterns exist in the uploaded file.")
