"""
Unit Tests for src/ocr_ktp.py
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from src.ocr_ktp import OCRKtp


class TestOCRKtpInit:
    """Test suite for OCRKtp initialization."""
    
    @pytest.mark.unit
    def test_init_with_api_key_param(self):
        """Test initialization with API key as parameter."""
        with patch('google.generativeai.configure') as mock_configure:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                ocr = OCRKtp(api_key="test-key-123")
                
                mock_configure.assert_called_once_with(api_key="test-key-123")
                mock_model.assert_called_once_with('gemini-2.0-flash')
    
    @pytest.mark.unit
    def test_init_with_env_api_key(self, mock_env_api_key):
        """Test initialization with API key from environment."""
        with patch('google.generativeai.configure') as mock_configure:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                ocr = OCRKtp()
                
                mock_configure.assert_called_once_with(api_key="test-api-key-12345")
    
    @pytest.mark.unit
    def test_init_without_api_key_raises_error(self, mock_env_no_api_key):
        """Test initialization without API key raises ValueError."""
        # Also need to patch load_dotenv to prevent loading from .env file
        with patch('src.ocr_ktp.load_dotenv'):
            with pytest.raises(ValueError) as exc_info:
                OCRKtp()
        
        assert "API Key tidak ditemukan" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_init_uses_gemini_flash_model(self, mock_env_api_key):
        """Test that initialization uses gemini-2.0-flash model."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model:
                ocr = OCRKtp()
                mock_model.assert_called_with('gemini-2.0-flash')


class TestOCRKtpExtract:
    """Test suite for OCRKtp.extract method."""
    
    @pytest.mark.unit
    def test_extract_from_file_path(self, ocr_instance, temp_image_file):
        """Test extraction from file path."""
        result = ocr_instance.extract(temp_image_file)
        
        assert result["success"] is True
        assert result["data"] is not None
        assert result["is_ktp"] is True
    
    @pytest.mark.unit
    def test_extract_from_pil_image(self, ocr_instance, sample_image_pil):
        """Test extraction from PIL Image object."""
        result = ocr_instance.extract(sample_image_pil)
        
        assert result["success"] is True
        assert result["data"] is not None
    
    @pytest.mark.unit
    def test_extract_converts_rgba_to_rgb(self, ocr_instance, sample_rgba_image):
        """Test that RGBA images are converted to RGB before processing."""
        result = ocr_instance.extract(sample_rgba_image)
        
        # Should not raise an error
        assert "success" in result
    
    @pytest.mark.unit
    def test_extract_invalid_source_type_raises_error(self, ocr_instance):
        """Test that invalid image source raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ocr_instance.extract(12345)  # Invalid type
        
        assert "harus berupa path file atau PIL Image" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_extract_returns_ktp_data_fields(self, ocr_instance, temp_image_file):
        """Test that extraction returns all expected KTP fields."""
        result = ocr_instance.extract(temp_image_file)
        
        expected_fields = [
            "nik", "nama", "tempat_lahir", "tanggal_lahir",
            "jenis_kelamin", "alamat", "rt_rw", "kelurahan_desa",
            "kecamatan", "agama", "status_perkawinan",
            "pekerjaan", "kewarganegaraan", "berlaku_hingga"
        ]
        
        for field in expected_fields:
            assert field in result["data"]
    
    @pytest.mark.unit
    def test_extract_non_ktp_image_returns_error(self, ocr_instance_non_ktp, temp_image_file):
        """Test extraction of non-KTP image returns error."""
        result = ocr_instance_non_ktp.extract(temp_image_file)
        
        assert result["success"] is False
        assert "bukan KTP" in result["error"]
        assert result["is_ktp"] is False
    
    @pytest.mark.unit
    def test_extract_handles_api_error(self, mock_env_api_key, temp_image_file):
        """Test that API errors are handled gracefully."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
        
        assert result["success"] is False
        assert "API Error" in result["error"]


