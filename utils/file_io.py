import pandas as pd
import numpy as np
import os
import zipfile
import tempfile
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

def extract_zip_file(zip_path: str, extract_to: str) -> bool:
    """Mengekstrak file ZIP ke direktori tertentu"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return False

def create_temp_dir() -> str:
    """Membuat direktori temporer dan mengembalikan path-nya"""
    return tempfile.mkdtemp()

def cleanup_temp_dir(dir_path: str):
    """Membersihkan direktori temporer"""
    import shutil
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)