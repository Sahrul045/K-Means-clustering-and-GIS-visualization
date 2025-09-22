import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any  # Import yang digabung
from services.evaluation import evaluate_dbi_range
from models.result_model import FullEvaluationResult, ClusteringResult
from services.clustering import (
    perform_kmeans_clustering,
    add_clusters_to_data,
    analyze_cluster_characteristics,
    prepare_data_for_merge,
    visualize_clusters
)

class ClusterController:
    def __init__(self):
        self.evaluation_result = None
        self.clustering_result = None
        self.df_with_clusters = None
        self.df_norm_with_clusters = None
        self.interpretations = None
        
    def perform_dbi_evaluation(self, scaled_data: np.ndarray, k_min: int = 2, k_max: int = 6) -> FullEvaluationResult:
        """Melakukan evaluasi DBI untuk rentang nilai k"""
        results, best_k, best_dbi = evaluate_dbi_range(scaled_data, k_min, k_max)
        
        # Konversi ke model
        evaluation_results = []
        for result in results:
            evaluation_results.append({
                'k': result['k'],
                'ssw': result['ssw'],
                'ssb': result['ssb'],
                'dbi': result['dbi'],
                'labels': result['labels'],
                'centroids': result['centroids']
            })
        
        self.evaluation_result = FullEvaluationResult(
            evaluation_results=evaluation_results,
            best_k=best_k,
            best_dbi=best_dbi,
            k_min=k_min,
            k_max=k_max
        )
        
        return self.evaluation_result
    
    def get_evaluation_table_data(self):
        """Mendapatkan data untuk tabel evaluasi"""
        if self.evaluation_result is None:
            return []
        
        table_data = []
        for result in self.evaluation_result.evaluation_results:
            table_data.append({
                'k': result.k,
                'ssw': result.ssw,
                'ssb': result.ssb,
                'dbi': result.dbi
            })
        
        return table_data
        
    def perform_kmeans_clustering(
        self,
        scaled_data: np.ndarray,
        original_df: pd.DataFrame,
        normalized_df: pd.DataFrame,
        numeric_cols: list,
        best_k: int,
        merge_key_column: Optional[str] = None
    ) -> ClusteringResult:
        """Melakukan clustering K-Means dengan nilai k terbaik"""
        # Lakukan clustering
        clustering_output = perform_kmeans_clustering(scaled_data, best_k)
        clusters = clustering_output['clusters']
        centroids = clustering_output['centroids']
        
        # Tambahkan cluster ke DataFrame
        df_with_clusters, df_norm_with_clusters = add_clusters_to_data(
            original_df, normalized_df, clusters
        )
        
        # Analisis karakteristik cluster
        cluster_analysis = analyze_cluster_characteristics(
            original_df, numeric_cols, clusters
        )
        
        # Siapkan data untuk merge dengan shapefile
        merge_data = None
        if merge_key_column:
            try:
                merge_data = prepare_data_for_merge(
                    df_with_clusters, clusters, centroids, numeric_cols, merge_key_column
                )
            except ValueError as e:
                print(f"Peringatan: {e}")
        
        # Simpan hasil clustering
        self.clustering_result = ClusteringResult(
            clusters=clusters,
            centroids=centroids,
            cluster_summary=cluster_analysis['cluster_summary'],
            cluster_counts=cluster_analysis['cluster_counts'],
            merge_data=merge_data
        )
        
        # Simpan DataFrame dengan cluster di session state untuk akses mudah
        self.df_with_clusters = df_with_clusters
        self.df_norm_with_clusters = df_norm_with_clusters
        
        return self.clustering_result
    
    def get_clustering_result(self) -> Optional[ClusteringResult]:
        """Mendapatkan hasil clustering"""
        return self.clustering_result
    
    def get_data_with_clusters(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Mendapatkan DataFrame dengan cluster"""
        return self.df_with_clusters, self.df_norm_with_clusters
    
    def create_clustering_table(
        self,
        region_column: str,
        numeric_cols: list
    ) -> Tuple[pd.DataFrame, Dict[int, Dict[str, Any]]]:
        """Membuat tabel hasil clustering lengkap dan interpretasi"""
        from services.clustering import create_clustering_table, interpret_clusters
        
        if (self.df_with_clusters is None or 
            self.df_norm_with_clusters is None or 
            self.clustering_result is None):
            raise ValueError("Clustering belum dilakukan")
        
        # Buat tabel clustering
        clustering_table = create_clustering_table(
            self.df_with_clusters,
            self.df_norm_with_clusters,
            self.clustering_result.clusters,
            self.clustering_result.centroids,
            numeric_cols,
            region_column
        )
        
        # Buat interpretasi cluster
        self.interpretations = interpret_clusters(
            self.df_with_clusters,
            numeric_cols,
            self.clustering_result.clusters
        )
        
        return clustering_table, self.interpretations
    
    def generate_comprehensive_report(self) -> str:
        """Membuat laporan lengkap analisis clustering dalam format markdown"""
        if (self.evaluation_result is None or 
            self.clustering_result is None or 
            self.interpretations is None):
            raise ValueError("Analisis clustering belum lengkap")
        
        # Tambahkan pengecekan tambahan untuk menghindari error
        if not hasattr(self, 'df_with_clusters') or self.df_with_clusters is None:
            raise ValueError("Data dengan cluster belum tersedia")
        
        report_lines = []
        
        # Header
        report_lines.append("# Laporan Analisis Clustering Komprehensif")
        report_lines.append("## Ringkasan Proses Analisis\n")
        
        # Informasi dasar
        report_lines.append("### Informasi Dataset")
        report_lines.append(f"- Jumlah observasi: {len(self.df_with_clusters)}")
        
        # Pastikan centroids ada dan tidak kosong
        if (hasattr(self.clustering_result, 'centroids') and 
            self.clustering_result.centroids is not None and 
            len(self.clustering_result.centroids) > 0):
            
            # Fungsi untuk mendapatkan jumlah fitur dari centroid
            def get_num_features(centroid):
                if hasattr(centroid, 'shape'):  # Jika numpy array
                    return centroid.shape[0]
                elif hasattr(centroid, '__len__'):  # Jika list atau sequence lainnya
                    return len(centroid)
                else:  # Jika scalar
                    return 1
            
            num_features = get_num_features(self.clustering_result.centroids[0])
            report_lines.append(f"- Jumlah variabel numerik: {num_features}")
        else:
            report_lines.append("- Jumlah variabel numerik: Tidak tersedia")
        
        # Fungsi helper untuk mendapatkan nilai scalar dari kemungkinan array
        def get_scalar_value(value):
            if hasattr(value, 'shape') and value.shape:  # Jika numpy array dengan shape
                return value.mean() if value.size > 0 else 0
            elif hasattr(value, '__len__') and not isinstance(value, str):  # Jika sequence bukan string
                return sum(value) / len(value) if len(value) > 0 else 0
            else:  # Jika sudah scalar
                return value
        
        # Hasil DBI
        report_lines.append("\n### Hasil Evaluasi DBI")
        for result in self.evaluation_result.evaluation_results:
            # Pastikan nilai-nilai adalah scalar
            dbi_val = get_scalar_value(result.dbi)
            ssw_val = get_scalar_value(result.ssw)
            ssb_val = get_scalar_value(result.ssb)
            
            report_lines.append(f"- K={result.k}: DBI={dbi_val:.4f}, SSW={ssw_val:.4f}, SSB={ssb_val:.4f}")
        
        # Pastikan best_dbi adalah scalar
        best_dbi = get_scalar_value(self.evaluation_result.best_dbi)
        report_lines.append(f"\n**Cluster optimal**: K={self.evaluation_result.best_k} (DBI={best_dbi:.4f})")
        
        # Hasil Clustering
        report_lines.append("\n### Hasil Clustering")
        for cluster_id in range(self.evaluation_result.best_k):
            count = self.clustering_result.cluster_counts.get(cluster_id, 0)
            report_lines.append(f"- Cluster {cluster_id}: {count} anggota")
        
        # Interpretasi Cluster
        report_lines.append("\n### Interpretasi Cluster")
        for cluster_id, interpretation in self.interpretations.items():
            report_lines.append(f"\n#### Cluster {cluster_id}")
            report_lines.append(f"{interpretation['description']}")
            
            report_lines.append("\n**Karakteristik:**")
            # Gunakan 'means' bukan 'characteristics'
            for var, value in interpretation['means'].items():
                # Pastikan value adalah scalar
                scalar_value = get_scalar_value(value)
                report_lines.append(f"- {var}: {scalar_value:.4f}")
            
            # Gunakan get dengan default value untuk menghindari KeyError
            recommendation = interpretation.get('recommendation', 'Tidak ada rekomendasi spesifik')
            report_lines.append(f"\n**Rekomendasi:** {recommendation}")
        
        # Kesimpulan
        report_lines.append("\n### Kesimpulan Umum")
        dominant_cluster = max(self.clustering_result.cluster_counts, key=self.clustering_result.cluster_counts.get)
        report_lines.append(f"- Cluster {dominant_cluster} memiliki anggota terbanyak ({self.clustering_result.cluster_counts[dominant_cluster]} wilayah)")
        
        # Analisis kualitas clustering berdasarkan DBI
        if best_dbi < 0.5:
            report_lines.append("- Kualitas clustering sangat baik (DBI < 0.5)")
        elif best_dbi < 1.0:
            report_lines.append("- Kualitas clustering baik (0.5 ≤ DBI < 1.0)")
        elif best_dbi < 2.0:
            report_lines.append("- Kualitas clustering cukup (1.0 ≤ DBI < 2.0)")
        else:
            report_lines.append("- Kualitas clustering kurang optimal (DBI ≥ 2.0)")
        
        # Footer
        report_lines.append("\n---")
        report_lines.append("*Laporan ini dihasilkan secara otomatis oleh Clustering Analysis App*")
        
        # Konversi ke string
        return "\n".join(report_lines)