import geopandas as gpd
import mapclassify
import streamlit as st
import tempfile
import zipfile
import os
import numpy as np
from config import SHAPEFILE_PATH, SHAPEFILE_KEY_COLUMN
from services.geoprocessing import GeoProcessingService
from services.map_visualization import MapVisualizationService

class GeoController:
    def __init__(self):
        self.shapefile = None
        self.geo_processor = GeoProcessingService()
        self.map_visualizer = MapVisualizationService()
        self.extract_dir = None
        self.load_shapefile()
    
    def load_shapefile(self):
        """Memuat shapefile default untuk Sulawesi Tenggara"""
        try:
            if os.path.exists(SHAPEFILE_PATH):
                self.shapefile = gpd.read_file(SHAPEFILE_PATH)
            else:
                self.shapefile = None
        except Exception as e:
            print(f"Peringatan: Gagal memuat shapefile default: {str(e)}")
            self.shapefile = None
    
    def process_uploaded_shapefile(self, uploaded_zip):
        """Memproses shapefile zip yang diupload"""
        try:
            # Ekstrak dan baca shapefile
            gdf, extract_dir = self.geo_processor.extract_shapefile_zip(uploaded_zip)
            self.shapefile = gdf
            self.extract_dir = extract_dir
            return gdf, extract_dir
        except Exception as e:
            raise Exception(f"Gagal memproses shapefile: {str(e)}")
    
    def merge_with_geodata(self, clustering_data, merge_column, numeric_cols):
        """
        Menggabungkan data clustering dengan data geospatial
        
        Args:
            clustering_data (pd.DataFrame): Data hasil clustering
            merge_column (str): Nama kolom yang digunakan untuk merge
            numeric_cols (list): Daftar kolom numerik
        
        Returns:
            dict: Hasil merge dengan laporan
        """
        try:
            # Pastikan shapefile sudah dimuat
            if self.shapefile is None:
                raise Exception("Shapefile belum dimuat. Silakan upload shapefile terlebih dahulu.")
            
            # Pastikan data clustering memiliki kolom Cluster
            if 'Cluster' not in clustering_data.columns:
                raise Exception("Data clustering tidak memiliki kolom 'Cluster'. Pastikan clustering telah dilakukan dengan benar.")
            
            # Merge data clustering dengan shapefile
            merge_report = self.geo_processor.merge_with_shapefile(
                self.shapefile, 
                clustering_data, 
                merge_column,
                numeric_cols
            )
            
            return merge_report
        except Exception as e:
            raise Exception(f"Gagal menggabungkan data dengan geodata: {str(e)}")
    
    def generate_choropleth_map(self, merged_data, numeric_cols, best_k):
        """
        Menghasilkan peta choropleth untuk visualisasi cluster
        
        Args:
            merged_data (geopandas.GeoDataFrame): Data yang sudah digabung dengan geodata
            numeric_cols (list): Daftar kolom numerik
            best_k (int): Jumlah cluster terbaik
        
        Returns:
            folium.Map: Peta choropleth
        """
        try:
            # Pastikan kolom Cluster ada dalam data
            if 'Cluster' not in merged_data.columns:
                raise ValueError("Kolom 'Cluster' tidak ditemukan dalam data yang digabung")
            
            return self.map_visualizer.create_choropleth_map(merged_data, numeric_cols, best_k)
        except Exception as e:
            # Jika terjadi error, kembalikan peta dasar
            st.error(f"Error generating choropleth map: {str(e)}")
            import folium
            from config import MAP_CENTER, MAP_ZOOM
            return folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM)
    
    def save_geodata(self, gdf, output_path):
        """Menyimpan data geospatial ke file"""
        try:
            gdf.to_file(output_path, encoding='utf-8')
            return True
        except Exception as e:
            raise Exception(f"Gagal menyimpan data geospatial: {str(e)}")
    
    def cleanup_temp_files(self):
        """Membersihkan file temporer"""
        if self.extract_dir and os.path.exists(self.extract_dir):
            import shutil
            shutil.rmtree(self.extract_dir)
            self.extract_dir = None