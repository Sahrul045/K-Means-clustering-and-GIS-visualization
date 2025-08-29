from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd

class DatasetMetadata(BaseModel):
    """Metadata untuk dataset"""
    filename: str
    columns: List[str]
    numeric_columns: List[str]
    non_numeric_columns: List[str]
    row_count: int
    memory_usage_mb: float
    missing_values_info: Dict[str, Any]
    merge_key_column: Optional[str] = None

class NormalizationResult(BaseModel):
    """Hasil normalisasi data"""
    original_data: pd.DataFrame
    normalized_data: pd.DataFrame
    normalization_params: Dict[str, Any]
    scaled_data: Any  # numpy array
    
    class Config:
        arbitrary_types_allowed = True