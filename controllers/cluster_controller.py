import pandas as pd
import numpy as np
from typing import Tuple, Optional
from services.evaluation import evaluate_dbi_range
from models.result_model import FullEvaluationResult
from typing import Tuple, Dict, Any # ditambahkan setelah cell code 4 masuk
from services.clustering import (
    perform_kmeans_clustering,
    add_clusters_to_data,
    analyze_cluster_characteristics,
    prepare_data_for_merge,
    visualize_clusters
)
from models.result_model import ClusteringResult

class ClusterController:
    def __init__(self):
        self.evaluation_result = None
        self.clustering_result = None
        self.df_with_clusters = None
        self.df_norm_with_clusters = None
        
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
    
    # update cell code 4
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
        interpretations = interpret_clusters(
            self.df_with_clusters,
            numeric_cols,
            self.clustering_result.clusters
        )
        
        return clustering_table, interpretations