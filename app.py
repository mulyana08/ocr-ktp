"""
OCR KTP - Streamlit Web Application
Extract data from Indonesian ID Card (KTP) using Google Gemini Flash
"""
import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from PIL import Image
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ocr_ktp import OCRKtp


# Page configuration
st.set_page_config(
    page_title="OCR KTP Indonesia",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with light blue background theme
st.markdown("""
<style>
    /* Apply light blue background to main container */
    .stApp {
        background-color: #e3f2fd;
    }
    
    /* Apply light blue background to sidebar */
    section[data-testid="stSidebar"] {
        background-color: #bbdefb;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def init_ocr():
    """Initialize OCR with API key from session state or environment."""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return None
    try:
        return OCRKtp(api_key=api_key)
    except ValueError:
        return None


def display_result_table(data: dict):
    """Display extracted KTP data in a table format."""
    fields = [
        ("NIK", "nik"),
        ("Nama", "nama"),
        ("Tempat Lahir", "tempat_lahir"),
        ("Tanggal Lahir", "tanggal_lahir"),
        ("Jenis Kelamin", "jenis_kelamin"),
        ("Alamat", "alamat"),
        ("RT/RW", "rt_rw"),
        ("Kelurahan/Desa", "kelurahan_desa"),
        ("Kecamatan", "kecamatan"),
        ("Agama", "agama"),
        ("Status Perkawinan", "status_perkawinan"),
        ("Pekerjaan", "pekerjaan"),
        ("Kewarganegaraan", "kewarganegaraan"),
        ("Berlaku Hingga", "berlaku_hingga"),
    ]
    
    table_data = []
    for label, key in fields:
        value = data.get(key, "-") or "-"
        table_data.append({"Field": label, "Nilai": value})
    
    df = pd.DataFrame(table_data)
    st.table(df)


def main():
    # Header
    st.markdown('<p class="main-header">🪪 OCR KTP Indonesia</p>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: gray;'>"
        "Ekstrak data dari gambar KTP Indonesia menggunakan AI (Google Gemini Flash)"
        "</p>",
        unsafe_allow_html=True
    )
    
    # Sidebar for API Key
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        # Try to load API key from environment first
        env_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Initialize session state with env key if available
        if "api_key" not in st.session_state and env_api_key:
            st.session_state["api_key"] = env_api_key
        
        api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            placeholder="Masukkan API Key...",
            help="Dapatkan API Key di https://makersuite.google.com/app/apikey"
        )
        
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("✅ API Key tersimpan")
        
        st.markdown("---")
        st.markdown("### 📖 Cara Penggunaan")
        st.markdown("""
        1. Masukkan Gemini API Key
        2. Upload foto KTP
        3. Klik tombol **Ekstrak Data**
        4. Lihat dan download hasilnya
        """)
        
        st.markdown("---")
        st.markdown("### ⚠️ Catatan Keamanan")
        st.markdown("""
        - Data KTP bersifat sensitif
        - Gambar tidak disimpan di server
        - Gunakan untuk keperluan yang sah
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Gambar KTP")
        
        uploaded_file = st.file_uploader(
            "Pilih file gambar KTP",
            type=["jpg", "jpeg", "png", "webp"],
            help="Format yang didukung: JPG, JPEG, PNG, WEBP"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Gambar KTP yang diupload", use_container_width=True)
            
            # Extract button
            if st.button("🔍 Ekstrak Data", type="primary", use_container_width=True):
                if not st.session_state.get("api_key"):
                    st.error("❌ Silakan masukkan API Key terlebih dahulu di sidebar!")
                else:
                    with st.spinner("⏳ Mengekstrak data dari KTP..."):
                        try:
                            ocr = OCRKtp(api_key=st.session_state["api_key"])
                            
                            # Reset file position and read bytes
                            uploaded_file.seek(0)
                            image_bytes = uploaded_file.read()
                            
                            result = ocr.extract_from_bytes(image_bytes)
                            
                            if result["success"]:
                                st.session_state["result"] = result["data"]
                                st.success("✅ Ekstraksi berhasil!")
                            else:
                                st.error(f"❌ Error: {result['error']}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("📋 Hasil Ekstraksi")
        
        if "result" in st.session_state and st.session_state["result"]:
            data = st.session_state["result"]
            
            # Display as table
            tab1, tab2 = st.tabs(["📊 Tabel", "📝 JSON"])
            
            with tab1:
                display_result_table(data)
            
            with tab2:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.code(json_str, language="json")
            
            # Download buttons
            st.markdown("### 💾 Download Hasil")
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
                st.download_button(
                    label="📥 Download JSON",
                    data=json_bytes,
                    file_name="hasil_ktp.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_dl2:
                # Create CSV
                csv_data = []
                for key, value in data.items():
                    csv_data.append(f"{key},{value or ''}")
                csv_str = "field,value\n" + "\n".join(csv_data)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_str.encode("utf-8"),
                    file_name="hasil_ktp.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.markdown(
                '<div class="info-box">'
                '📌 Upload gambar KTP dan klik "Ekstrak Data" untuk melihat hasil di sini.'
                '</div>',
                unsafe_allow_html=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 0.8rem;'>"
        "Dibuat dengan ❤️ menggunakan Streamlit dan Google Gemini Flash"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
