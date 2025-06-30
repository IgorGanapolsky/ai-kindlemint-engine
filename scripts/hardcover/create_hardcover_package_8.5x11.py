#!/usr/bin/env python3
"""
Hardcover Production System for 8.5x11 inch books
Creates complete hardcover publishing packages for Large Print books
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


class HardcoverProducer8x11:
    """Automated hardcover production for 8.5x11 books"""

    def __init__(self, book_config):
        self.config = book_config

        # Calculate spine width: (pages × 0.0025) + 0.06
        self.spine_width = (self.config["pages"] * 0.0025) + 0.06

        # For 8.5x11 book with case laminate
        # Width = 0.125 (bleed) + 8.5 (back) + spine + 8.5 (front) + 0.125 (bleed) + 1.5 (wrap)
        self.template_width_inches = 0.125 + 8.5 + self.spine_width + 8.5 + 0.125 + 1.5
        self.template_height_inches = 11.25  # 11 + 0.125 + 0.125 bleed

        # Convert to pixels at 300 DPI
        self.template_width = int(self.template_width_inches * 300)
        self.template_height = int(self.template_height_inches * 300)

    def create_directory_structure(self):
        """Create hardcover production directories"""
        # Navigate to book directory
        config_path = Path(sys.argv[1])
        book_dir = config_path.parent
        hardcover_dir = book_dir / self.config["output_dir"]
        hardcover_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Created hardcover directory: {hardcover_dir}")
        return hardcover_dir

    def generate_metadata(self, output_dir):
        """Generate KDP metadata for hardcover edition"""
        metadata = {
            "title": self.config["title"],
            "subtitle": self.config["subtitle"],
            "series": "Large Print Crossword Masters",
            "series_number": "2",
            "author": self.config["author"],
            "publisher": self.config["publisher"],
            "description": self.config["description"],
            "keywords": [
                "hardcover crossword puzzle book",
                "large print crossword puzzles volume 2",
                "premium puzzle book gift",
                "crossword masters hardcover",
                "brain games for seniors hardcover",
                "collectible puzzle books",
                "crossword book series",
            ],
            "categories": [
                "Books > Humor & Entertainment > Puzzles & Games > Crossword Puzzles",
                "Books > Health, Fitness & Dieting > Aging",
                "Books > Self-Help > Memory Improvement",
            ],
            "language": "English",
            "pages": self.config["pages"],
            "format": "Hardcover - Case Laminate",
            "dimensions": f"{self.config['trim_size']} inches",
            "spine_width": f"{self.spine_width:.3f} inches",
            "list_price": self.config["pricing"]["list_price"],
            "publication_date": datetime.now().strftime("%Y-%m-%d"),
            "target_audience": "Adults 50+, Gift buyers, Puzzle collectors",
        }

        with open(output_dir / "amazon_kdp_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        print("📝 Created KDP metadata file")

    def create_production_checklist(self, output_dir):
        """Create detailed production checklist"""
        checklist = f"""# Hardcover Production Checklist - {self.config['title']}

## Book Specifications
- **Title**: {self.config['title']}
- **Subtitle**: {self.config['subtitle']}
- **Author**: {self.config['author']}
- **Pages**: {self.config['pages']}
- **Trim Size**: {self.config['trim_size']} inches
- **Spine Width**: {self.spine_width:.3f} inches
- **Format**: Hardcover - Case Laminate

## Cover Wrap Dimensions
- **Total Width**: {self.template_width_inches:.3f} inches ({self.template_width} pixels)
- **Total Height**: {self.template_height_inches:.3f} inches ({self.template_height} pixels)
- **DPI**: 300
- **Color Mode**: CMYK for print

## Cover Wrap Layout (Left to Right)
1. **Back Cover**: 8.5" × 11"
2. **Spine**: {self.spine_width:.3f}" × 11"
3. **Front Cover**: 8.5" × 11"
4. **Wrap Coverage**: 1.5" (extends around to inside)

## Bleed Specifications
- **Top/Bottom**: 0.125 inches
- **Left/Right**: 0.125 inches
- **Total Bleed Area**: Included in dimensions above

