import streamlit as st
import pandas as pd
import io
import os

# Page configuration
st.set_page_config(
    page_title="Store Location Finder",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>📍 Store Location Finder</h1>
        <p>Upload Excel → Get Coordinates → Download Results</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    st.write("**About this App:**")
    st.info("Upload an Excel file with ZIP codes to automatically get latitude and longitude coordinates.")
    st.markdown("---")
    st.write("**Support:**")
    st.write("• Supported format: .xlsx")
    st.write("• Required column: 'Zip Code'")
    st.write("• Max file size: 200 MB")

# Load ZIP database
@st.cache_data
def load_zip_db():
    if os.path.exists("uszips.csv"):
        zip_db = pd.read_csv("uszips.csv", dtype={"zip": str})
        zip_db = zip_db[["zip", "lat", "lng", "city", "state_id"]]
        zip_db.columns = ["Zip Code", "Latitude", "Longitude", "City", "State"]
        zip_db["Zip Code"] = zip_db["Zip Code"].str.strip()
        return zip_db
    else:
        st.error("⚠️ uszips.csv database not found!")
        return None

# Main layout
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📤 Upload File")
    st.markdown("""
    <div class="info-box">
    <strong>📋 Instructions:</strong>
    <br>1. Prepare your Excel file with ZIP codes
    <br>2. Column name must be "Zip Code"
    <br>3. Upload the file below
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"], label_visibility="collapsed")

with col2:
    st.subheader("📊 Results")
    st.markdown("<div class='info-box'><strong>Status:</strong> Ready to upload</div>", unsafe_allow_html=True)

st.markdown("---")

# Process uploaded file
if uploaded_file:
    try:
        # Load database
        zip_db = load_zip_db()
        
        if zip_db is None:
            st.stop()
        
        # Read uploaded file
        with st.spinner("📂 Reading file..."):
            df = pd.read_excel(uploaded_file)
        
        # Validate column
        if "Zip Code" not in df.columns:
            st.error("❌ Error: Column 'Zip Code' not found in Excel file!")
            st.write("Available columns:", df.columns.tolist())
            st.stop()
        
        # Clean zip codes
        with st.spinner("🧹 Cleaning data..."):
            df["Zip Code"] = df["Zip Code"].astype(str).str.replace("-", "").str.strip()
        
        st.markdown("""
        <div class="success-box">
        ✅ File loaded successfully! Processing...
        </div>
        """, unsafe_allow_html=True)
        
        # Display original data
        with st.expander("📋 Original Data", expanded=False):
            st.dataframe(df, use_container_width=True)
        
        # Process and merge
        with st.spinner("🔍 Matching ZIP codes..."):
            progress_bar = st.progress(0)
            
            result = df.merge(zip_db, on="Zip Code", how="left")
            
            total = len(result)
            matched = result["Latitude"].notna().sum()
            unmatched = total - matched
            
            progress_bar.progress(100)
        
        # Statistics
        st.markdown("---")
        st.subheader("📈 Processing Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("Total Records", total, delta=None)
        
        with stat_col2:
            st.metric("✅ Matched", matched, delta=f"{(matched/total*100):.1f}%")
        
        with stat_col3:
            st.metric("❌ Unmatched", unmatched, delta=f"{(unmatched/total*100):.1f}%")
        
        with stat_col4:
            match_rate = (matched / total * 100) if total > 0 else 0
            st.metric("Success Rate", f"{match_rate:.1f}%", delta=None)
        
        st.markdown("---")
        
        # Results tabs
        st.subheader("📊 Results")
        tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Full Data", "Unmatched", "Statistics"])
        
        with tab1:
            st.write("**Preview (First 10 rows)**")
            st.dataframe(result.head(10), use_container_width=True)
        
        with tab2:
            st.write("**Complete Dataset**")
            st.dataframe(result, use_container_width=True)
        
        with tab3:
            unmatched_df = result[result["Latitude"].isna()]
            if len(unmatched_df) > 0:
                st.write(f"**{len(unmatched_df)} Unmatched Records**")
                st.dataframe(unmatched_df, use_container_width=True)
            else:
                st.success("✅ All ZIP codes matched!")
        
        with tab4:
            st.write("**Data Summary**")
            col_stats1, col_stats2 = st.columns(2)
            
            with col_stats1:
                st.write("**Records by State:**")
                if "State" in result.columns:
                    state_count = result["State"].value_counts()
                    st.bar_chart(state_count)
            
            with col_stats2:
                st.write("**Match Statistics:**")
                match_data = pd.DataFrame({
                    "Status": ["Matched", "Unmatched"],
                    "Count": [matched, unmatched]
                })
                st.bar_chart(match_data.set_index("Status"))
        
        st.markdown("---")
        
        # Download button
        st.subheader("📥 Download Results")
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        with col_dl1:
            output_excel = io.BytesIO()
            result.to_excel(output_excel, index=False, engine="openpyxl")
            output_excel.seek(0)
            
            st.download_button(
                label="📊 Download Excel",
                data=output_excel,
                file_name="stores_with_coordinates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_dl2:
            output_csv = io.StringIO()
            result.to_csv(output_csv, index=False)
            output_csv.seek(0)
            
            st.download_button(
                label="📄 Download CSV",
                data=output_csv.getvalue(),
                file_name="stores_with_coordinates.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_dl3:
            st.info("✅ Ready to download!", icon="ℹ️")
        
        st.markdown("---")
        
        st.success("🎉 Processing complete!")
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.write("Please check your file and try again.")

else:
    st.info("👆 Upload an Excel file to get started!", icon="ℹ️")