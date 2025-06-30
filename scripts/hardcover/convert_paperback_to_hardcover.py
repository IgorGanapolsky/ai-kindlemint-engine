#!/usr/bin/env python3
"""
Paperback to Hardcover PDF Converter
Converts 8.5×11 paperback PDFs to 6×9 hardcover format while maintaining readability
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF


class PaperbackToHardcoverConverter:
    """Converts paperback PDFs to hardcover format"""

    def __init__(self):
        # Source dimensions (8.5×11 inches in points)
        self.source_width = 8.5 * 72
        self.source_height = 11 * 72

        # Target dimensions (6×9 inches in points)
        self.target_width = 6 * 72
        self.target_height = 9 * 72

        # Calculate scaling factors
        self.width_scale = self.target_width / self.source_width
        self.height_scale = self.target_height / self.source_height

        # Use the smaller scale to maintain aspect ratio and avoid cropping
        self.scale_factor = min(self.width_scale, self.height_scale)

        print(f"📐 Conversion parameters:")
        print(
            f"   Source: 8.5×11 inches ({
                self.source_width:.0f}×{
                self.source_height:.0f} points)"
        )
        print(
            f"   Target: 6×9 inches ({
                self.target_width:.0f}×{
                self.target_height:.0f} points)"
        )
        print(f"   Scale factor: {self.scale_factor:.3f}")

    def convert_pdf(self, input_path, output_path):
        """Convert paperback PDF to hardcover format"""

        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        print(f"📖 Converting: {input_file.name}")
        print(f"📄 Output: {output_file}")

        try:
            # Open source PDF
            source_doc = fitz.open(input_file)
            page_count = len(source_doc)
            print(f"📚 Processing {page_count} pages...")

            # Create new PDF with target dimensions
            output_doc = fitz.open()  # Create empty PDF

            for page_num in range(page_count):
                source_page = source_doc[page_num]

                # Create new page with target dimensions
                new_page = output_doc.new_page(
                    width=self.target_width, height=self.target_height
                )

                # Get source page as image at high resolution for quality
                mat = fitz.Matrix(2.0, 2.0)  # 2x resolution for quality
                pix = source_page.get_pixmap(matrix=mat)

                # Calculate positioning to center the scaled content
                scaled_width = self.source_width * self.scale_factor
                scaled_height = self.source_height * self.scale_factor

                x_offset = (self.target_width - scaled_width) / 2
                y_offset = (self.target_height - scaled_height) / 2

                # Create rectangle for image placement
                rect = fitz.Rect(
                    x_offset,
                    y_offset,
                    x_offset + scaled_width,
                    y_offset + scaled_height,
                )

                # Insert scaled image
                new_page.insert_image(rect, pixmap=pix)

                if (page_num + 1) % 10 == 0:
                    print(f"   ✅ Processed {page_num + 1} pages...")

            # Save converted PDF
            output_doc.save(output_file)
            output_doc.close()
            source_doc.close()

            # Verify output
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Conversion complete!")
            print(f"📊 Output file: {output_file}")
            print(f"📏 Pages: {page_count}")
            print(f"📁 File size: {file_size:.1f} MB")

            # Quality check
            if file_size > 650:
                print("⚠️  Warning: File size exceeds KDP limit (650 MB)")
            else:
                print("✅ File size within KDP limits")

            return True

        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            return False

    def convert_with_text_preservation(self, input_path, output_path):
        """Alternative conversion method that preserves text selectability"""

        input_file = Path(input_path)
        output_file = Path(output_path)

        print(f"📖 Converting with text preservation: {input_file.name}")

        try:
            # Open source PDF
            source_doc = fitz.open(input_file)
            page_count = len(source_doc)

            # Create new document
            output_doc = fitz.open()

            for page_num in range(page_count):
                source_doc[page_num]

                # Create new page
                new_page = output_doc.new_page(
                    width=self.target_width, height=self.target_height
                )

                # Calculate transformation matrix for scaling and centering
                scaled_width = self.source_width * self.scale_factor
                scaled_height = self.source_height * self.scale_factor

                x_offset = (self.target_width - scaled_width) / 2
                y_offset = (self.target_height - scaled_height) / 2

                # Create transformation matrix
                mat = fitz.Matrix(self.scale_factor, self.scale_factor)
                mat = mat.pretranslate(x_offset, y_offset)

                # Copy page content with transformation
                new_page.show_pdf_page(new_page.rect, source_doc, page_num, clip=None)

                if (page_num + 1) % 10 == 0:
                    print(f"   ✅ Processed {page_num + 1} pages...")

            # Save with optimization
            output_doc.save(output_file, garbage=4, deflate=True)
            output_doc.close()
            source_doc.close()

            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"✅ Text-preserving conversion complete!")
            print(f"📁 File size: {file_size:.1f} MB")

            return True

        except Exception as e:
            print(f"❌ Text-preserving conversion failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert paperback PDF to hardcover format"
    )
    parser.add_argument("input", help="Input paperback PDF file")
    parser.add_argument("output", help="Output hardcover PDF file")
    parser.add_argument(
        "--preserve-text",
        action="store_true",
        help="Use text preservation method (may produce larger files)",
    )

    args = parser.parse_args()

    converter = PaperbackToHardcoverConverter()

    if args.preserve_text:
        success = converter.convert_with_text_preservation(args.input, args.output)
    else:
        success = converter.convert_pdf(args.input, args.output)

    if success:
        print("\n🎯 Ready for KDP hardcover upload!")
        print("📋 Next steps:")
        print("   1. Upload the converted PDF as manuscript")
        print("   2. Upload the hardcover_cover_wrap.pdf as cover")
        print("   3. Review and publish")
    else:
        print("\n❌ Conversion failed - check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
