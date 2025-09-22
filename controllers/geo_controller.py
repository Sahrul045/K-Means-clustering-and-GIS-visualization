import geopandas as gpd
import streamlit as st
import tempfile
import zipfile
import folium
import os
import shutil
from config import SHAPEFILE_PATH, SHAPEFILE_KEY_COLUMN, SHAPEFILE_ZIP_PATH, SHAPEFILE_DIR
from services.geoprocessing import GeoProcessingService
from services.map_visualization import MapVisualizationService

class GeoController:
    def __init__(self):
        self.shapefile = None
        self.geo_processor = GeoProcessingService()
        self.map_visualizer = MapVisualizationService()
        self.extract_dir = None

    def load_default_shapefile(self):
        """Memuat shapefile default dari zip"""
        try:
            # Periksa apakah file zip ada di lokasi yang benar
            if not os.path.exists(SHAPEFILE_ZIP_PATH):
                st.error(f"File shapefile default tidak ditemukan di: {SHAPEFILE_ZIP_PATH}")
                st.info("""
                Silakan lakukan salah satu dari berikut:
                1. Pastikan file 'sultra_kabupaten_shapefile.zip' ada di direktori 'data/shapefiles/'
                2. Atau unggah shapefile custom menggunakan opsi 'Custom'
                """)
                return False

            # Ekstrak zip default ke temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                with zipfile.ZipFile(SHAPEFILE_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Baca shapefile yang diekstrak
                shp_files = [f for f in os.listdir(tmp_dir) if f.endswith('.shp')]
                if shp_files:
                    self.shapefile = gpd.read_file(os.path.join(tmp_dir, shp_files[0]))
                    st.success("Shapefile default berhasil diekstrak dan dimuat.")
                    return True
                else:
                    st.error("Tidak ada file .shp dalam zip shapefile default.")
                    return False
        except Exception as e:
            st.error(f"Gagal memuat shapefile default: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return False

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
                raise Exception("Shapefile belum dimuat. Silakan pilih opsi shapefile terlebih dahulu.")
            
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
        """
        try:
            # Pastikan kolom Cluster ada dalam data
            if 'Cluster' not in merged_data.columns:
                raise ValueError("Kolom 'Cluster' tidak ditemukan dalam data yang digabung")
            
            # Pastikan data memiliki geometri
            if not hasattr(merged_data, 'geometry') or merged_data.geometry.isnull().all():
                raise ValueError("Data tidak memiliki geometri yang valid")
            
            # Buat peta
            choropleth_map = self.map_visualizer.create_choropleth_map(merged_data, numeric_cols, best_k)
            
            # Pastikan peta berhasil dibuat
            if choropleth_map is None:
                raise ValueError("Map visualizer gagal membuat peta")
                
            return choropleth_map
                
        except Exception as e:
            st.error(f"Error generating choropleth map: {str(e)}")
            import traceback
            print(f"Error detail: {traceback.format_exc()}")
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
            shutil.rmtree(self.extract_dir)
            self.extract_dir = None