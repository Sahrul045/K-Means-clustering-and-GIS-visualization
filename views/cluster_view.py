import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from models.result_model import FullEvaluationResult, ClusteringResult
from services.clustering import visualize_clusters
from typing import Tuple, Dict, Any
import streamlit.components.v1 as components

def display_dbi_evaluation_results(evaluation_result: FullEvaluationResult):
    """Menampilkan hasil evaluasi DBI"""
    st.subheader("📈 Hasil Evaluasi DBI")
    
    # Tampilkan rekomendasi klaster terbaik
    st.success(f"**Rekomendasi Klaster Terbaik: k = {evaluation_result.best_k} (DBI = {evaluation_result.best_dbi:.4f})**")
    
    # Tampilkan tabel hasil
    st.write("**Tabel Hasil Evaluasi:**")
    table_data = []
    for result in evaluation_result.evaluation_results:
        table_data.append({
            'k': result.k,
            'SSW': f"{result.ssw:.4f}",
            'SSB': f"{result.ssb:.4f}",
            'DBI': f"{result.dbi:.4f}"
        })
    
    st.table(table_data)
    
    # Buat visualisasi
    fig, ax = plt.subplots(figsize=(10, 6))
    
    k_list = [result.k for result in evaluation_result.evaluation_results]
    dbi_list = [result.dbi for result in evaluation_result.evaluation_results]
    
    # Buat warna berbeda untuk klaster terbaik
    colors = ['skyblue' if k != evaluation_result.best_k else 'limegreen' for k in k_list]
    
    # Buat plot batang
    bars = ax.bar(k_list, dbi_list, color=colors, width=0.6)
    
    # Tambahkan nilai di atas batang
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.4f}', ha='center', va='bottom')
    
    # Tambahkan garis horizontal pada DBI terbaik
    ax.axhline(y=evaluation_result.best_dbi, color='r', linestyle='--', alpha=0.7)
    ax.text(max(k_list) + 0.5, evaluation_result.best_dbi,
            f'DBI Terbaik: {evaluation_result.best_dbi:.4f} (k={evaluation_result.best_k})',
            va='center', color='r')
    
    # Format plot
    ax.set_xticks(k_list)
    ax.set_xlabel('Jumlah Klaster (k)')
    ax.set_ylabel('Davies-Bouldin Index (DBI)')
    ax.set_title('Evaluasi Kualitas Klustering Berdasarkan DBI')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Tambahkan penjelasan DBI
    fig.text(0.5, 0.01,
            "Catatan: Nilai DBI yang lebih rendah menunjukkan kualitas klaster yang lebih baik. "
            "DBI mengukur rasio rata-rata dispersi intra-klaster terhadap pemisahan antar-klaster.",
            ha="center", fontsize=10, style='italic')
    
    plt.tight_layout()
    
    # Tampilkan plot di Streamlit
    st.pyplot(fig)
    
    # Tambahkan penjelasan tentang metrik
    with st.expander("ℹ️ Penjelasan Metrik"):
        st.markdown("""
        - **SSW (Sum of Squared Within-cluster)**: Mengukur sebaran data dalam klaster. Nilai lebih kecil berarti klaster lebih kompak.
        - **SSB (Sum of Squared Between-cluster)**: Mengukur pemisahan antar klaster. Nilai lebih besar berarti klaster lebih terpisah.
        - **DBI (Davies-Bouldin Index)**: Mengukur rasio antara dispersi intra-klaster dan pemisahan antar-klaster. 
        Nilai lebih kecil menunjukkan kualitas klaster yang lebih baik.
        """)
        
def display_clustering_results(clustering_result: ClusteringResult):
    """Menampilkan hasil clustering"""
    st.subheader("🔍 Hasil Clustering K-Means")
    
    # Tampilkan distribusi cluster
    st.write("**Distribusi Data per Cluster:**")
    cluster_counts_df = pd.DataFrame.from_dict(
        clustering_result.cluster_counts, 
        orient='index', 
        columns=['Jumlah Data']
    )
    st.table(cluster_counts_df)
    
    # Tampilkan karakteristik cluster
    st.write("**Karakteristik Cluster (Rata-rata):**")
    st.dataframe(clustering_result.cluster_summary)
    
    # Tampilkan data untuk merge jika tersedia
    if clustering_result.merge_data is not None:
        st.write("**Data untuk Merge dengan Shapefile:**")
        st.dataframe(clustering_result.merge_data.head())
        
        # Tambahkan opsi download
        csv = clustering_result.merge_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Data untuk Merge",
            data=csv,
            file_name="merge_data.csv",
            mime="text/csv",
            key="download_merge_data"
        )

