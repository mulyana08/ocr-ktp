"""
Unit Tests for src/utils.py
"""
import pytest
import os
from pathlib import Path
from PIL import Image

from src.utils import validate_image, load_image, format_ktp_data, SUPPORTED_FORMATS, MAX_FILE_SIZE


class TestValidateImage:
    """Test suite for validate_image function."""
    
    @pytest.mark.unit
    def test_validate_image_valid_jpg(self, temp_image_file):
        """Test validation with valid JPG image."""
        is_valid, message = validate_image(temp_image_file)
        assert is_valid is True
        assert "valid" in message.lower()
    
    @pytest.mark.unit
    def test_validate_image_valid_png(self, temp_png_image):
        """Test validation with valid PNG image."""
        is_valid, message = validate_image(temp_png_image)
        assert is_valid is True
        assert "valid" in message.lower()
    
    @pytest.mark.unit
    def test_validate_image_file_not_found(self):
        """Test validation with non-existent file."""
        is_valid, message = validate_image("/path/to/nonexistent/image.jpg")
        assert is_valid is False
        assert "tidak ditemukan" in message.lower()
    
    @pytest.mark.unit
    def test_validate_image_unsupported_format(self, tmp_path):
        """Test validation with unsupported file format."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not an image")
        
        is_valid, message = validate_image(str(txt_file))
        assert is_valid is False
        assert "tidak didukung" in message.lower()
    
    @pytest.mark.unit
    def test_validate_image_corrupted(self, corrupted_image_file):
        """Test validation with corrupted image file."""
        is_valid, message = validate_image(corrupted_image_file)
        assert is_valid is False
        assert "tidak valid" in message.lower()
    
    @pytest.mark.unit
    def test_validate_image_too_large(self, large_image_file):
        """Test validation with file exceeding size limit."""
        is_valid, message = validate_image(large_image_file)
        assert is_valid is False
        assert "terlalu besar" in message.lower()
    
    @pytest.mark.unit
    def test_supported_formats_includes_common_types(self):
        """Test that supported formats include common image types."""
        assert '.jpg' in SUPPORTED_FORMATS
        assert '.jpeg' in SUPPORTED_FORMATS
        assert '.png' in SUPPORTED_FORMATS
        assert '.webp' in SUPPORTED_FORMATS
    
    @pytest.mark.unit
    def test_max_file_size_is_10mb(self):
        """Test that max file size is 10MB."""
        assert MAX_FILE_SIZE == 10 * 1024 * 1024


class TestLoadImage:
    """Test suite for load_image function."""
    
    @pytest.mark.unit
    def test_load_image_valid_jpg(self, temp_image_file):
        """Test loading valid JPG image."""
        image = load_image(temp_image_file)
        assert image is not None
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
    
    @pytest.mark.unit
    def test_load_image_valid_png(self, temp_png_image):
        """Test loading valid PNG image."""
        image = load_image(temp_png_image)
        assert image is not None
        assert isinstance(image, Image.Image)
    
    @pytest.mark.unit
    def test_load_image_nonexistent_file(self):
        """Test loading non-existent file returns None."""
        image = load_image("/path/to/nonexistent/image.jpg")
        assert image is None
    
    @pytest.mark.unit
    def test_load_image_corrupted_file(self, corrupted_image_file):
        """Test loading corrupted file returns None."""
        image = load_image(corrupted_image_file)
        assert image is None
    
    @pytest.mark.unit
    def test_load_image_converts_rgba_to_rgb(self, tmp_path):
        """Test that RGBA images are converted to RGB."""
        # Create RGBA image
        rgba_img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        rgba_path = tmp_path / "rgba_test.png"
        rgba_img.save(rgba_path, format='PNG')
        
        loaded = load_image(str(rgba_path))
        assert loaded is not None
        assert loaded.mode == 'RGB'


class TestFormatKtpData:
    """Test suite for format_ktp_data function."""
    
    @pytest.mark.unit
    def test_format_ktp_data_complete(self, sample_ktp_data):
        """Test formatting complete KTP data."""
        output = format_ktp_data(sample_ktp_data)
        
        assert "DATA KTP" in output
        assert "NIK" in output
        assert "3201234567890001" in output
        assert "JOHN DOE" in output
        assert "JAKARTA" in output
    
    @pytest.mark.unit
    def test_format_ktp_data_empty(self, empty_ktp_data):
        """Test formatting empty KTP data."""
        output = format_ktp_data(empty_ktp_data)
        
        assert "DATA KTP" in output
        assert "-" in output  # Should show dashes for null values
    
    @pytest.mark.unit
    def test_format_ktp_data_partial(self):
        """Test formatting partial KTP data."""
        partial_data = {
            "nik": "1234567890123456",
            "nama": "TEST NAME",
            "alamat": None
        }
        output = format_ktp_data(partial_data)
        
        assert "1234567890123456" in output
        assert "TEST NAME" in output
        assert "-" in output  # For missing/None values
    
    @pytest.mark.unit
    def test_format_ktp_data_contains_all_fields(self, sample_ktp_data):
        """Test that output contains all expected field labels."""
        output = format_ktp_data(sample_ktp_data)
        
        expected_labels = [
            "NIK", "Nama", "Tempat Lahir", "Tanggal Lahir",
            "Jenis Kelamin", "Alamat", "RT/RW", "Kel/Desa",
            "Kecamatan", "Agama", "Status Perkawinan",
            "Pekerjaan", "Kewarganegaraan", "Berlaku Hingga"
        ]
        
        for label in expected_labels:
            assert label in output
    
    @pytest.mark.unit
    def test_format_ktp_data_has_separators(self, sample_ktp_data):
        """Test that output has visual separators."""
        output = format_ktp_data(sample_ktp_data)
        assert "=" * 50 in output
