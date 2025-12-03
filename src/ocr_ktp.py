"""
OCR KTP Module using Google Gemini Flash
"""
import os
import json
import re
from typing import Optional, Dict, Any
from PIL import Image

import google.generativeai as genai
from dotenv import load_dotenv


class OCRKtp:
    """
    OCR KTP class for extracting data from Indonesian ID Card (KTP) images.
    """
    
    # Prompt for Gemini to extract KTP data
    EXTRACTION_PROMPT = """Anda adalah asisten OCR yang sangat akurat. Ekstrak semua informasi dari gambar KTP Indonesia ini.

Berikan output dalam format JSON dengan struktur berikut:
{
  "is_ktp": true/false,
  "nik": "",
  "nama": "",
  "tempat_lahir": "",
  "tanggal_lahir": "",
  "jenis_kelamin": "",
  "alamat": "",
  "rt_rw": "",
  "kelurahan_desa": "",
  "kecamatan": "",
  "agama": "",
  "status_perkawinan": "",
  "pekerjaan": "",
  "kewarganegaraan": "",
  "berlaku_hingga": ""
}

Pastikan:
1. PERTAMA, periksa apakah gambar ini adalah KTP Indonesia yang valid. Set "is_ktp" = true jika ini adalah KTP, false jika bukan KTP (misalnya: SIM, Paspor, foto selfie, gambar random, dll)
2. Jika bukan KTP (is_ktp = false), isi semua field lainnya dengan null
3. NIK harus 16 digit angka
4. Tanggal dalam format DD-MM-YYYY
5. Jika ada field yang tidak terbaca, isi dengan null
6. Hanya berikan JSON, tanpa penjelasan tambahan
7. Pastikan JSON valid dan dapat di-parse"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OCR KTP with Gemini API.
        
        Args:
            api_key: Gemini API key. If not provided, will try to load from environment.
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API Key tidak ditemukan. "
                "Silakan set GEMINI_API_KEY di file .env atau berikan sebagai parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model (Gemini 2.0 Flash)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract(self, image_source) -> Dict[str, Any]:
        """
        Extract KTP data from image.
        
        Args:
            image_source: Can be a file path (str) or PIL Image object
            
        Returns:
            Dictionary containing extracted KTP data
        """
        # Load image if path is provided
        if isinstance(image_source, str):
            image = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            image = image_source
        else:
            raise ValueError("image_source harus berupa path file atau PIL Image object")
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        try:
            # Generate content using Gemini
            response = self.model.generate_content([self.EXTRACTION_PROMPT, image])
            
            # Parse response
            result = self._parse_response(response.text)
            
            # Check if the image is a valid KTP
            if not result.get("is_ktp", False):
                return {
                    "success": False,
                    "error": "Gambar yang diupload bukan KTP Indonesia. Silakan upload gambar KTP yang valid.",
                    "data": None,
                    "is_ktp": False
                }
            
            # Remove is_ktp from final data
            result.pop("is_ktp", None)
            
            return {
                "success": True,
                "data": result,
                "raw_response": response.text,
                "is_ktp": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini response to extract JSON data.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Parsed dictionary containing KTP data
        """
        # Try to find JSON in the response
        # Sometimes Gemini wraps JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to parse the entire response as JSON
            json_str = response_text.strip()
        
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty structure with error
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
                "berlaku_hingga": None,
                "_parse_error": "Gagal parsing JSON dari response"
            }
    
    def extract_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract KTP data from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary containing extracted KTP data
        """
        from io import BytesIO
        image = Image.open(BytesIO(image_bytes))
        return self.extract(image)
