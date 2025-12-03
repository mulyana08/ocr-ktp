"""
Pytest Configuration and Shared Fixtures
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_fixtures_dir(project_root):
    """Return test fixtures directory."""
    fixtures_dir = project_root / "tests" / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    return fixtures_dir


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Mock environment with API key."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-12345")


@pytest.fixture
def mock_env_no_api_key(monkeypatch):
    """Mock environment without API key."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


# ============================================================================
# Image Fixtures
# ============================================================================

@pytest.fixture
def sample_image_bytes():
    """Create a sample image as bytes."""
    img = Image.new('RGB', (800, 500), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_image_pil():
    """Create a sample PIL Image."""
    return Image.new('RGB', (800, 500), color='white')


@pytest.fixture
def sample_rgba_image():
    """Create a sample RGBA image (needs conversion)."""
    return Image.new('RGBA', (800, 500), color=(255, 255, 255, 255))


@pytest.fixture
def temp_image_file(tmp_path, sample_image_pil):
    """Create a temporary image file."""
    image_path = tmp_path / "test_image.jpg"
    sample_image_pil.save(image_path, format='JPEG')
    return str(image_path)


@pytest.fixture
def temp_png_image(tmp_path):
    """Create a temporary PNG image."""
    img = Image.new('RGB', (800, 500), color='blue')
    image_path = tmp_path / "test_image.png"
    img.save(image_path, format='PNG')
    return str(image_path)


@pytest.fixture
def corrupted_image_file(tmp_path):
    """Create a corrupted image file."""
    image_path = tmp_path / "corrupted.jpg"
    with open(image_path, 'wb') as f:
        f.write(b'not a valid image content')
    return str(image_path)


@pytest.fixture
def large_image_file(tmp_path):
    """Create a large image file (>10MB simulation)."""
    # Create a path that we'll pretend is too large
    image_path = tmp_path / "large_image.jpg"
    # Write more than 10MB of data
    with open(image_path, 'wb') as f:
        f.write(b'0' * (11 * 1024 * 1024))  # 11MB
    return str(image_path)


# ============================================================================
# Mock Gemini Response Fixtures
# ============================================================================

@pytest.fixture
def mock_ktp_response():
    """Mock successful KTP extraction response."""
    return {
        "is_ktp": True,
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


@pytest.fixture
def mock_non_ktp_response():
    """Mock response for non-KTP image."""
    return {
        "is_ktp": False,
        "nik": None,
        "nama": None,
        "tempat_lahir": None,
        "tanggal_lahir": None,
        "jenis_kelamin": None,
        "alamat": None,
        "rt_rw": None,
        "kelurahan_desa": None,
        "kecamatan": None,
        "agama": None,
        "status_perkawinan": None,
        "pekerjaan": None,
        "kewarganegaraan": None,
        "berlaku_hingga": None
    }


@pytest.fixture
def mock_gemini_model(mock_ktp_response):
    """Mock Gemini GenerativeModel."""
    import json
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_ktp_response)
    mock_model.generate_content.return_value = mock_response
    return mock_model


@pytest.fixture
def mock_gemini_model_non_ktp(mock_non_ktp_response):
    """Mock Gemini model that returns non-KTP response."""
    import json
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_non_ktp_response)
    mock_model.generate_content.return_value = mock_response
    return mock_model


# ============================================================================
# OCR Instance Fixtures
# ============================================================================

@pytest.fixture
def ocr_instance(mock_env_api_key, mock_gemini_model):
    """Create OCRKtp instance with mocked Gemini."""
    with patch('google.generativeai.configure'):
        with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
            from src.ocr_ktp import OCRKtp
            return OCRKtp()


@pytest.fixture
def ocr_instance_non_ktp(mock_env_api_key, mock_gemini_model_non_ktp):
    """Create OCRKtp instance that returns non-KTP response."""
    with patch('google.generativeai.configure'):
        with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model_non_ktp):
            from src.ocr_ktp import OCRKtp
            return OCRKtp()


# ============================================================================
# Performance Test Fixtures (function scope for benchmark compatibility)
# ============================================================================

@pytest.fixture
def perf_image_file():
    """Create a temporary image file for performance tests."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        img = Image.new('RGB', (800, 500), color='white')
        img.save(f.name, format='JPEG')
        img.close()
        path = f.name
    
    yield path
    
    # Cleanup
    import os
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def perf_image_bytes():
    """Create sample image bytes for performance tests."""
    img = Image.new('RGB', (800, 500), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def perf_mock_gemini_model():
    """Mock Gemini model for performance tests."""
    import json
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "is_ktp": True,
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
    })
    mock_model.generate_content.return_value = mock_response
    return mock_model


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def sample_ktp_data():
    """Sample KTP data for formatting tests."""
    return {
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


@pytest.fixture
def empty_ktp_data():
    """Empty KTP data with null values."""
    return {
        "nik": None,
        "nama": None,
        "tempat_lahir": None,
        "tanggal_lahir": None,
        "jenis_kelamin": None,
        "alamat": None,
        "rt_rw": None,
        "kelurahan_desa": None,
        "kecamatan": None,
        "agama": None,
        "status_perkawinan": None,
        "pekerjaan": None,
        "kewarganegaraan": None,
        "berlaku_hingga": None
    }