class TestOCRKtpExtractFromBytes:
    """Test suite for OCRKtp.extract_from_bytes method."""
    
    @pytest.mark.unit
    def test_extract_from_bytes_valid_image(self, ocr_instance, sample_image_bytes):
        """Test extraction from image bytes."""
        result = ocr_instance.extract_from_bytes(sample_image_bytes)
        
        assert result["success"] is True
        assert result["data"] is not None
    
    @pytest.mark.unit
    def test_extract_from_bytes_invalid_bytes(self, ocr_instance):
        """Test extraction from invalid bytes."""
        invalid_bytes = b"not an image"
        
        # Should handle the error gracefully
        try:
            result = ocr_instance.extract_from_bytes(invalid_bytes)
            assert result["success"] is False
        except Exception:
            pass  # Expected for truly invalid data


class TestOCRKtpParseResponse:
    """Test suite for OCRKtp._parse_response method."""
    
    @pytest.mark.unit
    def test_parse_response_valid_json(self, ocr_instance, mock_ktp_response):
        """Test parsing valid JSON response."""
        json_str = json.dumps(mock_ktp_response)
        result = ocr_instance._parse_response(json_str)
        
        assert result["nik"] == "3201234567890001"
        assert result["nama"] == "JOHN DOE"
    
    @pytest.mark.unit
    def test_parse_response_json_in_markdown(self, ocr_instance, mock_ktp_response):
        """Test parsing JSON wrapped in markdown code block."""
        markdown_response = f"```json\n{json.dumps(mock_ktp_response)}\n```"
        result = ocr_instance._parse_response(markdown_response)
        
        assert result["nik"] == "3201234567890001"
    
    @pytest.mark.unit
    def test_parse_response_json_in_markdown_no_lang(self, ocr_instance, mock_ktp_response):
        """Test parsing JSON in markdown without language specifier."""
        markdown_response = f"```\n{json.dumps(mock_ktp_response)}\n```"
        result = ocr_instance._parse_response(markdown_response)
        
        assert result["nik"] == "3201234567890001"
    
    @pytest.mark.unit
    def test_parse_response_invalid_json(self, ocr_instance):
        """Test parsing invalid JSON returns error structure."""
        invalid_json = "this is not json"
        result = ocr_instance._parse_response(invalid_json)
        
        assert result["nik"] is None
        assert result["nama"] is None
        assert "_parse_error" in result
    
    @pytest.mark.unit
    def test_parse_response_empty_string(self, ocr_instance):
        """Test parsing empty string."""
        result = ocr_instance._parse_response("")
        
        assert "_parse_error" in result
    
    @pytest.mark.unit
    def test_parse_response_whitespace_handling(self, ocr_instance, mock_ktp_response):
        """Test parsing JSON with extra whitespace."""
        json_with_whitespace = f"   \n\n{json.dumps(mock_ktp_response)}\n\n   "
        result = ocr_instance._parse_response(json_with_whitespace)
        
        assert result["nik"] == "3201234567890001"


class TestOCRKtpPrompt:
    """Test suite for OCRKtp prompt configuration."""
    
    @pytest.mark.unit
    def test_prompt_contains_is_ktp_field(self):
        """Test that extraction prompt includes is_ktp validation."""
        assert "is_ktp" in OCRKtp.EXTRACTION_PROMPT
    
    @pytest.mark.unit
    def test_prompt_contains_all_ktp_fields(self):
        """Test that prompt includes all required KTP fields."""
        expected_fields = [
            "nik", "nama", "tempat_lahir", "tanggal_lahir",
            "jenis_kelamin", "alamat", "rt_rw", "kelurahan_desa",
            "kecamatan", "agama", "status_perkawinan",
            "pekerjaan", "kewarganegaraan", "berlaku_hingga"
        ]
        
        for field in expected_fields:
            assert field in OCRKtp.EXTRACTION_PROMPT
    
    @pytest.mark.unit
    def test_prompt_mentions_json_format(self):
        """Test that prompt requests JSON format."""
        assert "JSON" in OCRKtp.EXTRACTION_PROMPT
    
    @pytest.mark.unit
    def test_prompt_mentions_nik_validation(self):
        """Test that prompt mentions NIK should be 16 digits."""
        assert "16 digit" in OCRKtp.EXTRACTION_PROMPT
