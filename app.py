import streamlit as st
import tempfile
import os
from controllers.data_controller import DataController
from controllers.cluster_controller import ClusterController
from controllers.geo_controller import GeoController
from views.data_view import display_dataset_metadata, display_data_preview
from views.cluster_view import(
    display_dbi_evaluation_results,
    display_clustering_results,
    display_cluster_visualization,
    display_clustering_table,
    display_cluster_interpretation
)
from views.map_view import (
    display_shapefile_uploader,
    display_merge_report,
    display_choropleth_map,
    display_geodata_download_options
)

# Konfigurasi halaman
st.set_page_config(
    page_title="Clustering Analysis App",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Clustering Analysis App")
st.markdown("Aplikasi untuk analisis clustering dengan DBI dan visualisasi SIG")

# Initialize controllers
data_controller = DataController()
if "cluster_controller" not in st.session_state:
    st.session_state.cluster_controller = ClusterController()

# Tambahkan geo controller
if "geo_controller" not in st.session_state:
    st.session_state.geo_controller = GeoController()

cluster_controller = st.session_state.cluster_controller
geo_controller = st.session_state.geo_controller

# Inisialisasi session state
if 'dbi_evaluated' not in st.session_state:
    st.session_state.dbi_evaluated = False
if 'clustering_performed' not in st.session_state:
    st.session_state.clustering_performed = False
if 'clustering_table_created' not in st.session_state:
    st.session_state.clustering_table_created = False
if 'clustering_table' not in st.session_state:
    st.session_state.clustering_table = None
if 'interpretations' not in st.session_state:
    st.session_state.interpretations = None
if 'shapefile_processed' not in st.session_state:
    st.session_state.shapefile_processed = False
if 'geodata_merged' not in st.session_state:
    st.session_state.geodata_merged = False
if 'choropleth_map' not in st.session_state:
    st.session_state.choropleth_map = None
if 'merge_report' not in st.session_state:
    st.session_state.merge_report = None
if 'choropleth_map_attempted' not in st.session_state:  # Tambahkan state baru
    st.session_state.choropleth_map_attempted = False

# Upload file data CSV
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
        
        # Evaluasi DBI - tombol dengan status disabled jika sudah diklik
        if not st.session_state.dbi_evaluated:
            if st.button("🚀 Evaluasi DBI", type="primary"):
                with st.spinner("Melakukan evaluasi DBI..."):
                    evaluation_result = cluster_controller.perform_dbi_evaluation(
                        norm_result.scaled_data,
                        k_min=2,
                        k_max=6
                    )
                    
                    # Simpan hasil evaluasi di session state
                    st.session_state.evaluation_result = evaluation_result
                    st.session_state.dbi_evaluated = True
                    
                    # Refresh halaman untuk menampilkan hasil
                    st.rerun()
        else:
            st.button("🚀 Evaluasi DBI", disabled=True, help="Evaluasi DBI sudah dilakukan")
        
        # Tampilkan hasil evaluasi jika sudah ada di session state
        if 'evaluation_result' in st.session_state:
            display_dbi_evaluation_results(st.session_state.evaluation_result)
            
            # Clustering K-Means - tombol dengan status disabled jika sudah diklik
            if not st.session_state.clustering_performed:
                if st.button("🔍 Lakukan Clustering K-Means", type="primary"):
                    with st.spinner("Melakukan clustering K-Means..."):
                        clustering_result = cluster_controller.perform_kmeans_clustering(
                            st.session_state.scaled_data,
                            st.session_state.normalization_result.original_data,
                            st.session_state.normalization_result.normalized_data,
                            st.session_state.dataset_metadata.numeric_columns,
                            st.session_state.evaluation_result.best_k,
                            st.session_state.dataset_metadata.merge_key_column
                        )
                        
                        # Simpan hasil clustering di session state
                        st.session_state.clustering_result = clustering_result
                        st.session_state.clustering_performed = True
                        
                        # Refresh halaman untuk menampilkan hasil
                        st.rerun()
            else:
                st.button("🔍 Lakukan Clustering K-Means", disabled=True, help="Clustering sudah dilakukan")
            
            # Tampilkan hasil clustering jika sudah ada di session state
            if 'clustering_result' in st.session_state:
                display_clustering_results(st.session_state.clustering_result)
                display_cluster_visualization(
                    st.session_state.clustering_result,
                    st.session_state.scaled_data,
                    st.session_state.dataset_metadata.numeric_columns
                )
                
                # Tombol untuk menampilkan tabel lengkap - HANYA muncul setelah clustering selesai
                if not st.session_state.clustering_table_created:
                    if st.button("📊 Tampilkan Tabel Hasil Clustering Lengkap", type="primary"):
                        with st.spinner("Membuat tabel hasil clustering..."):
                            try:
                                clustering_table, interpretations = cluster_controller.create_clustering_table(
                                    st.session_state.dataset_metadata.merge_key_column,
                                    st.session_state.dataset_metadata.numeric_columns
                                )
                                
                                st.session_state.clustering_table = clustering_table
                                st.session_state.interpretations = interpretations
                                st.session_state.clustering_table_created = True
                                
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating clustering table: {str(e)}")
                else:
                    st.button("📊 Tampilkan Tabel Hasil Clustering Lengkap", disabled=True, 
                            help="Tabel sudah ditampilkan")
                
                # Tampilkan tabel dan interpretasi jika sudah dibuat
                if st.session_state.clustering_table is not None:
                    display_clustering_table(
                        st.session_state.clustering_table,
                        st.session_state.dataset_metadata.merge_key_column,
                        st.session_state.dataset_metadata.numeric_columns
                    )
                    
                    # Tambahkan opsi download dengan key unik
                    csv = st.session_state.clustering_table.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Tabel Hasil Clustering",
                        data=csv,
                        file_name="clustering_results.csv",
                        mime="text/csv",
                        key="unique_download_button_1"
                    )
                
                if st.session_state.interpretations is not None:
                    display_cluster_interpretation(st.session_state.interpretations)
                
                # Tampilkan opsi untuk upload shapefile setelah clustering selesai
                st.divider()
                st.subheader("Integrasi dengan Sistem Informasi Geografis")
                
                # Upload shapefile
                uploaded_shapefile = display_shapefile_uploader()

                if uploaded_shapefile is not None and not st.session_state.shapefile_processed:
                    if st.button("🗺️ Proses Shapefile", type="primary"):
                        with st.spinner("Memproses shapefile..."):
                            try:
                                # Proses shapefile
                                gdf, extract_dir = geo_controller.process_uploaded_shapefile(uploaded_shapefile)
                                st.session_state.shapefile_gdf = gdf
                                st.session_state.shapefile_extract_dir = extract_dir
                                st.session_state.shapefile_processed = True
                            except Exception as e:
                                st.error(f"Error processing shapefile: {str(e)}")

                # Merge data dengan geodata setelah shapefile diproses
                if (st.session_state.shapefile_processed and 
                    'clustering_result' in st.session_state and 
                    not st.session_state.geodata_merged):
                    
                    if st.button("🔗 Gabungkan dengan Data Geospatial", type="primary"):
                        with st.spinner("Menggabungkan data dengan geodata..."):
                            try:
                                # Merge data clustering dengan shapefile
                                merge_report = geo_controller.merge_with_geodata(
                                    st.session_state.clustering_result.merge_data,
                                    st.session_state.dataset_metadata.merge_key_column,
                                    st.session_state.dataset_metadata.numeric_columns
                                )
                                
                                st.session_state.merge_report = merge_report
                                st.session_state.geodata_merged = True
                            except Exception as e:
                                st.error(f"Error merging data with geodata: {str(e)}")

                # Tampilkan hasil merge dan buat peta
                if st.session_state.geodata_merged and st.session_state.merge_report:
                    display_merge_report(st.session_state.merge_report)
                    
                    if st.session_state.choropleth_map is None:
                        if st.button("🗺️ Buat Peta Choropleth", type="primary"):
                            st.session_state.choropleth_map_attempted = True
                            with st.spinner("Membuat peta choropleth..."):
                                try:
                                    # Pastikan semua data yang diperlukan tersedia
                                    if ('merge_report' in st.session_state and 
                                        'dataset_metadata' in st.session_state and 
                                        'evaluation_result' in st.session_state):
                                        
                                        # Buat peta choropleth
                                        choropleth_map = geo_controller.generate_choropleth_map(
                                            st.session_state.merge_report['merged_gdf'],
                                            st.session_state.dataset_metadata.numeric_columns,
                                            st.session_state.evaluation_result.best_k
                                        )
                                        
                                        # Simpan objek peta ke session state
                                        st.session_state.choropleth_map = choropleth_map
                                    else:
                                        st.error("Data yang diperlukan untuk membuat peta tidak tersedia.")
                                        
                                except Exception as e:
                                    st.error(f"Error creating choropleth map: {str(e)}")
                    
                    # Tampilkan peta jika sudah dibuat
                    if st.session_state.choropleth_map is not None:
                        # Pastikan merge_report juga tersedia
                        if 'merge_report' in st.session_state:
                            # Tampilkan peta tanpa pengecekan hasattr yang bermasalah
                            display_choropleth_map(st.session_state.choropleth_map)
                            
                            # Tampilkan opsi download
                            display_geodata_download_options(
                                st.session_state.merge_report['merged_gdf'],
                                filename_prefix="sultra_clustering"
                            )
                        else:
                            st.error("Data merge report tidak tersedia.")
                    else:
                        # Hanya tampilkan pesan error jika pengguna sudah mencoba membuat peta
                        if st.session_state.choropleth_map_attempted:
                            st.error("Objek peta tidak valid. Silakan buat peta kembali.")
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
    
    finally:
        # Hapus file sementara
        os.unlink(tmp_file_path)
        # Bersihkan file temporer shapefile
        if 'geo_controller' in st.session_state:
            st.session_state.geo_controller.cleanup_temp_files()

# Tambahkan tombol reset di sidebar
with st.sidebar:
    if st.button("🔄 Reset Aplikasi"):
        # Bersihkan file temporer shapefile
        if 'geo_controller' in st.session_state:
            st.session_state.geo_controller.cleanup_temp_files()
        
        # Hapus semua session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()