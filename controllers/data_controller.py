import pandas as pd
from typing import Tuple, Dict, Any
from models.data_model import DatasetMetadata, NormalizationResult
from services.preprocessing import (
    detect_numeric_columns, 
    detect_non_numeric_columns, 
    check_missing_values, 
    normalize_minmax,
    convert_to_numpy
)
from utils.file_io import read_csv_file, validate_file_format

class DataController:
    def __init__(self):
        self.dataset_metadata = None
        self.normalization_result = None
    
    def process_uploaded_file(self, file_path: str, filename: str) -> Tuple[DatasetMetadata, NormalizationResult]:
        """Memproses file yang diupload"""
        # Validasi format file
        if not validate_file_format(filename):
            raise ValueError("Format file tidak didukung! Silakan upload file CSV.")
        
        # Baca data
        df = read_csv_file(file_path)
        
        # Deteksi kolom
        numeric_cols = detect_numeric_columns(df)
        non_numeric_cols = detect_non_numeric_columns(df)
        
        # Handle missing values
        df_clean, missing_info = check_missing_values(df)
        
        # Identifikasi kolom untuk merge
        merge_key_column = non_numeric_cols[0] if non_numeric_cols else None
        
        # Buat metadata
        self.dataset_metadata = DatasetMetadata(
            filename=filename,
            columns=df_clean.columns.tolist(),
            numeric_columns=numeric_cols,
            non_numeric_columns=non_numeric_cols,
            row_count=len(df_clean),
            memory_usage_mb=df_clean.memory_usage(deep=True).sum() / 1024 ** 2,
            missing_values_info=missing_info,
            merge_key_column=merge_key_column
        )
        
        # Normalisasi data
        df_norm, norm_params = normalize_minmax(df_clean, numeric_cols)
        scaled_data = convert_to_numpy(df_norm, numeric_cols)
        
        # Simpan hasil normalisasi
        self.normalization_result = NormalizationResult(
            original_data=df_clean,
            normalized_data=df_norm,
            normalization_params=norm_params,
            scaled_data=scaled_data
        )
        
        return self.dataset_metadata, self.normalization_result
    
    def get_data_preview(self, num_rows: int = 5) -> Dict[str, Any]:
        """Mendapatkan preview data"""
        if self.normalization_result is None:
            return {}
            
        return {
            "original_preview": self.normalization_result.original_data.head(num_rows).to_dict(),
            "normalized_preview": self.normalization_result.normalized_data.head(num_rows).to_dict()
        }