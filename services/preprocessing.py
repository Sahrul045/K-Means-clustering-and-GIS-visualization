import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def detect_numeric_columns(df: pd.DataFrame) -> list:
    """Mendeteksi kolom numerik dalam dataframe"""
    return df.select_dtypes(include=np.number).columns.tolist()

def detect_non_numeric_columns(df: pd.DataFrame) -> list:
    """Mendeteksi kolom non-numerik dalam dataframe"""
    return df.select_dtypes(exclude=[np.number]).columns.tolist()

def check_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Memeriksa dan menangani missing values"""
    missing_values = df.isnull().sum()
    missing_info = {}
    
    if missing_values.any():
        missing_info["has_missing"] = True
        missing_info["missing_counts"] = missing_values[missing_values > 0].to_dict()
        
        # Hapus baris dengan missing values
        df_clean = df.dropna()
        rows_dropped = len(df) - len(df_clean)
        missing_info["rows_dropped"] = rows_dropped
        
        if len(df_clean) == 0:
            raise ValueError("ERROR: Semua data mengandung missing values! Tidak dapat melanjutkan.")
            
        df = df_clean
        missing_info["new_row_count"] = len(df)
    else:
        missing_info["has_missing"] = False
        
    return df, missing_info

def normalize_minmax(df: pd.DataFrame, numeric_cols: list) -> Tuple[pd.DataFrame, dict]:
    """Melakukan normalisasi Min-Max pada kolom numerik"""
    df_norm = df.copy()
    normalization_params = {}
    
    for col in numeric_cols:
        col_min = df[col].min()
        col_max = df[col].max()
        normalization_params[col] = {"min": col_min, "max": col_max}

        if col_max == col_min:
            df_norm[col] = 0  # Handle kolom konstan
        else:
            df_norm[col] = (df[col] - col_min) / (col_max - col_min)
            
    return df_norm, normalization_params

def convert_to_numpy(df_norm: pd.DataFrame, numeric_cols: list) -> np.ndarray:
    """Mengkonversi dataframe ke array numpy untuk clustering"""
    return df_norm[numeric_cols].values