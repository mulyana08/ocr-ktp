#!/usr/bin/env python3
"""
OCR KTP - Command Line Interface
Extract data from Indonesian ID Card (KTP) using Google Gemini Flash
"""
import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ocr_ktp import OCRKtp
from src.utils import validate_image, format_ktp_data


def main():
    parser = argparse.ArgumentParser(
        description="OCR KTP - Ekstrak data dari gambar KTP Indonesia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python main.py --image samples/ktp.jpg
  python main.py --image samples/ktp.jpg --output hasil.json
  python main.py --image samples/ktp.jpg --format json
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Path ke file gambar KTP"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Path untuk menyimpan hasil (format JSON)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="text",
        help="Format output: json atau text (default: text)"
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API Key (opsional jika sudah di set di .env)"
    )
    
    args = parser.parse_args()
    
    # Validate image
    print(f"🔍 Memeriksa gambar: {args.image}")
    is_valid, message = validate_image(args.image)
    
    if not is_valid:
        print(f"❌ Error: {message}")
        sys.exit(1)
    
    print(f"✅ {message}")
    
    # Initialize OCR
    try:
        print("🚀 Menginisialisasi OCR KTP...")
        ocr = OCRKtp(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Extract data
    print("📷 Mengekstrak data dari KTP...")
    result = ocr.extract(args.image)
    
    if not result["success"]:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    print("✅ Ekstraksi berhasil!")
    
    # Output result
    if args.format == "json":
        output = json.dumps(result["data"], indent=2, ensure_ascii=False)
        print("\n" + output)
    else:
        print("\n" + format_ktp_data(result["data"]))
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result["data"], f, indent=2, ensure_ascii=False)
        print(f"\n💾 Hasil disimpan ke: {args.output}")


if __name__ == "__main__":
    main()
