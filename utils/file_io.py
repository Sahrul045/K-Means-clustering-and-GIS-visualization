import pandas as pd
import numpy as np
import os
from typing import Tuple

def validate_file_format(filename: str, allowed_extensions: list = ['.csv']) -> bool:
    """Memvalidasi format file"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def read_csv_file(file_path: str) -> pd.DataFrame:
    """Membaca file CSV dengan error handling"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Gagal membaca file CSV: {e}")

def save_to_csv(df: pd.DataFrame, file_path: str) -> bool:
    """Menyimpan dataframe ke CSV"""
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error menyimpan file: {e}")
        return False