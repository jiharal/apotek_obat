"""
Configuration settings for the medicine price extractor app
"""

import os
from dotenv import load_dotenv

load_dotenv()

# App settings
APP_TITLE = "Ekstraksi Harga Obat dari PDF"
APP_DESCRIPTION = "Aplikasi untuk mengekstrak dan membandingkan harga obat dari berbagai PBF"

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["pdf"]
DEFAULT_PBF_FOLDER = "pbf"

# Data processing settings
SIMILARITY_THRESHOLD = 0.8  # Threshold for medicine name matching
CURRENCY_FORMATS = ["Rp", "IDR", "rupiah"]

# Column name mappings for different PBFs
PBF_COLUMN_MAPPINGS = {
    "kimia_farma": {
        "nama": ["NAMA BARANG", "NAMA BRG"],
        "harga": ["HNA+PPN", "HNA + PPN"],
        "stok": ["STOK", "QTY"]
    },
    "enseval": {
        "nama": ["NAMA BRG", "NAMA BARANG"],
        "harga": ["HRG+PPN", "HRG + PPN"],
        "stok": ["QTY", "QUANTITY"]
    },
    "pharos": {
        "nama": ["NAMA OBAT", "NAMA BRG"],
        "harga": ["HARGA JADI", "HARGA"],
        "diskon": ["DISKON", "DISC"]
    },
    "guardian": {
        "nama": ["PRODUK", "NAMA PRODUK"],
        "harga": ["HARGA", "PRICE"],
        "stok": ["STOK TERAKHIR", "STOK"]
    }
}

# Export settings
EXPORT_FORMATS = ["CSV", "Excel"]

# UI settings
ITEMS_PER_PAGE = 50
CHART_HEIGHT = 400