def display_cluster_visualization(clustering_result: ClusteringResult, scaled_data: np.ndarray, numeric_cols: list):
    """Menampilkan visualisasi cluster"""
    st.subheader("📊 Visualisasi Cluster")
    
    # Buat visualisasi
    fig = visualize_clusters(
        scaled_data, 
        clustering_result.clusters, 
        clustering_result.centroids, 
        numeric_cols
    )
    
    # Tampilkan plot di Streamlit
    st.pyplot(fig)
    
    # Tambahkan penjelasan tentang visualisasi
    with st.expander("ℹ️ Penjelasan Visualisasi"):
        if len(numeric_cols) == 2:
            st.markdown("""
            Visualisasi ini menunjukkan distribusi data dalam 2D menggunakan dua fitur asli:
            - **Titik berwarna**: Data point yang dikelompokkan ke dalam cluster
            - **Tanda X merah**: Centroid (pusat) dari setiap cluster
            """)
        else:
            st.markdown("""
            Visualisasi ini menunjukkan distribusi data dalam 2D menggunakan PCA (Principal Component Analysis):
            - **PCA**: Teknik reduksi dimensi yang memproyeksikan data multi-dimensi ke dalam 2D
            - **Titik berwarna**: Data point yang dikelompokkan ke dalam cluster
            - **Tanda X merah**: Centroid (pusat) dari setiap cluster
            - **Variansi yang dijelaskan**: Persentase informasi dari data asli yang dipertahankan dalam visualisasi 2D
            """)

def display_clustering_table(
    clustering_table: pd.DataFrame, 
    region_column: str,
    numeric_cols: list
):
    """Menampilkan tabel hasil clustering dengan styling"""
    st.subheader("📋 Tabel Hasil Clustering Lengkap")
    
    # Buat salinan untuk styling
    styled_df = clustering_table.copy()
    
    # Fungsi untuk warna cluster dengan kontras tinggi
    def color_cluster(val):
        # Warna dengan kontras tinggi untuk mode terang dan gelap
        colors = {
            0: 'background-color: #FF6B6B; color: black;',  # Merah terang
            1: 'background-color: #4ECDC4; color: black;',  # Turquoise
            2: 'background-color: #FFE66D; color: black;',  # Kuning terang
            3: 'background-color: #6A0572; color: white;',  # Ungu tua (teks putih)
            4: 'background-color: #FF9A8B; color: black;',  # Salmon
            5: 'background-color: #5C80BC; color: white;',  # Biru (teks putih)
            6: 'background-color: #8AC926; color: black;',  # Hijau terang
        }
        if val.name == 'Cluster':
            return [colors.get(v % 7, 'background-color: #CCCCCC; color: black;') for v in val]
        return [''] * len(val)
    
    # Format numerik
    format_dict = {'Jarak ke Centroid': '{:.6f}'}
    for col in numeric_cols:
        format_dict[f"{col} (Norm)"] = '{:.6f}'
    
    # Tampilkan tabel dengan styling
    st.dataframe(
        styled_df.style
        .apply(color_cluster, axis=0)
        .format(format_dict)
        .set_properties(**{
            'text-align': 'center', 
            'border': '1px solid black',
            'font-weight': 'normal'
        })
        .set_table_styles([{
            'selector': 'th',
            'props': [
                ('background-color', '#404040'), 
                ('color', 'white'),
                ('font-weight', 'bold'),
                ('text-align', 'center'),
                ('border', '1px solid black')
            ]
        }, {
            'selector': 'td',
            'props': [
                ('border', '1px solid black'),
                ('padding', '5px')
            ]
        }]),
        use_container_width=True,
        height=400
    )

def display_cluster_interpretation(interpretations: Dict[int, Dict[str, Any]]):
    """Menampilkan interpretasi cluster"""
    st.subheader("📋 Interpretasi Cluster")
    
    for cluster_id, interpretation in interpretations.items():
        # Header cluster
        st.markdown(f"### Cluster {cluster_id} ({interpretation['count']} wilayah)")
        
        # Tampilkan deskripsi
        st.write(interpretation['description'])
        
        # Tampilkan rata-rata nilai fitur dalam bentuk tabel
        st.write("**Rata-rata Nilai Fitur:**")
        means_df = pd.DataFrame.from_dict(
            interpretation['means'], 
            orient='index', 
            columns=['Nilai Rata-rata']
        ).round(4)
        
        # Style tabel rata-rata
        st.dataframe(
            means_df.style
            .set_properties(**{
                'text-align': 'center',
                'border': '1px solid #ddd'
            })
            .set_table_styles([{
                'selector': 'th',
                'props': [
                    ('background-color', '#f0f0f0'),
                    ('color', 'black'),
                    ('font-weight', 'bold'),
                    ('text-align', 'center')
                ]
            }])
        )
        
        # Pembatas antar cluster
        if cluster_id < len(interpretations) - 1:
            st.markdown("---")