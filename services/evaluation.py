import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score
from typing import List, Tuple, Dict, Any

def calculate_dbi_for_k(scaled_data: np.ndarray, k: int, random_state: int = 42) -> Dict[str, Any]:
    """Menghitung DBI dan metrik lainnya untuk nilai k tertentu"""
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(scaled_data)
    centroids = kmeans.cluster_centers_
    
    ssw = kmeans.inertia_
    overall_mean = np.mean(scaled_data, axis=0)
    
    # Hitung SSB
    ssb = 0
    for i in range(k):
        cluster_points = scaled_data[labels == i]
        ni = len(cluster_points)
        ssb += ni * np.sum((centroids[i] - overall_mean) ** 2)
    
    # Hitung DBI
    dbi = davies_bouldin_score(scaled_data, labels)
    
    return {
        'k': k,
        'ssw': ssw,
        'ssb': ssb,
        'dbi': dbi,
        'labels': labels,
        'centroids': centroids
    }

def evaluate_dbi_range(scaled_data: np.ndarray, k_min: int = 2, k_max: int = 6) -> Tuple[List[Dict[str, Any]], int, float]:
    """Evaluasi DBI untuk rentang nilai k"""
    results = []
    dbis = []
    
    for k in range(k_min, k_max + 1):
        result = calculate_dbi_for_k(scaled_data, k)
        results.append(result)
        dbis.append(result['dbi'])
    
    # Temukan k terbaik (DBI terkecil)
    best_idx = np.argmin(dbis)
    best_k = results[best_idx]['k']
    best_dbi = results[best_idx]['dbi']
    
    return results, best_k, best_dbi