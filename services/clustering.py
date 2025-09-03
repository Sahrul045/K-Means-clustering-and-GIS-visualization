import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Tuple, Dict, Any, Optional
import matplotlib.pyplot as plt

def perform_kmeans_clustering(
    scaled_data: np.ndarray, 
    best_k: int, 
    random_state: int = 42
) -> Dict[str, Any]:
    """Melakukan clustering K-Means dengan nilai k terbaik"""
    kmeans_final = KMeans(n_clusters=best_k, random_state=random_state, n_init=10)
    clusters = kmeans_final.fit_predict(scaled_data)
    centroids = kmeans_final.cluster_centers_
    
    return {
        'clusters': clusters,
        'centroids': centroids,
        'model': kmeans_final
    }

def add_clusters_to_data(
    original_df: pd.DataFrame, 
    normalized_df: pd.DataFrame, 
    clusters: np.ndarray
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Menambahkan hasil clustering ke DataFrame"""
    df_with_clusters = original_df.copy()
    df_norm_with_clusters = normalized_df.copy()
    
    df_with_clusters['Cluster'] = clusters
    df_norm_with_clusters['Cluster'] = clusters
    
    return df_with_clusters, df_norm_with_clusters

def analyze_cluster_characteristics(
    df: pd.DataFrame, 
    numeric_cols: list, 
    clusters: np.ndarray
) -> Dict[str, Any]:
    """Menganalisis karakteristik cluster"""
    df_with_clusters = df.copy()
    df_with_clusters['Cluster'] = clusters
    
    cluster_summary = df_with_clusters.groupby('Cluster')[numeric_cols].mean()
    cluster_counts = df_with_clusters['Cluster'].value_counts().sort_index()
    
    return {
        'cluster_summary': cluster_summary,
        'cluster_counts': cluster_counts.to_dict()
    }

def prepare_data_for_merge(
    df: pd.DataFrame, 
    clusters: np.ndarray, 
    centroids: np.ndarray, 
    numeric_cols: list, 
    merge_key_column: Optional[str] = None
) -> Tuple[pd.DataFrame, str]:
    """Mempersiapkan data untuk merge dengan shapefile"""
    if merge_key_column is None:
        raise ValueError("Tidak ada kolom kunci untuk merge dengan shapefile")
    
    # Buat DataFrame khusus untuk merge
    merge_data = df[[merge_key_column, 'Cluster']].copy()
    
    # Tambahkan informasi centroid untuk analisis spasial
    for i, col in enumerate(numeric_cols):
        merge_data[f'Centroid_{col}'] = [centroids[cluster, i] for cluster in clusters]
    
    return merge_data

def visualize_clusters(
    scaled_data: np.ndarray, 
    clusters: np.ndarray, 
    centroids: np.ndarray, 
    numeric_cols: list
):
    """Membuat visualisasi cluster"""
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 8))
    
    if len(numeric_cols) == 2:
        # Visualisasi langsung jika hanya 2 fitur
        plt.scatter(scaled_data[:, 0], scaled_data[:, 1], c=clusters,
                    cmap='viridis', s=80, alpha=0.7, edgecolor='k')
        plt.scatter(centroids[:, 0], centroids[:, 1], c='red',
                    marker='X', s=200, label='Centroids')
        plt.xlabel(numeric_cols[0])
        plt.ylabel(numeric_cols[1])
    else:
        # Gunakan PCA untuk reduksi dimensi jika fitur > 2
        pca = PCA(n_components=2)
        data_pca = pca.fit_transform(scaled_data)
        centroids_pca = pca.transform(centroids)
        
        plt.scatter(data_pca[:, 0], data_pca[:, 1], c=clusters,
                    cmap='viridis', s=80, alpha=0.7, edgecolor='k')
        plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], c='red',
                    marker='X', s=200, label='Centroids')
        
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 2")
        plt.title("Visualisasi PCA (Reduksi Dimensi)", fontsize=12)
        
        # Tambahkan persentase varian yang dijelaskan
        var_ratio = pca.explained_variance_ratio_
        plt.figtext(0.5, 0.01,
                    f"PCA menjelaskan {var_ratio[0]*100:.1f}% + {var_ratio[1]*100:.1f}% = {sum(var_ratio)*100:.1f}% variansi data",
                    ha="center", fontsize=10)
    
    plt.title(f"K-Means Clustering (k={len(np.unique(clusters))})", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    return plt

# cell code 4
def create_clustering_table(
    original_df: pd.DataFrame,
    normalized_df: pd.DataFrame,
    clusters: np.ndarray,
    centroids: np.ndarray,
    numeric_cols: list,
    region_column: str
) -> pd.DataFrame:
    """
    Membuat tabel hasil clustering lengkap
    """
    # 1. Ambil nama wilayah
    wilayah_names = original_df[region_column].values
    
    # 2. Buat DataFrame untuk hasil clustering
    results_df = pd.DataFrame({
        region_column: wilayah_names
    })
    
    # 3. Tambahkan nilai asli
    for col in numeric_cols:
        results_df[col] = original_df[col].values
    
    # 4. Tambahkan nilai normalisasi
    for col in numeric_cols:
        results_df[f"{col} (Norm)"] = normalized_df[col].values
    
    # 5. Tambahkan cluster assignment
    results_df['Cluster'] = clusters
    
    # 6. Hitung jarak setiap titik ke centroid clusternya
    distances = []
    for i in range(len(normalized_df)):
        cluster_id = clusters[i]
        # Gunakan hanya kolom numerik untuk menghitung jarak
        point = normalized_df[numeric_cols].iloc[i].values
        dist = np.linalg.norm(point - centroids[cluster_id])
        distances.append(dist)
    
    results_df['Jarak ke Centroid'] = distances
    
    # 7. Tambahkan koordinat centroid untuk setiap baris
    centroid_coords = []
    for cluster_id in clusters:
        centroid_coords.append(f"{centroids[cluster_id].round(4)}")
    
    results_df['Koordinat Centroid'] = centroid_coords
    
    # 8. Urutkan berdasarkan cluster
    results_df = results_df.sort_values(by='Cluster')
    
    return results_df

def interpret_clusters(
    original_df: pd.DataFrame, 
    numeric_cols: list, 
    clusters: np.ndarray
) -> Dict[int, Dict[str, Any]]:
    """
    Membuat interpretasi untuk setiap cluster
    """
    original_df = original_df.copy()
    original_df['Cluster'] = clusters
    
    interpretations = {}
    unique_clusters = np.unique(clusters)
    
    for cluster_id in unique_clusters:
        cluster_data = original_df[original_df['Cluster'] == cluster_id]
        interpretation = {
            'count': len(cluster_data),
            'means': {},
            'description': f"Cluster {cluster_id} memiliki {len(cluster_data)} wilayah dengan karakteristik:"
        }
        
        # Hitung rata-rata untuk setiap fitur numerik
        for col in numeric_cols:
            interpretation['means'][col] = cluster_data[col].mean()
        
        # Buat deskripsi yang lebih informatif
        top_features = []
        for col in numeric_cols:
            mean_val = interpretation['means'][col]
            overall_mean = original_df[col].mean()
            
            if mean_val > overall_mean * 1.1:
                top_features.append(f"{col} tinggi")
            elif mean_val < overall_mean * 0.9:
                top_features.append(f"{col} rendah")
        
        if top_features:
            interpretation['description'] += f" Karakteristik utama: {', '.join(top_features)}."
        else:
            interpretation['description'] += " Tidak memiliki karakteristik yang menonjol dibandingkan rata-rata."
        
        interpretations[cluster_id] = interpretation
    
    return interpretations