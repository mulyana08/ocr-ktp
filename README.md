# 🪪 OCR KTP Indonesia

Aplikasi untuk mengekstrak data dari gambar KTP (Kartu Tanda Penduduk) Indonesia menggunakan Google Gemini Flash AI.

## ✨ Fitur

- 📷 Ekstrak data dari gambar KTP secara otomatis
- 🌐 Web interface dengan Streamlit
- 💻 Command-line interface (CLI)
- 📊 Output dalam format JSON dan tabel
- 💾 Download hasil dalam format JSON/CSV

## 📦 Data yang Diekstrak

| Field | Keterangan |
|-------|------------|
| NIK | Nomor Induk Kependudukan (16 digit) |
| Nama | Nama lengkap |
| Tempat/Tanggal Lahir | Kota dan tanggal lahir |
| Jenis Kelamin | Laki-laki / Perempuan |
| Alamat | Alamat lengkap dengan RT/RW |
| Kelurahan/Desa | Nama kelurahan |
| Kecamatan | Nama kecamatan |
| Agama | Agama yang tertera |
| Status Perkawinan | Status perkawinan |
| Pekerjaan | Jenis pekerjaan |
| Kewarganegaraan | WNI / WNA |
| Berlaku Hingga | Masa berlaku KTP |

## 🛠️ Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/mulyana08/ocr-ktp.git
cd ocr-ktp
```

### 2. Buat Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup API Key

```bash
cp .env.example .env
```

Edit file `.env` dan masukkan Gemini API Key Anda:

```
GEMINI_API_KEY=your-api-key-here
```

> 💡 Dapatkan API Key di: https://makersuite.google.com/app/apikey

## 🚀 Cara Penggunaan

### Web Interface (Streamlit)

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`

### Command Line (CLI)

```bash
# Basic usage
python main.py --image path/to/ktp.jpg

# Output JSON format
python main.py --image path/to/ktp.jpg --format json

# Save to file
python main.py --image path/to/ktp.jpg --output hasil.json
```

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

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## 📁 Struktur Proyek

```
ocr-ktp/
├── app.py              # Streamlit web app
├── main.py             # CLI entry point
├── requirements.txt    # Dependencies
├── .env.example        # Template API key
├── src/
│   ├── __init__.py
│   ├── ocr_ktp.py      # OCR module
│   └── utils.py        # Utility functions
├── tests/              # Test suite
└── .github/
    └── workflows/      # CI/CD
```

## ⚠️ Catatan Keamanan

- 🔐 Jangan commit file `.env` yang berisi API Key
- 🔒 Data KTP adalah data sensitif - gunakan dengan bijak
- ✅ Aplikasi ini tidak menyimpan data apapun di server

## 📄 Lisensi

MIT License

---

Dibuat dengan ❤️ menggunakan Python, Streamlit, dan Google Gemini Flash
