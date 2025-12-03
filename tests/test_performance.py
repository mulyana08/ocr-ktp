"""
Performance Tests for OCR KTP Application

Note: Some tests may fail on systems with low file descriptor limits.
To increase limit, run: ulimit -n 4096
"""
import pytest
import time
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import io


class TestImageProcessingPerformance:
    """Performance tests for image processing operations."""
    
    @pytest.mark.performance
    def test_image_load_performance(self, perf_image_file, benchmark):
        """Benchmark image loading performance."""
        from src.utils import load_image
        
        # Reduce iterations for macOS file limit
        benchmark.pedantic(load_image, args=(perf_image_file,), rounds=10, iterations=1)
    
    @pytest.mark.performance
    def test_image_validation_performance(self, perf_image_file, benchmark):
        """Benchmark image validation performance."""
        from src.utils import validate_image
        
        # Reduce iterations for macOS file limit
        benchmark.pedantic(validate_image, args=(perf_image_file,), rounds=10, iterations=1)
    
    @pytest.mark.performance
    def test_large_image_processing(self):
        """Test processing of large image (4K resolution)."""
        from src.utils import load_image, validate_image
        
        # Create a large image (4K) using tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            large_path = f.name
        
        try:
            large_img = Image.new('RGB', (3840, 2160), color='white')
            large_img.save(large_path, format='JPEG', quality=95)
            large_img.close()
            
            start_time = time.time()
            
            # Validate
            is_valid, _ = validate_image(large_path)
            assert is_valid is True
            
            # Load
            img = load_image(large_path)
            assert img is not None
            img.close()
            
            elapsed = time.time() - start_time
            
            # Should complete within 2 seconds
            assert elapsed < 2.0, f"Large image processing took {elapsed:.2f}s"
        finally:
            os.unlink(large_path)
    
    @pytest.mark.performance
    def test_multiple_small_images(self):
        """Test processing multiple small images."""
        from src.utils import load_image, validate_image
        
        # Create 5 small images (reduced for file limit)
        image_paths = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                img = Image.new('RGB', (800, 500), color='white')
                img.save(f.name, format='JPEG')
                img.close()
                image_paths.append(f.name)
        
        try:
            start_time = time.time()
            
            for img_path in image_paths:
                validate_image(img_path)
                loaded = load_image(img_path)
                if loaded:
                    loaded.close()
            
            elapsed = time.time() - start_time
            
            # Should process 5 images within 0.5 second
            assert elapsed < 0.5, f"Processing 5 images took {elapsed:.2f}s"
        finally:
            for path in image_paths:
                os.unlink(path)


class TestFormattingPerformance:
    """Performance tests for output formatting."""
    
    @pytest.mark.performance
    def test_format_ktp_data_performance(self, sample_ktp_data, benchmark):
        """Benchmark KTP data formatting performance."""
        from src.utils import format_ktp_data
        
        result = benchmark(format_ktp_data, sample_ktp_data)
        
        assert "DATA KTP" in result
    
    @pytest.mark.performance
    def test_format_large_data_performance(self, benchmark):
        """Test formatting with large address data."""
        from src.utils import format_ktp_data
        
        # Create data with very long address
        large_data = {
            "nik": "3201234567890001",
            "nama": "VERY LONG NAME THAT GOES ON AND ON AND ON",
            "tempat_lahir": "JAKARTA",
            "tanggal_lahir": "17-08-1990",
            "jenis_kelamin": "LAKI-LAKI",
            "alamat": "JL. SANGAT PANJANG SEKALI NO. 123 BLOK ABC RT 001 RW 002 " * 5,
            "rt_rw": "001/002",
            "kelurahan_desa": "KELURAHAN DENGAN NAMA YANG SANGAT PANJANG",
            "kecamatan": "KECAMATAN YANG JUGA PANJANG NAMANYA",
            "agama": "ISLAM",
            "status_perkawinan": "BELUM KAWIN",
            "pekerjaan": "KARYAWAN SWASTA DI PERUSAHAAN BESAR",
            "kewarganegaraan": "WNI",
            "berlaku_hingga": "SEUMUR HIDUP"
        }
        
        result = benchmark(format_ktp_data, large_data)
        
        assert "DATA KTP" in result


class TestJSONParsingPerformance:
    """Performance tests for JSON parsing."""
    
    @pytest.mark.performance
    def test_json_parsing_speed(self, benchmark):
        """Benchmark pure JSON parsing performance."""
        test_json = json.dumps({
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
        
        result = benchmark(json.loads, test_json)
        
        assert result["nik"] is not None


class TestOCRPerformance:
    """Performance tests for OCR operations (basic, no file I/O heavy)."""
    
    @pytest.mark.performance
    def test_ocr_init_performance(self, perf_mock_gemini_model, monkeypatch, benchmark):
        """Benchmark OCR initialization performance."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-12345")
        
        def create_ocr():
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel', return_value=perf_mock_gemini_model):
                    with patch('src.ocr_ktp.load_dotenv'):
                        from src.ocr_ktp import OCRKtp
                        return OCRKtp()
        
        # Reduce rounds to avoid file handle exhaustion
        benchmark.pedantic(create_ocr, rounds=5, iterations=1)
    
    @pytest.mark.performance
    def test_parse_response_performance(self, perf_mock_gemini_model, monkeypatch):
        """Test parse_response performance without benchmark overhead."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-12345")
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=perf_mock_gemini_model):
                with patch('src.ocr_ktp.load_dotenv'):
                    from src.ocr_ktp import OCRKtp
                    
                    ocr = OCRKtp()
                    
                    test_json = json.dumps({
                        "is_ktp": True,
                        "nik": "3201234567890001",
                        "nama": "JOHN DOE"
                    })
                    
                    start_time = time.time()
                    for _ in range(100):
                        ocr._parse_response(test_json)
                    elapsed = time.time() - start_time
                    
                    # 100 parses should complete within 0.1 second
                    assert elapsed < 0.1, f"100 parses took {elapsed:.2f}s"
