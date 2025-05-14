import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path
csv_path = "ct_bcit_students.csv"

def load_data():
    """Load data from CSV file"""
    if not os.path.exists(csv_path):
        st.error(f"Error: CSV file not found at {csv_path}")
        return pd.DataFrame()
        
    # Load from existing CSV
    df = pd.read_csv(csv_path)
    
    # If 'Batch' column doesn't exist, create it by extracting from Enrollment_Number
    if 'Batch' not in df.columns:
        df['Batch'] = df['Enrollment_Number'].apply(extract_batch_year)
    
    return df

def extract_batch_year(enrollment_number):
    """Extract batch year from enrollment number"""
    import re
    
    # Pattern 1: NED-24012/2001-2002
    match = re.search(r'(\d{4})-(\d{4})', enrollment_number)
    if match:
        return f"{match.group(1)} - {match.group(2)}"
    
    # Pattern 2: NED-23019/2000-
    match = re.search(r'/(\d{4})-', enrollment_number)
    if match:
        year = match.group(1)
        next_year = str(int(year) + 1)
        return f"{year} - {next_year}"
    
    # Pattern 3: NED/0073/08-09
    match = re.search(r'/(\d{2})-(\d{2})', enrollment_number)
    if match:
        # Convert to four-digit years (assuming 20xx for years)
        start_year = f"20{match.group(1)}"
        end_year = f"20{match.group(2)}"
        return f"{start_year} - {end_year}"
    
    # Pattern 4: NED-26000/1/2003-2004
    match = re.search(r'(\d{4})-(\d{4})', enrollment_number)
    if match:
        return f"{match.group(1)} - {match.group(2)}"
    
    # Pattern 5: NED-0001/04-05 or NED/0001/04-05
    match = re.search(r'/(\d{2})-(\d{2})', enrollment_number)
    if match:
        start_year = f"20{match.group(1)}"
        end_year = f"20{match.group(2)}"
        return f"{start_year} - {end_year}"
    
    return "Unknown"

def main():
    st.set_page_config(
        page_title="NED University Students List",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("NED University CT/BCIT Students List (1999-2000 to 2008-2009)")
    st.write("Filter and view students with roll numbers starting with CT or BCIT")
    
    # Show loading spinner
    with st.spinner("Loading data..."):
        df = load_data()
    
    if df.empty:
        st.warning("No data available. Please check if the CSV file exists.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get unique batch years and sort them
    batch_years = sorted(df['Batch'].unique())
    
    # Batch year filter
    selected_batch = st.sidebar.selectbox(
        "Select Batch Year",
        ["All"] + list(batch_years)
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_batch != "All":
        filtered_df = filtered_df[filtered_df['Batch'] == selected_batch]
    
    # Display stats
    st.header("Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Students", len(filtered_df))
    
    with col2:
        st.metric("Total Batches", len(filtered_df['Batch'].unique()))
    
    # Display data table
    st.header("Student Records")
    st.dataframe(
        filtered_df,
        column_config={
            "Name": st.column_config.TextColumn("Student Name"),
            "Enrollment_Number": st.column_config.TextColumn("Enrollment Number"),
            "Roll_Number": st.column_config.TextColumn("Roll Number"),
            "Batch": st.column_config.TextColumn("Batch Year")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Search functionality
    st.header("Search by Name")
    search_term = st.text_input("Enter student name or part of name")
    
    if search_term:
        search_results = filtered_df[filtered_df['Name'].str.contains(search_term, case=False)]
        st.subheader(f"Search Results: {len(search_results)} matches")
        
        if not search_results.empty:
            st.dataframe(
                search_results,
                column_config={
                    "Name": st.column_config.TextColumn("Student Name"),
                    "Enrollment_Number": st.column_config.TextColumn("Enrollment Number"),
                    "Roll_Number": st.column_config.TextColumn("Roll Number"),
                    "Batch": st.column_config.TextColumn("Batch Year")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.write("No matching records found.")
    
    # Download filtered data as CSV
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name=f"filtered_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()