## Pricing Strategy
- **List Price**: {self.config['pricing']['list_price']}
- **Printing Cost**: {self.config['pricing']['printing_cost']}
- **Expected Royalty**: {self.config['pricing']['expected_royalty']}

## Production Steps
1. [ ] Create cover wrap design at exact dimensions
2. [ ] Add spine text (title + author) - vertically centered
3. [ ] Include barcode area on back cover (2" × 1.2")
4. [ ] Convert to CMYK color mode
5. [ ] Export as PDF/X-1a for print
6. [ ] Verify all text is at least 0.125" from trim edges
7. [ ] Upload to KDP and order proof copy

## Quality Control
- [ ] Spine text readable and properly oriented
- [ ] All images at 300 DPI or higher
- [ ] No text in bleed areas
- [ ] Colors adjusted for CMYK printing
- [ ] File size under 650 MB
"""

        with open(output_dir / "hardcover_production_checklist.md", "w") as f:
            f.write(checklist)
        print("📋 Created production checklist")

    def create_design_brief(self, output_dir):
        """Create cover wrap design brief"""
        brief = f"""# Hardcover Cover Wrap Design Brief

## Project: {self.config['title']} - Volume 2

### Dimensions
- **Trim Size**: 8.5" × 11"
- **Cover Wrap**: {self.template_width_inches:.3f}" × {self.template_height_inches:.3f}" at 300 DPI
- **Spine Width**: {self.spine_width:.3f} inches

### Layout Specifications

