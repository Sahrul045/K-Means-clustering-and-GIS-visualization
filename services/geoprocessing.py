import geopandas as gpd
import zipfile
import os
import tempfile
import numpy as np
from config import SHAPEFILE_DIR

class GeoProcessingService:
    def __init__(self):
        self.shapefile_path = None
        # Gunakan nilai dari config, bukan hardcode
        from config import SHAPEFILE_KEY_COLUMN
        self.name_column = SHAPEFILE_KEY_COLUMN  # Sekarang akan menggunakan 'KAB_KOTA'
    
    def extract_shapefile_zip(self, uploaded_zip):
        """Mengekstrak file shapefile zip yang diupload"""
        try:
            # Simpan file zip sementara
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
                tmp_zip.write(uploaded_zip.getvalue())
                tmp_zip_path = tmp_zip.name
            
            # Buat direktori untuk ekstraksi
            extract_dir = os.path.join(SHAPEFILE_DIR, "temp_extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            # Ekstrak file zip
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Cari file .shp
            shp_file = None
            for file in os.listdir(extract_dir):
                if file.endswith(".shp"):
                    shp_file = os.path.join(extract_dir, file)
                    break
            
            if not shp_file:
                raise ValueError("File .shp tidak ditemukan dalam arsip zip")
            
            # Baca shapefile
            gdf = gpd.read_file(shp_file)
            
            # Bersihkan file sementara
            os.unlink(tmp_zip_path)
            
            return gdf, extract_dir
            
        except Exception as e:
            # Bersihkan file sementara jika ada error
            if 'tmp_zip_path' in locals() and os.path.exists(tmp_zip_path):
                os.unlink(tmp_zip_path)
            raise Exception(f"Gagal mengekstrak shapefile: {str(e)}")
    
    def standardize_region_names(self, data, merge_key_column):
        """Standarisasi nama wilayah untuk memastikan match dengan shapefile"""
        name_mapping = {
            'KOTA BAUBAU': 'KOTA BAU BAU',
            # Tambahkan mapping lainnya jika diperlukan
        }
        
        data_standardized = data.copy()
        data_standardized[merge_key_column] = data_standardized[merge_key_column].str.upper()
        
        for old_name, new_name in name_mapping.items():
            data_standardized[merge_key_column] = data_standardized[merge_key_column].str.replace(old_name, new_name)
        
        return data_standardized
    
    def merge_with_shapefile(self, gdf, clustering_data, merge_key_column, numeric_cols):
        """Menggabungkan data clustering dengan shapefile"""
        # Standardisasi nama wilayah
        clustering_data_std = self.standardize_region_names(clustering_data, merge_key_column)
        
        # Pastikan kolom KAB_KOTA ada di shapefile
        if self.name_column not in gdf.columns:
            raise ValueError(f"Kolom {self.name_column} tidak ditemukan dalam shapefile")
        
        # Pastikan kolom Cluster ada di data clustering
        if 'Cluster' not in clustering_data_std.columns:
            raise ValueError("Kolom 'Cluster' tidak ditemukan dalam data clustering")
        
        # Merge shapefile dengan data clustering
        gdf_merged = gdf.merge(
            clustering_data_std,
            left_on=self.name_column,
            right_on=merge_key_column,
            how='left'
        )
        
        # Cek hasil merge
        missing_in_shapefile = clustering_data_std[~clustering_data_std[merge_key_column].isin(gdf[self.name_column])]
        missing_in_data = gdf[~gdf[self.name_column].isin(clustering_data_std[merge_key_column])]
        
        merge_report = {
            'merged_gdf': gdf_merged,
            'missing_in_shapefile': missing_in_shapefile,
            'missing_in_data': missing_in_data,
            'total_matched': len(gdf_merged[gdf_merged['Cluster'].notna()])
        }
        
        return merge_report