import streamlit as st
import tempfile
import os
from controllers.data_controller import DataController
from views.data_view import display_dataset_metadata, display_data_preview

# Konfigurasi halaman
st.set_page_config(
    page_title="Clustering Analysis App",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Clustering Analysis App")
st.markdown("Aplikasi untuk analisis clustering dengan DBI dan visualisasi SIG")

# Initialize controller
data_controller = DataController()

# Upload file
uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])

if uploaded_file is not None:
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Proses file
        with st.spinner("Memproses data..."):
            metadata, norm_result = data_controller.process_uploaded_file(
                tmp_file_path, uploaded_file.name
            )
        
        # Tampilkan hasil
        st.success("Data berhasil diproses!")
        
        # Tampilkan metadata
        display_dataset_metadata(metadata)
        
        # Tampilkan preview data
        display_data_preview(
            norm_result.original_data, 
            norm_result.normalized_data
        )
        
        # Simpan data di session state untuk tahap berikutnya
        st.session_state.dataset_metadata = metadata
        st.session_state.normalization_result = norm_result
        st.session_state.scaled_data = norm_result.scaled_data
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
    
    finally:
        # Hapus file sementara
        os.unlink(tmp_file_path)