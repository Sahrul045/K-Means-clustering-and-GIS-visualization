import streamlit as st

def render_sidebar():
    """Render sidebar dengan status progress dan reset button"""
    with st.sidebar:
        st.title("📊 Clustering Analysis")
        
        # Progress status
        st.subheader("Progress Status")
        
        # Daftar status yang akan ditampilkan
        status_items = [
            ("Data Processing", 'data_processed'),
            ("DBI Evaluation", 'evaluation_complete'), 
            ("Clustering", 'clustering_complete'),
            ("Spatial Visualization", 'geodata_merged')
        ]
        
        # Tampilkan status untuk setiap item
        for label, key in status_items:
            if st.session_state.get(key):
                st.success(f"✅ {label}")
            else:
                st.info(f"⏳ {label}")
        
        # Reset button
        st.divider()
        if st.button("🔄 Reset Aplikasi", use_container_width=True, type="secondary"):
            # Bersihkan file temporer shapefile
            if 'geo_controller' in st.session_state:
                st.session_state.geo_controller.cleanup_temp_files()
            
            # Hapus semua session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Rerun aplikasi
            st.rerun()