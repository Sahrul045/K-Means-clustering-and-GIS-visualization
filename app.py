# source venv/bin/activate
import pandas as pd
import streamlit as st
import tempfile
import os
from controllers.data_controller import DataController
from controllers.cluster_controller import ClusterController
from controllers.geo_controller import GeoController
from views.sidebar import render_sidebar
from views.data_view import display_dataset_metadata, display_data_preview
from views.cluster_view import(
    display_dbi_evaluation_results,
    display_clustering_results,
    display_cluster_visualization,
    display_clustering_table,
    display_cluster_interpretation
)
from views.map_view import (
    display_shapefile_option,
    display_merge_report,
    display_choropleth_map,
    display_geodata_download_options
)

# Konfigurasi halaman
st.set_page_config(
    page_title="Clustering Analysis App",
    page_icon="📊",
    layout="centered"
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
if 'map_data' not in st.session_state:
    st.session_state.map_data = None
if 'merge_report' not in st.session_state:
    st.session_state.merge_report = None
if 'shapefile_option' not in st.session_state:  # Tambahkan state untuk opsi shapefile
    st.session_state.shapefile_option = "Default"

# Tambahkan inisialisasi untuk status progress
if 'data_processed' not in st.session_state:
    st.session_state.data_processed = False
if 'evaluation_complete' not in st.session_state:
    st.session_state.evaluation_complete = False
if 'clustering_complete' not in st.session_state:
    st.session_state.clustering_complete = False

# Panggil sidebar
render_sidebar()

# SECTION 1: DATA PROCESSING

st.header("⏳ Data Processing")
st.markdown("Unggah dan proses data untuk persiapan analisis clustering.")

uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"], key="data_uploader")

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
        
        st.success("✅ Data berhasil diproses!")
        
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
        st.session_state.data_processed = True
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
    
    finally:
        # Hapus file sementara
        os.unlink(tmp_file_path)

# Divider antara section
st.divider()


# SECTION 2: DBI EVALUATION

st.header("🧮 DBI Evaluation")
st.markdown("Evaluasi kualitas clustering menggunakan Davies-Bouldin Index (DBI).")

if 'data_processed' in st.session_state and st.session_state.data_processed:
    # Evaluasi DBI - tombol dengan status disabled jika sudah diklik
    if not st.session_state.dbi_evaluated:
        if st.button("🚀 Evaluasi DBI", type="primary", key="dbi_button"):
            with st.spinner("Melakukan evaluasi DBI..."):
                evaluation_result = cluster_controller.perform_dbi_evaluation(
                    st.session_state.scaled_data,
                    k_min=2,
                    k_max=6
                )
                
                # Simpan hasil evaluasi di session state
                st.session_state.evaluation_result = evaluation_result
                st.session_state.dbi_evaluated = True
                st.session_state.evaluation_complete = True
                
                # Refresh halaman untuk menampilkan hasil
                st.rerun()
    else:
        st.button("🚀 Evaluasi DBI", disabled=True, help="Evaluasi DBI sudah dilakukan", key="dbi_button_disabled")

    # Tampilkan hasil evaluasi jika sudah ada di session state
    if 'evaluation_result' in st.session_state:
        display_dbi_evaluation_results(st.session_state.evaluation_result)
else:
    st.info("ℹ️ Silakan lengkapi proses data terlebih dahulu untuk melakukan evaluasi DBI.")

# Divider antara section
st.divider()


# SECTION 3: CLUSTERING

st.header("📊 Clustering")
st.markdown("Lakukan clustering K-Means berdasarkan hasil evaluasi DBI.")

if 'evaluation_complete' in st.session_state and st.session_state.evaluation_complete:
    # Clustering K-Means - tombol dengan status disabled jika sudah diklik
    if not st.session_state.clustering_performed:
        if st.button("🔍 Lakukan Clustering K-Means", type="primary", key="clustering_button"):
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
                st.session_state.clustering_complete = True
                
                # Refresh halaman untuk menampilkan hasil
                st.rerun()
    else:
        st.button("🔍 Lakukan Clustering K-Means", disabled=True, help="Clustering sudah dilakukan", key="clustering_button_disabled")
    
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
            if st.button("📊 Tampilkan Tabel Hasil Clustering Lengkap", type="primary", key="table_button"):
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
                    help="Tabel sudah ditampilkan", key="table_button_disabled")
        
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
else:
    st.info("ℹ️ Silakan lengkapi evaluasi DBI terlebih dahulu untuk melakukan clustering.")

