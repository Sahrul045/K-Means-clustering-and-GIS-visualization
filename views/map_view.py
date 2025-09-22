import streamlit as st
from streamlit_folium import st_folium
import tempfile
import os
import zipfile

def display_shapefile_option():
    """Menampilkan opsi pemilihan shapefile"""
    st.subheader("Pilihan Shapefile")
    
    option = st.radio(
        "Pilih sumber shapefile:",
        ["Default", "Custom"],
        help="Pilih 'Default' untuk menggunakan shapefile bawaan sistem atau 'Custom' untuk mengunggah sendiri",
        key="shapefile_option"
    )
    
    uploaded_zip = None
    if option == "Custom":
        uploaded_zip = st.file_uploader(
            "Unggah file ZIP shapefile Sulawesi Tenggara", 
            type=["zip"],
            help="File ZIP harus berisi shapefile (.shp, .shx, .dbf, etc.) untuk wilayah Sulawesi Tenggara",
            key="shapefile_uploader"
        )
    else:
        st.info("Menggunakan shapefile default untuk Sulawesi Tenggara.")
    
    return uploaded_zip, option

def display_merge_report(merge_report):
    """Menampilkan laporan hasil merge data"""
    st.subheader("Laporan Integrasi Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Wilayah Berhasil Dimatch", 
            f"{merge_report['total_matched']} wilayah"
        )
    
    with col2:
        st.metric(
            "Wilayah Tidak Match", 
            f"{len(merge_report['missing_in_shapefile'])} wilayah"
        )
    
    if len(merge_report['missing_in_shapefile']) > 0:
        with st.expander("Detail Wilayah yang Tidak Match dengan Shapefile"):
            st.write("Wilayah berikut ada dalam data clustering tetapi tidak ditemukan dalam shapefile:")
            st.dataframe(merge_report['missing_in_shapefile'])
    
    if len(merge_report['missing_in_data']) > 0:
        with st.expander("Detail Wilayah dalam Shapefile tanpa Data Clustering"):
            st.write("Wilayah berikut ada dalam shapefile tetapi tidak memiliki data clustering:")
            st.dataframe(merge_report['missing_in_data'])

def display_choropleth_map(choropleth_map, height=600):
    """
    Menampilkan peta choropleth di Streamlit
    
    Args:
        choropleth_map: Objek peta Folium
        height (int): Tinggi peta dalam piksel
    """
    # Simplifikasi pengecekan - cukup pastikan bukan None
    if choropleth_map is None:
        st.error("Objek peta tidak valid. Silakan buat peta kembali.")
        return
    
    st.subheader("🗺️ Peta Sebaran Cluster")
    
    # Gunakan container untuk mencegah rerender yang tidak perlu
    with st.container():
        # Tampilkan peta dengan key unik
        st_folium(
            choropleth_map, 
            width=700, 
            height=height,
            key="choropleth_map"
        )
    
    # Tambahkan penjelasan
    st.caption("""
    Peta di atas menunjukkan sebaran cluster di wilayah Sulawesi Tenggara.
    Setiap warna mewakili cluster yang berbeda.
    """)
    

def display_geodata_download_options(gdf, filename_prefix="clustering"):
    """Menampilkan opsi download untuk data geospatial"""
    st.subheader("💾 Download Data Geospatial")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download sebagai GeoJSON
        geojson_str = gdf.to_json()
        st.download_button(
            label="Download GeoJSON",
            data=geojson_str,
            file_name=f"{filename_prefix}_geodata.geojson",
            mime="application/json",
            key="geojson_download"
        )
    
    with col2:
        # Download sebagai Shapefile (zip)
        with tempfile.TemporaryDirectory() as tmp_dir:
            shp_path = os.path.join(tmp_dir, f"{filename_prefix}.shp")
            gdf.to_file(shp_path, encoding='utf-8') 
            
            # Buat zip file
            zip_path = os.path.join(tmp_dir, f"{filename_prefix}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in os.listdir(tmp_dir):
                    if file.endswith(('.shp', '.shx', '.dbf', '.prj', '.cpg')):
                        zipf.write(os.path.join(tmp_dir, file), file)
            
            # Baca zip file untuk download
            with open(zip_path, "rb") as f:
                zip_data = f.read()
            
            st.download_button(
                label="Download Shapefile (ZIP)",
                data=zip_data,
                file_name=f"{filename_prefix}_shapefile.zip",
                mime="application/zip",
                key="shapefile_download"
            )