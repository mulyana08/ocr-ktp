"""
Utility functions for OCR KTP
"""
import os
from PIL import Image
from typing import Tuple, Optional


# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_image(image_path: str) -> Tuple[bool, str]:
    """
    Validate image file before processing.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check if file exists
    if not os.path.exists(image_path):
        return False, f"File tidak ditemukan: {image_path}"
    
    # Check file extension
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"Format file tidak didukung: {ext}. Format yang didukung: {', '.join(SUPPORTED_FORMATS)}"
    
    # Check file size
    file_size = os.path.getsize(image_path)
    if file_size > MAX_FILE_SIZE:
        return False, f"Ukuran file terlalu besar: {file_size / 1024 / 1024:.2f}MB. Maksimum: {MAX_FILE_SIZE / 1024 / 1024}MB"
    
    # Try to open the image
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        return False, f"File gambar tidak valid: {str(e)}"
    
    return True, "Gambar valid"


def load_image(image_path: str) -> Optional[Image.Image]:
    """
    Load and return PIL Image object.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image object or None if failed
    """
    try:
        image = Image.open(image_path)
        # Convert to RGB if necessary (for RGBA or P mode images)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        return image
    except Exception as e:
        print(f"Error loading image: {str(e)}")
        return None


def format_ktp_data(data: dict) -> str:
    """
    Format KTP data for display.
    
    Args:
        data: Dictionary containing KTP data
        
    Returns:
        Formatted string for display
    """
    output = []
    output.append("=" * 50)
    output.append("         DATA KTP")
    output.append("=" * 50)
    
    fields = [
        ("NIK", "nik"),
        ("Nama", "nama"),
        ("Tempat Lahir", "tempat_lahir"),
        ("Tanggal Lahir", "tanggal_lahir"),
        ("Jenis Kelamin", "jenis_kelamin"),
        ("Alamat", "alamat"),
        ("RT/RW", "rt_rw"),
        ("Kel/Desa", "kelurahan_desa"),
        ("Kecamatan", "kecamatan"),
        ("Agama", "agama"),
        ("Status Perkawinan", "status_perkawinan"),
        ("Pekerjaan", "pekerjaan"),
        ("Kewarganegaraan", "kewarganegaraan"),
        ("Berlaku Hingga", "berlaku_hingga"),
    ]
    
    for label, key in fields:
        value = data.get(key, "-") or "-"
        output.append(f"{label:<20}: {value}")
    
    output.append("=" * 50)
    
    return "\n".join(output)
