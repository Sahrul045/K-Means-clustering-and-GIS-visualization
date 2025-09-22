import streamlit as st
import pandas as pd
from models.data_model import DatasetMetadata, NormalizationResult

def display_dataset_metadata(metadata: DatasetMetadata):
    """Menampilkan metadata dataset"""
    st.subheader("Metadata Dataset")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jumlah Data", metadata.row_count)
    with col2:
        st.metric("Jumlah Fitur", len(metadata.columns))
    with col3:
        st.metric("Memori Digunakan", f"{metadata.memory_usage_mb:.2f} MB")
    
    st.write("**Kolom Numerik:**", ", ".join(metadata.numeric_columns))
    if metadata.non_numeric_columns:
        st.write("**Kolom Non-Numerik:**", ", ".join(metadata.non_numeric_columns))
        st.write("**Kolom untuk Merge:**", metadata.merge_key_column)
    
    if metadata.missing_values_info["has_missing"]:
        st.warning(f"Terdapat missing values! {metadata.missing_values_info['rows_dropped']} baris dihapus.")
        st.write("Missing values per kolom:", metadata.missing_values_info["missing_counts"])
    else:
        st.success("Tidak ditemukan missing values. Data bersih.")

def display_data_preview(original_data: pd.DataFrame, normalized_data: pd.DataFrame):
    """Menampilkan preview data"""
    st.subheader("👀 Preview Data")
    
    tab1, tab2 = st.tabs(["Data Asli", "Data Normalisasi"])
    
    with tab1:
        st.write("Data Asli (5 baris pertama):")
        st.dataframe(original_data.head())
    
    with tab2:
        st.write("Data Normalisasi (5 baris pertama):")
        st.dataframe(normalized_data.head())