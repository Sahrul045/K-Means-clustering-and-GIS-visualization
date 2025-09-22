import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

def detect_numeric_columns(df: pd.DataFrame) -> list:
    """Mendeteksi kolom numerik dalam dataframe"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def detect_potential_numeric_columns(df: pd.DataFrame) -> list:
    """
    Mendeteksi kolom yang seharusnya numerik tetapi mungkin mengandung teks
    dengan mencoba mengonversi ke numerik dan melihat persentase keberhasilan
    """
    potential_numeric_cols = []
    
    for col in df.columns:
        # Skip kolom yang sudah numerik
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
            
        # Coba konversi ke numerik
        numeric_series = pd.to_numeric(df[col], errors='coerce')
        
        # Hitung persentase nilai yang berhasil dikonversi
        success_rate = numeric_series.notna().mean()
        
        # Jika lebih dari 50% nilai berhasil dikonversi, anggap sebagai kolom numerik
        if success_rate > 0.5:
            potential_numeric_cols.append(col)
    
    return potential_numeric_cols

def detect_non_numeric_columns(df: pd.DataFrame) -> list:
    """Mendeteksi kolom non-numerik dalam dataframe"""
    return df.select_dtypes(exclude=[np.number]).columns.tolist()

def validate_numeric_columns(df: pd.DataFrame, numeric_cols: list) -> Tuple[bool, Dict[str, List[int]]]:
    """
    Memvalidasi bahwa kolom numerik hanya berisi nilai numerik
    Mengembalikan status valid dan daftar baris dengan nilai non-numerik per kolom
    """
    errors = {}
    is_valid = True
    
    for col in numeric_cols:
        # Coba konversi ke numerik, non-numerik akan menjadi NaN
        numeric_series = pd.to_numeric(df[col], errors='coerce')
        
        # Temukan baris dengan NaN yang bukan originally NaN
        non_numeric_mask = numeric_series.isna() & df[col].notna()
        
        if non_numeric_mask.any():
            is_valid = False
            error_rows = non_numeric_mask[non_numeric_mask].index.tolist()
            errors[col] = error_rows
    
    return is_valid, errors

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
        # Pastikan kolom numerik
        df_norm[col] = pd.to_numeric(df_norm[col], errors='coerce')
        
        col_min = df_norm[col].min()
        col_max = df_norm[col].max()
        normalization_params[col] = {"min": col_min, "max": col_max}

        if col_max == col_min:
            df_norm[col] = 0  # Handle kolom konstan
        else:
            df_norm[col] = (df_norm[col] - col_min) / (col_max - col_min)
            
    return df_norm, normalization_params

def convert_to_numpy(df_norm: pd.DataFrame, numeric_cols: list) -> np.ndarray:
    """Mengkonversi dataframe ke array numpy untuk clustering"""
    return df_norm[numeric_cols].values