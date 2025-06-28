# Medicine Price Extractor

Aplikasi web untuk mengekstrak dan membandingkan harga obat dari file PDF berbagai PBF (Pedagang Besar Farmasi).

## Fitur Utama

- 📁 Upload multiple file PDF sekaligus
- 🔍 Ekstraksi otomatis data obat (nama, harga, PBF) dari PDF
- 💰 Perbandingan harga antar PBF
- 📊 Visualisasi data dengan grafik interaktif
- 💾 Export hasil ke CSV dan Excel
- 🔍 Pencarian dan filter obat
- 📈 Analitik penghematan dan performa PBF

## Instalasi

1. Clone atau download repository ini
2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

## Cara Penggunaan

1. **Upload File PDF**: Di sidebar, klik "Browse files" dan pilih satu atau beberapa file PDF yang berisi daftar harga obat dari PBF.

2. **Atur Pengaturan**: Sesuaikan threshold kesamaan nama obat (default 0.8) untuk mengenali obat yang sama dengan nama sedikit berbeda.

3. **Proses File**: Klik tombol "🚀 Proses File" untuk memulai ekstraksi data.

4. **Lihat Hasil**: Setelah pemrosesan selesai, hasil akan ditampilkan dalam 4 tab:
   - **Perbandingan Harga**: Tabel perbandingan dengan harga terbaik
   - **Analitik**: Grafik distribusi harga dan analisis penghematan
   - **Data Lengkap**: Semua data yang diekstrak dengan filter
   - **Export**: Download hasil dalam format CSV/Excel

## Format PDF yang Didukung

Aplikasi ini mendukung berbagai format PDF:
- PDF dengan tabel terstruktur
- PDF dengan text yang dapat di-copy
- PDF scan (dengan OCR terbatas)

## Folder PBF Default

Secara default, aplikasi menyediakan folder `pbf/` untuk menyimpan file PDF daftar harga:

```
pbf/
├── pbf_kimia_farma/
├── enseval/
├── pharos/
├── guardian/
└── [pbf_lainnya]/
```

## Kolom yang Dikenali

### Nama Obat/Barang:
- **NAMA BRG** (umum di Enseval)
- **NAMA BARANG** (umum di Kimia Farma)
- **NAMA OBAT** (umum di Pharos)
- **PRODUK** (umum di Guardian)

### Harga:
- **HNA+PPN** (Kimia Farma)
- **HRG+PPN** (Enseval)
- **HARGA JADI** (Pharos)
- **HARGA** (Guardian)

### Stok:
- **STOK TERAKHIR**
- **STOK**
- **QTY**
- **QUANTITY**

### Diskon:
- **DISKON**
- **DISCOUNT**
- **DISC**

## Struktur Data

Data yang diekstrak mengandung informasi:
- Nama obat
- Stok terakhir
- Diskon (%)
- Harga
- PBF (nama file)
- Halaman dalam PDF

## Troubleshooting

### PDF tidak terbaca
- Pastikan PDF tidak terproteksi password
- Coba convert PDF ke format yang lebih standar
- Untuk PDF scan, pastikan kualitas scan cukup baik

### Data tidak terdeteksi
- Periksa apakah PDF mengandung tabel dengan format yang jelas
- Pastikan ada indikator obat (tablet, kapsul, mg, ml, dll.)
- Sesuaikan threshold kesamaan nama

### Error saat processing
- Periksa ukuran file (maksimal 10MB per file)
- Pastikan format file benar-benar PDF
- Restart aplikasi jika perlu

## Dependencies

- streamlit: Framework web app
- pandas: Data processing
- PyPDF2: PDF reader
- pdfplumber: PDF table extraction
- tabula-py: Alternative PDF table extraction
- plotly: Interactive charts
- openpyxl: Excel export

## Kontribusi

Silakan buat issue atau pull request untuk perbaikan dan penambahan fitur.

## Lisensi

MIT License