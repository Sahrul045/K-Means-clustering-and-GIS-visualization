# cell code 4
def get_cluster_color(cluster_id: int) -> str:
    """Mendapatkan warna untuk cluster tertentu"""
    from config import CLUSTER_COLORS
    return CLUSTER_COLORS.get(cluster_id % len(CLUSTER_COLORS), '#CCCCCC')