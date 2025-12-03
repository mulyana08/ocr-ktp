"""
Integration Tests for OCR KTP Application
"""
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLIIntegration:
    """Integration tests for CLI (main.py)."""
    
    @pytest.mark.integration
    def test_cli_with_valid_image(self, temp_image_file, mock_env_api_key, mock_gemini_model, capsys):
        """Test CLI with valid image file."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from main import main
                
                # Mock sys.argv
                test_args = ['main.py', '--image', temp_image_file, '--format', 'json']
                with patch.object(sys, 'argv', test_args):
                    try:
                        main()
                    except SystemExit:
                        pass
    
    @pytest.mark.integration
    def test_cli_with_nonexistent_image(self, mock_env_api_key, capsys):
        """Test CLI with non-existent image file."""
        from main import main
        
        test_args = ['main.py', '--image', '/nonexistent/image.jpg']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    @pytest.mark.integration
    def test_cli_output_format_text(self, temp_image_file, mock_env_api_key, mock_gemini_model, capsys):
        """Test CLI text output format."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from main import main
                
                test_args = ['main.py', '--image', temp_image_file, '--format', 'text']
                with patch.object(sys, 'argv', test_args):
                    try:
                        main()
                        captured = capsys.readouterr()
                        assert "DATA KTP" in captured.out or "NIK" in captured.out
                    except SystemExit:
                        pass
    
    @pytest.mark.integration
    def test_cli_save_to_file(self, temp_image_file, mock_env_api_key, mock_gemini_model, tmp_path):
        """Test CLI saving output to file."""
        output_file = tmp_path / "output.json"
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from main import main
                
                test_args = ['main.py', '--image', temp_image_file, '--output', str(output_file)]
                with patch.object(sys, 'argv', test_args):
                    try:
                        main()
                        
                        # Check output file was created
                        if output_file.exists():
                            content = json.loads(output_file.read_text())
                            assert "nik" in content
                    except SystemExit:
                        pass


class TestOCRWorkflow:
    """Integration tests for complete OCR workflow."""
    
    @pytest.mark.integration
    def test_complete_ocr_workflow(self, mock_env_api_key, mock_gemini_model, temp_image_file):
        """Test complete OCR workflow from image to JSON."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from src.ocr_ktp import OCRKtp
                from src.utils import validate_image, format_ktp_data
                
                # Step 1: Validate image
                is_valid, message = validate_image(temp_image_file)
                assert is_valid is True
                
                # Step 2: Extract data
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                assert result["success"] is True
                
                # Step 3: Format output
                formatted = format_ktp_data(result["data"])
                assert "DATA KTP" in formatted
    
    @pytest.mark.integration
    def test_workflow_with_non_ktp_image(self, mock_env_api_key, mock_gemini_model_non_ktp, temp_image_file):
        """Test workflow rejects non-KTP images."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model_non_ktp):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                
                assert result["success"] is False
                assert "bukan KTP" in result["error"]
    
    @pytest.mark.integration
    def test_workflow_with_bytes_input(self, mock_env_api_key, mock_gemini_model, sample_image_bytes):
        """Test OCR workflow with bytes input (for web upload)."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract_from_bytes(sample_image_bytes)
                
                assert result["success"] is True
                assert result["data"]["nik"] == "3201234567890001"


class TestErrorHandling:
    """Integration tests for error handling."""
    
    @pytest.mark.integration
    def test_graceful_api_error_handling(self, mock_env_api_key, temp_image_file):
        """Test graceful handling of API errors."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Network error")
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                
                assert result["success"] is False
                assert "Network error" in result["error"]
    
    @pytest.mark.integration
    def test_invalid_json_response_handling(self, mock_env_api_key, temp_image_file):
        """Test handling of invalid JSON response from API."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON at all"
        mock_model.generate_content.return_value = mock_response
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                
                # Should handle gracefully - either success with error in data, or failure
                if result["success"]:
                    assert "_parse_error" in result["data"]
                else:
                    assert "error" in result


class TestDataIntegrity:
    """Integration tests for data integrity."""
    
    @pytest.mark.integration
    def test_all_ktp_fields_preserved(self, mock_env_api_key, mock_gemini_model, temp_image_file):
        """Test that all KTP fields are preserved through the workflow."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                
                expected_fields = [
                    "nik", "nama", "tempat_lahir", "tanggal_lahir",
                    "jenis_kelamin", "alamat", "rt_rw", "kelurahan_desa",
                    "kecamatan", "agama", "status_perkawinan",
                    "pekerjaan", "kewarganegaraan", "berlaku_hingga"
                ]
                
                for field in expected_fields:
                    assert field in result["data"], f"Missing field: {field}"
    
    @pytest.mark.integration
    def test_nik_format_validation(self, mock_env_api_key, mock_gemini_model, temp_image_file):
        """Test that NIK is in correct format (16 digits)."""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                from src.ocr_ktp import OCRKtp
                
                ocr = OCRKtp()
                result = ocr.extract(temp_image_file)
                
                nik = result["data"]["nik"]
                assert len(nik) == 16
                assert nik.isdigit()
