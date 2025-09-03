import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DBIEvaluationResult(BaseModel):
    """Hasil evaluasi DBI untuk satu nilai k"""
    k: int
    ssw: float
    ssb: float
    dbi: float
    labels: Any  # numpy array
    centroids: Any  # numpy array
    
    class Config:
        arbitrary_types_allowed = True

class FullEvaluationResult(BaseModel):
    """Hasil evaluasi DBI untuk semua nilai k"""
    evaluation_results: List[DBIEvaluationResult]
    best_k: int
    best_dbi: float
    k_min: int
    k_max: int
    
class ClusteringResult(BaseModel):
    """Hasil clustering K-Means"""
    clusters: Any  # numpy array
    centroids: Any  # numpy array
    cluster_summary: pd.DataFrame
    cluster_counts: Dict[int, int]   # ✅ ubah jadi int
    merge_data: Optional[pd.DataFrame] = None
    
    class Config:
        arbitrary_types_allowed = True