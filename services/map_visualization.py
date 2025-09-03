import streamlit as st
import folium
from folium.plugins import MarkerCluster
import numpy as np
from config import MAP_CENTER, MAP_ZOOM

class MapVisualizationService:
    def __init__(self):
        self.cluster_colormap = {
            0: 'red',
            1: 'blue',
            2: 'green',
            3: 'purple',
            4: 'orange',
            5: 'darkred',
            6: 'lightblue'
        }
    
    def create_choropleth_map(self, gdf_merged, numeric_cols, best_k):
        """Membuat peta choropleth untuk visualisasi cluster"""
        try:
            # Pastikan gdf_merged adalah GeoDataFrame yang valid
            if gdf_merged is None or gdf_merged.empty:
                return self._create_fallback_map("Data geospatial tidak valid atau kosong")
            
            # Pastikan kolom 'Cluster' ada
            if 'Cluster' not in gdf_merged.columns:
                return self._create_fallback_map("Kolom 'Cluster' tidak ditemukan dalam data geospatial")
            
            # Hitung bounds untuk fokus pada wilayah yang relevan
            minx, miny, maxx, maxy = gdf_merged.total_bounds
            
            # Buat peta dasar
            m = folium.Map(
                location=[(miny + maxy) / 2, (minx + maxx) / 2],
                zoom_start=MAP_ZOOM,
                tiles='CartoDB positron',
                width='100%',
                height='500px'
            )
            
            # Batasi tampilan peta
            m.fit_bounds([[miny, minx], [maxy, maxx]])
            
            # Tambahkan CSS custom
            m.get_root().html.add_child(folium.Element("""
            <style>
                .folium-map {
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .html-container {
                    width: 100% !important;
                    padding: 0 !important;
                }
            </style>
            """))
            
            # Style function untuk pewarnaan berdasarkan cluster
            def style_function(feature):
                cluster = feature['properties']['Cluster']
                if cluster is None or np.isnan(cluster):
                    return {'fillColor': 'gray', 'color': 'black', 'weight': 1, 'fillOpacity': 0.3}
                else:
                    return {
                        'fillColor': self.cluster_colormap.get(int(cluster), 'gray'),
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    }
            
            # Highlight function
            def highlight_function(feature):
                return {
                    'fillColor': '#ffff00',
                    'color': '#ffff00',
                    'weight': 3,
                    'fillOpacity': 0.7
                }
            
            # Buat GeoJson layer
            folium.GeoJson(
                gdf_merged,
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.GeoJsonTooltip(
                    fields=['KAB_KOTA', 'Cluster'],
                    aliases=['Kabupaten/Kota: ', 'Cluster: '],
                    localize=True
                ),
                popup=folium.GeoJsonPopup(
                    fields=['KAB_KOTA', 'Cluster'] + [f'Centroid_{col}' for col in numeric_cols],
                    aliases=['Kabupaten/Kota: ', 'Cluster: '] + [f'{col}: ' for col in numeric_cols],
                    localize=True
                ),
                name='Clustering Results'
            ).add_to(m)
            
            # Tambahkan label untuk setiap kabupaten/kota
            for idx, row in gdf_merged.iterrows():
                if row['geometry'] is not None:
                    centroid = row['geometry'].centroid
                    folium.Marker(
                        location=[centroid.y, centroid.x],
                        icon=folium.DivIcon(
                            html=f'<div style="font-size: 9px; font-weight: bold; color: black; text-shadow: -1px -1px 0 white, 1px -1px 0 white, -1px 1px 0 white, 1px 1px 0 white;">{row["KAB_KOTA"]}</div>'
                        )
                    ).add_to(m)
            
            # Tambahkan legenda
            self._add_legend(m, best_k)
            
            return m
            
        except Exception as e:
            st.error(f"Error creating choropleth map: {str(e)}")
            return self._create_fallback_map(f"Error: {str(e)}")
    
    def _create_fallback_map(self, message="Terjadi kesalahan"):
        """Membuat peta fallback jika terjadi error"""
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM)
        # Tambahkan pesan error ke peta
        m.get_root().html.add_child(folium.Element(
            f'<div style="position: fixed; top: 10px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 1px solid gray;">{message}</div>'
        ))
        return m
    
    def _add_legend(self, map_object, best_k):
        """Menambahkan legenda ke peta"""
        legend_html = '''
        <div style="position: fixed;
            bottom: 20px; left: 20px; width: 160px; height: auto;
            background-color: white; border:1px solid grey; z-index:9999;
            font-size:12px; padding: 8px; border-radius: 5px;">
            <b style="font-size: 13px;">Keterangan Cluster</b><br>
        '''
        
        for cluster_id in range(best_k):
            legend_html += f'''
            <div style="margin: 2px 0;">
                <i style="background: {self.cluster_colormap.get(cluster_id, 'gray')};
                    width: 15px; height: 15px; display: inline-block; margin-right: 5px; border: 1px solid #000;"></i>
                <span>Cluster {cluster_id}</span>
            </div>
            '''
        
        legend_html += '''
        <div style="margin: 2px 0;">
            <i style="background: gray; width: 15px; height: 15px; display: inline-block; margin-right: 5px; border: 1px solid #000;"></i>
            <span>Tidak ada data</span>
        </div>
        </div>
        '''
        
        map_object.get_root().html.add_child(folium.Element(legend_html))