# Divider antara section
st.divider()

# 4: SPATIAL VISUALIZATION

st.header("🗺️ Spatial Visualization")
st.markdown("Integrasikan hasil clustering dengan data geospasial untuk visualisasi peta.")

if 'clustering_complete' in st.session_state and st.session_state.clustering_complete:
    # Inisialisasi shapefile_option jika belum ada
    if 'shapefile_option' not in st.session_state:
        st.session_state.shapefile_option = "Default"
    
    # Cek apakah shapefile sudah diproses
    if st.session_state.shapefile_processed:
        # Tampilkan opsi shapefile yang dinonaktifkan
        st.radio(
            "Pilih sumber shapefile:",
            ["Default", "Custom"],
            help="Pilihan shapefile sudah ditentukan. Reset aplikasi untuk mengubah.",
            key="shapefile_option_disabled",
            index=0 if st.session_state.shapefile_option == "Default" else 1,
            disabled=True
        )
        
        # Tampilkan tombol reset
        if st.button("🔄 Reset Pilihan Shapefile", key="reset_shapefile_btn"):
            st.session_state.shapefile_processed = False
            st.session_state.geodata_merged = False
            st.session_state.map_data = None
            st.session_state.merge_report = None
            geo_controller.cleanup_temp_files()
            st.rerun()
    else:
        # Upload shapefile dengan opsi default/custom
        uploaded_shapefile, selected_option = display_shapefile_option()
        
        # Gunakan callback untuk mengupdate session state
        if selected_option != st.session_state.shapefile_option:
            st.session_state.shapefile_option = selected_option
            st.rerun()

    # Tombol proses shapefile (hanya tampil jika belum diproses)
    if not st.session_state.shapefile_processed:
        if st.button("🗺️ Proses Shapefile", type="primary", key="shapefile_button"):
            with st.spinner("Memproses shapefile..."):
                try:
                    if st.session_state.shapefile_option == "Default":
                        # Gunakan shapefile default
                        success = geo_controller.load_default_shapefile()
                        if success:
                            st.session_state.shapefile_processed = True
                            st.success("Shapefile default berhasil dimuat!")
                            st.rerun()
                        else:
                            st.error("Gagal memuat shapefile default. Silakan hubungi administrator.")
                    else:
                        # Gunakan shapefile custom
                        if uploaded_shapefile is not None:
                            gdf, extract_dir = geo_controller.process_uploaded_shapefile(uploaded_shapefile)
                            st.session_state.shapefile_gdf = gdf
                            st.session_state.shapefile_extract_dir = extract_dir
                            st.session_state.shapefile_processed = True
                            st.rerun()
                        else:
                            st.error("Silakan unggah file shapefile untuk opsi custom.")
                except Exception as e:
                    st.error(f"Error processing shapefile: {str(e)}")

    # Merge data dengan geodata setelah shapefile diproses
    if (st.session_state.shapefile_processed and 
        'clustering_result' in st.session_state and 
        not st.session_state.geodata_merged):
        
        if st.button("🔗 Gabungkan dengan Data Geospatial", type="primary", key="merge_button"):
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
                    st.rerun()
                except Exception as e:
                    st.error(f"Error merging data with geodata: {str(e)}")

    # Tampilkan hasil merge dan buat peta
    if st.session_state.geodata_merged and st.session_state.merge_report:
        display_merge_report(st.session_state.merge_report)
        
        # Simpan data yang diperlukan untuk membuat peta
        st.session_state.map_data = {
            'merged_gdf': st.session_state.merge_report['merged_gdf'],
            'numeric_cols': st.session_state.dataset_metadata.numeric_columns,
            'best_k': st.session_state.evaluation_result.best_k
        }
        
        # Buat dan tampilkan peta
        if st.session_state.map_data is not None:
            try:
                choropleth_map = geo_controller.generate_choropleth_map(
                    st.session_state.map_data['merged_gdf'],
                    st.session_state.map_data['numeric_cols'],
                    st.session_state.map_data['best_k']
                )
                
                # Tampilkan peta
                display_choropleth_map(choropleth_map)
                
                # Tampilkan opsi download
                display_geodata_download_options(
                    st.session_state.merge_report['merged_gdf'],
                    filename_prefix="sultra_clustering"
                )
            except Exception as e:
                st.error(f"Error creating choropleth map: {str(e)}")
else:
    st.info("ℹ️ Silakan lengkapi proses clustering terlebih dahulu untuk visualisasi spasial.")