#### Front Cover (Right Side)
- Replicate paperback cover design
- Navy blue background (#2C3E50)
- Large white serif title text
- Gold "VOLUME 2" diagonal banner
- Centered subtitle on gold band

#### Spine
- Width: {self.spine_width:.3f} inches
- Text orientation: Bottom to top (readable when book lies face-up)
- Content:
  - Title: "LARGE PRINT CROSSWORD MASTERS"
  - Volume: "VOLUME 2"
  - Author: "CROSSWORD MASTERS PUBLISHING"
- White text on navy background
- Maintain 0.125" margins from edges

#### Back Cover (Left Side)
- Navy blue background matching front
- Book description (provided in metadata)
- Barcode area: 2" × 1.2" in bottom right
- Publisher information at bottom

### Technical Requirements
- **Resolution**: 300 DPI
- **Color Mode**: CMYK
- **File Format**: PDF/X-1a
- **Fonts**: Embed all fonts
- **Images**: Flatten all layers

### Brand Guidelines
- Primary: Navy Blue #2C3E50
- Accent: Gold #F39C12
- Text: White #FFFFFF
- Maintain consistent typography with Volume 1
"""

        with open(output_dir / "cover_wrap_design_brief.md", "w") as f:
            f.write(brief)
        print("🎨 Created design brief")

    def create_cover_wrap_template(self, output_dir):
        """Create cover wrap with template overlay"""
        # Create base image
        img = Image.new(
            "CMYK", (self.template_width, self.template_height), (100, 100, 100, 0)
        )
        draw = ImageDraw.Draw(img)

        # Calculate positions
        bleed = int(0.125 * 300)
        back_width = int(8.5 * 300)
        spine_width_px = int(self.spine_width * 300)
        front_width = int(8.5 * 300)
        wrap_width = int(1.5 * 300)

        # Draw template guides
        # Back cover
        draw.rectangle(
            [bleed, bleed, bleed + back_width, self.template_height - bleed],
            outline=(0, 0, 0, 100),
            width=3,
        )
        draw.text(
            (bleed + 50, self.template_height // 2), "BACK COVER", fill=(0, 0, 0, 100)
        )

        # Spine
        spine_x = bleed + back_width
        draw.rectangle(
            [spine_x, bleed, spine_x + spine_width_px, self.template_height - bleed],
            outline=(0, 0, 0, 100),
            width=3,
        )
        draw.text(
            (spine_x + 10, self.template_height // 2), "SPINE", fill=(0, 0, 0, 100)
        )

        # Front cover
        front_x = spine_x + spine_width_px
        draw.rectangle(
            [front_x, bleed, front_x + front_width, self.template_height - bleed],
            outline=(0, 0, 0, 100),
            width=3,
        )
        draw.text(
            (front_x + 50, self.template_height // 2),
            "FRONT COVER",
            fill=(0, 0, 0, 100),
        )

        # Wrap area
        wrap_x = front_x + front_width
        draw.rectangle(
            [wrap_x, bleed, wrap_x + wrap_width - bleed, self.template_height - bleed],
            outline=(100, 0, 100, 0),
            width=2,
        )
        draw.text(
            (wrap_x + 20, self.template_height // 2), "WRAP", fill=(100, 0, 100, 0)
        )

        # Save template
        template_path = output_dir / "hardcover_template_guide.jpg"
        img.convert("RGB").save(template_path, "JPEG")
        print("📐 Created template guide")

        # Create actual cover wrap
        self.create_actual_cover_wrap(output_dir, spine_width_px)

    def create_actual_cover_wrap(self, output_dir, spine_width_px):
        """Create the actual hardcover wrap design"""
        # Create CMYK image
        img = Image.new(
            "CMYK", (self.template_width, self.template_height), (80, 50, 30, 0)
        )
        draw = ImageDraw.Draw(img)

        # Get source cover
        config_path = Path(sys.argv[1])
        book_dir = config_path.parent
        cover_source = book_dir / self.config["cover_source"]

        if cover_source.exists():
            # Load and place front cover
            source_img = Image.open(cover_source).convert("CMYK")
            # Resize to fit front cover area
            front_width = int(8.5 * 300)
            front_height = int(11 * 300)
            source_img = source_img.resize(
                (front_width, front_height), Image.Resampling.LANCZOS
            )

            # Place on right side (front cover position)
            bleed = int(0.125 * 300)
            back_width = int(8.5 * 300)
            front_x = bleed + back_width + spine_width_px
            front_y = bleed

            img.paste(source_img, (front_x, front_y))

            # Add spine text
            bleed + back_width
            # Note: Real implementation would rotate text 90 degrees

            # Add back cover - simple navy background with description
            draw.rectangle(
                [bleed, bleed, bleed + back_width, self.template_height - bleed],
                fill=(80, 50, 30, 0),
            )

        # Save files
        final_path = output_dir / "hardcover_cover_wrap_final.jpg"
        img.convert("RGB").save(final_path, "JPEG", quality=95)

        # Also save as PDF-ready CMYK
        pdf_path = output_dir / "hardcover_cover_wrap.pdf"
        img.save(pdf_path, "PDF", resolution=300.0)

        print("✅ Created hardcover cover wrap")
        print(f"📄 Final cover wrap: {final_path}")
        print(f"📄 PDF version: {pdf_path}")

    def copy_source_cover(self, output_dir):
        """Copy source cover for reference"""
        config_path = Path(sys.argv[1])
        book_dir = config_path.parent
        cover_source = book_dir / self.config["cover_source"]

        if cover_source.exists():
            dest = output_dir / f"cover_source_{cover_source.name}"
            shutil.copy(cover_source, dest)
            print(f"📋 Copied source cover: {dest.name}")

    def run(self):
        """Execute complete hardcover production"""
        print(f"🏭 Creating hardcover package for: {self.config['title']}")
        print(f"📐 Spine width: {self.spine_width:.4f} inches")

        # Create directories
        output_dir = self.create_directory_structure()

        # Generate all files
        self.generate_metadata(output_dir)
        self.create_production_checklist(output_dir)
        self.create_design_brief(output_dir)
        self.create_cover_wrap_template(output_dir)
        self.copy_source_cover(output_dir)

        print("\n✅ Hardcover package complete!")
        print(f"📁 Output location: {output_dir}")
        print("\n📋 Next steps:")
        print("1. Review the design brief and checklist")
        print("2. Create final artwork using the template guide")
        print("3. Export as PDF/X-1a with CMYK colors")
        print("4. Upload to KDP for hardcover edition")


def main():
    parser = argparse.ArgumentParser(description="Create hardcover publishing package")
    parser.add_argument("config_file", help="Path to book configuration JSON file")
    args = parser.parse_args()

    # Load configuration
    config_path = Path(args.config_file)
    if not config_path.exists():
        print(f"❌ Error: Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        book_config = json.load(f)

    # Create hardcover package
    producer = HardcoverProducer8x11(book_config)
    producer.run()


if __name__ == "__main__":
    main()
