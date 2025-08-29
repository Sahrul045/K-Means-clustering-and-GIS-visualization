import os

# Path konfigurasi
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