# Divider antara section
st.divider()

# SECTION 5: FINAL INTERPRETATION

st.header("📋 Final Interpretation")
st.markdown("Ringkasan dan interpretasi keseluruhan proses analisis clustering.")

if all([st.session_state.data_processed, 
        st.session_state.evaluation_complete, 
        st.session_state.clustering_complete,
        st.session_state.geodata_merged]):

    # Container untuk interpretasi
    with st.container():
        st.subheader("Ringkasan Proses Analisis")
        
        # 1. Informasi Dataset
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Data", st.session_state.dataset_metadata.filename)
        with col2:
            st.metric("Jumlah Observasi", len(st.session_state.normalization_result.original_data))
        with col3:
            st.metric("Variabel Numerik", len(st.session_state.dataset_metadata.numeric_columns))
        
        # 2. Hasil Evaluasi DBI
        st.subheader("📈 Hasil Evaluasi DBI")
        eval_df = pd.DataFrame([{
            'K': result.k,
            'SSW': f"{result.ssw:.4f}",
            'SSB': f"{result.ssb:.4f}", 
            'DBI': f"{result.dbi:.4f}"
        } for result in st.session_state.evaluation_result.evaluation_results])
        
        st.dataframe(eval_df, use_container_width=True)
        st.info(f"**Cluster optimal**: K = {st.session_state.evaluation_result.best_k} "
                f"(DBI = {st.session_state.evaluation_result.best_dbi:.4f})")
        
        # 3. Hasil Clustering
        st.subheader("🔍 Hasil Clustering")
        if st.session_state.interpretations:
            for cluster_id, interpretation in st.session_state.interpretations.items():
                # Gunakan judul yang sesuai dengan struktur data yang ada
                with st.expander(f"Cluster {cluster_id} ({interpretation['count']} wilayah)"):
                    st.write(f"**Karakteristik**: {interpretation['description']}")
                    
                    # PERBAIKAN: Gunakan 'means' bukan 'characteristics'
                    stats_df = pd.DataFrame.from_dict(interpretation['means'], orient='index')
                    stats_df.columns = ['Nilai Rata-rata']
                    st.dataframe(stats_df, use_container_width=True)
        
        # 4. Interpretasi Spasial
        st.subheader("🗺️ Interpretasi Spasial")
        if st.session_state.merge_report:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Wilayah Terpetakan", f"{st.session_state.merge_report['total_matched']}")
            with col2:
                st.metric("Wilayah Tidak Match", f"{len(st.session_state.merge_report['missing_in_shapefile'])}")
            
            # Interpretasi pola spasial
            st.write("**Pola Spasial**:")
            # PERBAIKAN: Gunakan .empty untuk mengecek DataFrame
            if not st.session_state.merge_report['missing_in_shapefile'].empty:
                st.warning("Beberapa wilayah dalam data tidak memiliki representasi dalam shapefile. "
                    "Ini dapat mempengaruhi interpretasi pola spasial."
                )
            else:
                st.success("Semua wilayah memiliki representasi dalam shapefile")
                
        # 5. Analisis Teknis Clustering
        st.subheader("🔬 Analisis Teknis Clustering")
        st.write("Berdasarkan analisis clustering menggunakan Davies-Bouldin Index (DBI), berikut temuan teknis yang dapat disimpulkan:")

        # Analisis kualitas clustering berdasarkan DBI - Tampilkan selalu (sebagai ringkasan utama)
        best_dbi = st.session_state.evaluation_result.best_dbi
        if best_dbi < 0.5:
            quality_assessment = "sangat baik"
            explanation = "Cluster yang dihasilkan sangat kompak dan terpisah dengan jelas"
        elif best_dbi < 1.0:
            quality_assessment = "baik" 
            explanation = "Cluster yang dihasilkan kompak dan cukup terpisah"
        elif best_dbi < 2.0:
            quality_assessment = "cukup"
            explanation = "Cluster yang dihasilkan cukup kompak tetapi ada beberapa overlap"
        else:
            quality_assessment = "kurang optimal"
            explanation = "Cluster yang dihasilkan kurang kompak dan banyak overlap"

        st.success(f"**Kualitas Clustering**: {quality_assessment} (DBI = {best_dbi:.4f})")
        st.info(f"{explanation}")

        # Gunakan expander untuk detail teknis
        with st.expander("📊 Detail Analisis Metrik", expanded=False):
            # Analisis metrik evaluasi
            best_result = None
            for result in st.session_state.evaluation_result.evaluation_results:
                if result.k == st.session_state.evaluation_result.best_k:
                    best_result = result
                    break
            
            if best_result:
                st.write("**Analisis Metrik:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("SSW", f"{best_result.ssw:.4f}", 
                            help="Sum of Squared Within-cluster: Mengukur sebaran data dalam klaster. Nilai lebih kecil berarti klaster lebih kompak.")
                with col2:
                    st.metric("SSB", f"{best_result.ssb:.4f}", 
                            help="Sum of Squared Between-cluster: Mengukur pemisahan antar klaster. Nilai lebih besar berarti klaster lebih terpisah.")
                with col3:
                    st.metric("DBI", f"{best_result.dbi:.4f}", 
                            help="Davies-Bouldin Index: Mengukur rasio antara dispersi intra-klaster dan pemisahan antar-klaster.")
                
                # Interpretasi nilai
                st.write("**Interpretasi Nilai:**")
                st.write("- **SSW**: Nilai lebih kecil menunjukkan cluster lebih kompak")
                st.write("- **SSB**: Nilai lebih besar menunjukkan pemisahan cluster lebih baik")
                st.write("- **DBI**: Nilai lebih kecil menunjukkan kualitas clustering lebih baik")

        with st.expander("⭐ Keunggulan DBI", expanded=False):
            st.write("**Keunggulan DBI dalam Pemilihan Cluster Optimal:**")
            advantages = [
                "**Objektif**: Memberikan nilai kuantitatif yang jelas tanpa subjektivitas visual seperti elbow method",
                "**Komprehensif**: Mempertimbangkan both within-cluster variance (SSW) dan between-cluster separation (SSB)",
                "**Robust**: Lebih tahan terhadap noise dan outliers dibanding silhouette score",
                "**Interpretable**: Nilai DBI yang lebih rendah secara konsisten menunjukkan kualitas clustering yang lebih baik"
            ]
            
            for advantage in advantages:
                st.write(f"- {advantage}")

        with st.expander("⚙️ Implementasi Teknis", expanded=False):
            st.write("**Implementasi Teknis:**")
            implementations = [
                "Algoritma K-Means berhasil mengelompokkan data dengan efisien",
                "Normalisasi data memastikan semua fitur berkontribusi secara seimbang dalam proses clustering",
                "Integrasi dengan SIG memungkinkan visualisasi spasial yang memperkaya interpretasi hasil"
            ]
            
            for implementation in implementations:
                st.write(f"- {implementation}")

        with st.expander("📈 Distribusi Cluster", expanded=False):
            if st.session_state.interpretations and st.session_state.merge_report:
                # Analisis distribusi cluster
                cluster_distribution = st.session_state.clustering_result.cluster_counts
                dominant_cluster = max(cluster_distribution, key=cluster_distribution.get)
                
                st.write("**Distribusi Cluster:**")
                st.write(f"- Cluster {dominant_cluster} memiliki anggota terbanyak ({cluster_distribution[dominant_cluster]} wilayah)")
                
                # Tampilkan chart distribusi cluster
                dist_df = pd.DataFrame({
                    'Cluster': list(cluster_distribution.keys()),
                    'Jumlah Wilayah': list(cluster_distribution.values())
                })
                
                # Urutkan berdasarkan cluster
                dist_df = dist_df.sort_values('Cluster')
                
                # Tampilkan chart
                st.bar_chart(dist_df.set_index('Cluster'))
                
                # Tampilkan tabel detail
                st.write("**Detail Distribusi:**")
                for cluster_id, count in cluster_distribution.items():
                    st.write(f"- Cluster {cluster_id}: {count} wilayah")

        # 6. Download Report
        st.subheader("📥 Download Laporan Lengkap")
        if st.button("💾 Generate Full Report", key="generate_report_btn"):
            with st.spinner("Membuat laporan lengkap..."):
                try:
                    # Pastikan method tersedia
                    if hasattr(cluster_controller, 'generate_comprehensive_report'):
                        report_content = cluster_controller.generate_comprehensive_report()
                        st.download_button(
                            label="Download Laporan Lengkap",
                            data=report_content,
                            file_name="clustering_analysis_report.md",
                            mime="text/markdown",
                            key="report_download"
                        )
                    else:
                        st.error("Fitur generate laporan tidak tersedia")
                except Exception as e:
                    st.error(f"Gagal membuat laporan: {str(e)}")

else:
    st.info("ℹ️ Silakan lengkapi seluruh proses analisis untuk melihat interpretasi akhir.")