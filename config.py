import os

# Path konfigurasi - HAPUS DUPLIKASI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "input")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
SHAPEFILE_DIR = os.path.join(DATA_DIR, "shapefiles")

# Buat direktori jika belum ada
for directory in [DATA_DIR, UPLOAD_DIR, PROCESSED_DIR, SHAPEFILE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Konstanta aplikasi
ALLOWED_FILE_EXTENSIONS = ['.csv']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Warna untuk styling cluster (cell code 4)
CLUSTER_COLORS = {
    0: '#FFCCCC',  # Merah muda
    1: '#CCFFCC',  # Hijau muda
    2: '#CCCCFF',  # Biru muda
    3: '#FFFFCC',  # Kuning muda
    4: '#FFCCFF',  # Ungu muda
    5: '#CCFFFF',  # Cyan muda
    6: '#FFE5CC',  # Oranye muda
}

# Konfigurasi Shapefile dan Peta - HAPUS DUPLIKASI
SHAPEFILE_PATH = os.path.join(SHAPEFILE_DIR, "sultra.shp")
# SESUAIKAN DENGAN geoprocessing.py - ubah ke 'KAB_KOTA'
SHAPEFILE_KEY_COLUMN = "KAB_KOTA"  # Diubah dari "KABKOTA" menjadi "KAB_KOTA"

# Map configuration
MAP_CENTER = [-4.0, 122.0]  # Koordinat tengah peta Sulawesi Tenggara
MAP_ZOOM = 7