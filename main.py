import streamlit as st
import pandas as pd
import os

# The main title for the app
st.header("SearchPattern Updater")

# --- NEW: Added descriptive text with a clickable link below the header ---
st.markdown(
    "Upload the SP and SKU files for processing. You can find the latest uploaded versions at "
    "[https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r](https://drive.google.com/drive/folders/1hrbWrcEeMjoWrRdZdBhZcvRdLqofru8r)"
)


# --- FILE UPLOADERS ---
# Renamed variables and updated labels for clarity.
searchpatterns_csv = st.file_uploader(
    "1. Upload Search Patterns File (CSV)", 
    type="csv", 
    key="uploader1"
)

productid_csv = st.file_uploader(
    "2. Upload Product IDs File (Optional)", 
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
    st.write("### Product IDs File Preview")
    # Renamed DataFrame to df_prod (for Product IDs)
    df_prod = None
    try:
        df_prod = pd.read_csv(productid_csv)
    except UnicodeDecodeError:
        productid_csv.seek(0)
        try:
            df_prod = pd.read_csv(productid_csv, encoding='latin1')
        except Exception as e:
            st.error(f"Error reading the Product IDs CSV file: {e}")
    except Exception as e:
        st.error(f"Error reading the Product IDs CSV file: {e}")

    if df_prod is not None:
        st.success("Product IDs file uploaded successfully!")
        st.dataframe(df_prod.head())
