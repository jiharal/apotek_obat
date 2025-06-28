# Instruksi Claude Code: Webapp Ekstraksi Harga Obat dari PDF

## Deskripsi Proyek

Buat webapp menggunakan Streamlit untuk mengekstrak data harga obat dari file PDF dan menentukan harga terbaik dari beberapa PBF (Pedagang Besar Farmasi).

## Fitur Utama yang Diminta

1. **Upload Multiple PDF**: Kemampuan upload beberapa file PDF sekaligus
2. **Ekstraksi Data**: Extract informasi obat (nama, harga, PBF) dari PDF
3. **Perbandingan Harga**: Analisis dan tampilkan harga terbaik untuk setiap obat
4. **Export Data**: Kemampuan export hasil ke CSV/Excel
5. **Filter & Search**: Fitur pencarian dan filter obat

## Struktur Aplikasi

```
medicine_price_extractor/
├── app.py                 # Main Streamlit app
├── utils/
│   ├── pdf_extractor.py   # PDF processing functions
│   ├── data_processor.py  # Data cleaning & analysis
│   └── visualizer.py      # Charts & visualization
├── requirements.txt       # Dependencies
├── config.py             # Configuration settings
└── README.md             # Documentation
```

## Dependencies yang Dibutuhkan

```txt
streamlit>=1.28.0
pandas>=2.0.0
PyPDF2>=3.0.0
pdfplumber>=0.9.0
tabula-py>=2.7.0
openpyxl>=3.1.0
plotly>=5.15.0
python-dotenv>=1.0.0
```

## Komponen Utama

### 1. PDF Extractor (utils/pdf_extractor.py)

- Fungsi untuk membaca berbagai format PDF
- Support untuk PDF yang berisi tabel
- Handling untuk PDF dengan layout yang berbeda-beda
- Ekstraksi metadata (nama, satuan, stok, harga)

### 2. Data Processor (utils/data_processor.py)

- Cleaning dan standardisasi nama obat
- Normalisasi format harga
- Matching obat yang sama dari PBF berbeda
- Algoritma untuk menentukan harga terbaik

### 3. Main App (app.py)

Interface Streamlit dengan:

- **Sidebar**: Upload files, filter options
- **Main Area**: Results table, comparison charts
- **Tabs**:
  - Upload & Process
  - Price Comparison
  - Data Export
  - Analytics Dashboard

## Fitur Khusus

1. **Smart Matching**: Algoritma untuk mengenali obat yang sama meski nama sedikit berbeda
2. **Price Analytics**: Grafik perbandingan harga, trend analysis
3. **Batch Processing**: Proses multiple PDF sekaligus
4. **Data Validation**: Validasi format harga dan nama obat
5. **Export Options**: CSV, Excel, PDF report

## UI/UX Requirements

- Interface bahasa Indonesia
- Responsive design
- Progress indicators untuk processing
- Error handling yang user-friendly
- Clear data visualization dengan Plotly

## Testing Requirements

- Test dengan berbagai format PDF
- Validasi akurasi ekstraksi data
- Performance test dengan file besar
- Error handling untuk PDF corrupt/tidak readable

## Task Breakdown

Step 1: Baca dan Analisis PDF

Gunakan pdfplumber atau tabula-py untuk membaca PDF
PENTING: Identifikasi dua area tabel yang berdampingan pada setiap halaman
Definisikan koordinat/bbox untuk tabel kiri dan tabel kanan secara terpisah
Ekstrak kedua tabel secara independen untuk menghindari data tercampur

Step 2: Data Processing

Ekstrak tabel kiri dan kanan secara terpisah
Gabungkan data dari kedua tabel ke dalam satu dataset
Clean data yang terekstrak (hapus karakter tidak perlu)
Pisahkan kolom dengan benar untuk setiap tabel
Handle format angka (convert string ke numeric)
Standardisasi nama kolom
Pastikan tidak ada duplikasi antara data tabel kiri dan kanan

## Deployment

- Siapkan untuk deploy ke Streamlit Cloud
- Include sample PDF files untuk testing
- Documentation lengkap di README.md

## Instruksi Spesifik untuk Claude Code

**Mulai dengan:**

```bash
# Buat project baru
mkdir medicine_price_extractor
cd medicine_price_extractor

# Inisialisasi virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau venv\Scripts\activate  # Windows

# Install dependencies dasar
pip install streamlit pandas PyPDF2 pdfplumber
```

**Prioritas Development:**

1. Buat basic Streamlit app dengan file upload
2. Implement PDF extraction untuk satu file
3. Tambahkan data processing dan cleaning
4. Buat comparison logic
5. Tambahkan visualization
6. Implement batch processing
7. Add export functionality
8. Polish UI/UX

**Struktur Data yang Diharapkan:**

```python
{
    'nama_obat': str,
    'satuan': str,
    'stok_akhir': str,
    'diskon': float,
    'harga': float,
}
```

**Informasi kolom di beberapa pbf**

- Nama Obat: NAMA BRG, NAMA BARANG
- Harga: HNA+PPN, HRG+PPN, HARGA JADI

**Error Handling:**

- PDF tidak bisa dibaca
- Format harga tidak valid
- Nama obat tidak terdeteksi
- File kosong atau corrupt

Fokus pada akurasi ekstraksi data dan kemudahan penggunaan. Buat interface yang intuitif untuk pengguna farmasi/apotek.
