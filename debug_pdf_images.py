#!/usr/bin/env python3
"""
Debug tool to extract and examine images from PDF pages
"""

import sys
from pathlib import Path

import fitz


def extract_page_images(pdf_path, page_num, output_dir):
    """Extract all images from a specific PDF page"""
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]

    print(f"🔍 Extracting images from page {page_num + 1}...")

    image_list = page.get_images()
    print(f"Found {len(image_list)} images on page {page_num + 1}")

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for img_index, img in enumerate(image_list):
        # Extract image
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        # Save image
        img_filename = f"page_{page_num+1}_image_{img_index+1}.png"
        img_path = output_dir / img_filename

        if pix.n - pix.alpha < 4:  # GRAY or RGB
            pix.save(str(img_path))
            print(f"✅ Saved: {img_path}")
            print(f"   Size: {pix.width}x{pix.height}")
        else:  # CMYK: convert to RGB
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pix1.save(str(img_path))
            pix1 = None
            print(f"✅ Saved (converted): {img_path}")
            print(f"   Size: {pix.width}x{pix.height}")

        pix = None

    doc.close()


def main():
    if len(sys.argv) != 4:
        print("Usage: python debug_pdf_images.py <pdf_path> <page_number> <output_dir>")
        print("Note: page_number is 1-based (page 1 = first page)")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    page_num = int(sys.argv[2]) - 1  # Convert to 0-based
    output_dir = sys.argv[3]

    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    extract_page_images(pdf_path, page_num, output_dir)


if __name__ == "__main__":
    main()
