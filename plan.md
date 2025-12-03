# Plan: OCR KTP dengan Gemini Flash

## 📋 Deskripsi Proyek
Membangun aplikasi OCR (Optical Character Recognition) untuk mengekstrak data dari KTP (Kartu Tanda Penduduk) Indonesia menggunakan Google Gemini Flash API.

---

## 🎯 Tujuan
- Mengekstrak informasi dari gambar KTP secara otomatis
- Mendapatkan data terstruktur seperti NIK, Nama, Tempat/Tanggal Lahir, Alamat, dll.
- Memberikan output dalam format JSON yang mudah diproses

---

## 📦 Data yang Akan Diekstrak dari KTP
| No | Field | Keterangan |
|----|-------|------------|
| 1 | NIK | Nomor Induk Kependudukan (16 digit) |
| 2 | Nama | Nama lengkap |
| 3 | Tempat Lahir | Kota/Kabupaten kelahiran |
| 4 | Tanggal Lahir | Format DD-MM-YYYY |
| 5 | Jenis Kelamin | Laki-laki / Perempuan |
| 6 | Alamat | Alamat lengkap |
| 7 | RT/RW | Nomor RT dan RW |
| 8 | Kelurahan/Desa | Nama kelurahan atau desa |
| 9 | Kecamatan | Nama kecamatan |
| 10 | Agama | Agama yang tertera |
| 11 | Status Perkawinan | Belum Kawin / Kawin / Cerai |
| 12 | Pekerjaan | Jenis pekerjaan |
| 13 | Kewarganegaraan | WNI / WNA |
| 14 | Berlaku Hingga | Tanggal berlaku atau SEUMUR HIDUP |

---

## 🛠️ Tech Stack
| Komponen | Teknologi |
|----------|----------|
| Bahasa Pemrograman | Python 3.9+ |
| AI Model | Google Gemini 2.0 Flash |
| Library Utama | `google-generativeai` |
| Image Processing | `Pillow` (PIL) |
| Web Interface | `Streamlit` |
| Output Format | JSON |

---

## 📁 Struktur Proyek
```
latihan_01/
├── plan.md                 # Dokumen perencanaan (file ini)
├── requirements.txt        # Dependencies Python
├── .env                    # API Key (tidak di-commit ke git)
├── .env.example            # Template API Key
├── .gitignore              # File yang diabaikan git
├── src/
│   ├── __init__.py
│   ├── ocr_ktp.py          # Modul utama OCR KTP
│   └── utils.py            # Fungsi utilitas
├── samples/                # Folder untuk sample gambar KTP
│   └── .gitkeep
├── main.py                 # Entry point CLI
├── app.py                  # Entry point Streamlit Web App
└── README.md               # Dokumentasi penggunaan
```

---

## 🔧 Langkah Implementasi

### Fase 1: Setup Environment ✅
1. ✅ Membuat virtual environment Python
2. ✅ Menginstall dependencies
3. ✅ Menyiapkan file `.env.example` untuk template API Key
4. ✅ Membuat `.gitignore` untuk keamanan
5. ✅ Membuat folder `samples/` untuk gambar KTP

### Fase 2: Modul Utama OCR ✅
1. ✅ Membuat `src/__init__.py` - Package initialization
2. ✅ Membuat `src/utils.py` - Fungsi utilitas
3. ✅ Membuat `src/ocr_ktp.py` - Modul utama OCR

### Fase 3: Entry Point CLI ✅
1. ✅ Membuat `main.py` sebagai entry point CLI
2. ✅ Error handling dan validasi input

### Fase 4: Web Interface (Streamlit) ✅
1. ✅ Membuat `app.py` dengan Streamlit
2. ✅ Upload gambar, preview, dan download hasil

### Fase 5: Dokumentasi ✅
1. ✅ Membuat `README.md`
2. ✅ Update `plan.md` dengan progress implementasi

### Fase 6: Fitur Tambahan ✅
1. ✅ Validasi gambar bukan KTP
2. ✅ Auto-load API Key dari file `.env`
3. ✅ Update model ke Gemini 2.0 Flash

---

## ✅ Checklist Implementasi
- [x] Setup virtual environment Python
- [x] Install dependencies
- [x] Buat file konfigurasi (.env, .gitignore)
- [x] Buat modul OCR KTP (src/ocr_ktp.py)
- [x] Buat fungsi utilitas (src/utils.py)
- [x] Buat CLI entry point (main.py)
- [x] Buat Web Interface Streamlit (app.py)
- [x] Tambahkan validasi gambar bukan KTP
- [x] Buat dokumentasi (README.md)
- [x] Testing dengan sample KTP

---

## 🚀 Cara Penggunaan

### Opsi 1: Command Line (CLI)
```bash
python main.py --image path/to/ktp.jpg
```

### Opsi 2: Web Interface (Streamlit)
```bash
streamlit run app.py
# Buka browser di http://localhost:8501
```

---

## 📤 Contoh Output
```json
{
  "nik": "3201234567890001",
  "nama": "JOHN DOE",
  "tempat_lahir": "JAKARTA",
  "tanggal_lahir": "17-08-1990",
  "jenis_kelamin": "LAKI-LAKI",
  "alamat": "JL. MERDEKA NO. 123",
  "rt_rw": "001/002",
  "kelurahan_desa": "MENTENG",
  "kecamatan": "MENTENG",
  "agama": "ISLAM",
  "status_perkawinan": "KAWIN",
  "pekerjaan": "KARYAWAN SWASTA",
  "kewarganegaraan": "WNI",
  "berlaku_hingga": "SEUMUR HIDUP"
}
```

---

**Status:** ✅ Selesai - Implementasi Lengkap
