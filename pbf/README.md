# Folder PBF - Daftar Harga

Folder ini digunakan untuk menyimpan file PDF daftar harga dari berbagai PBF (Pedagang Besar Farmasi).

## Struktur Folder

```
pbf/
├── pbf1_name/
│   ├── daftar_harga_januari_2024.pdf
│   ├── daftar_harga_februari_2024.pdf
│   └── ...
├── pbf2_name/
│   ├── price_list_jan_2024.pdf
│   └── ...
└── ...
```

## Format File yang Didukung

- **Format**: PDF
- **Ukuran maksimal**: 10MB per file
- **Struktur**: Tabel dengan kolom yang jelas

## Kolom yang Dikenali

### Nama Obat/Barang:
- NAMA BRG
- NAMA BARANG  
- NAMA OBAT
- BARANG
- PRODUK

### Harga:
- HNA+PPN
- HRG+PPN
- HARGA JADI
- HARGA
- TOTAL

### Stok:
- STOK
- STOK TERAKHIR
- QTY
- QUANTITY

### Diskon:
- DISKON
- DISCOUNT
- DISC
- POTONGAN

## Petunjuk Penggunaan

1. Simpan file PDF daftar harga di folder ini
2. Buat subfolder untuk setiap PBF jika diperlukan
3. Upload file melalui interface aplikasi
4. Aplikasi akan otomatis mengenali struktur tabel dan mengekstrak data

## Tips untuk Hasil Terbaik

- Pastikan PDF berisi tabel yang terstruktur
- Hindari PDF yang hanya berisi gambar tanpa teks
- Kolom header harus jelas dan sesuai dengan format yang dikenali
- File tidak boleh terproteksi password