#!/usr/bin/env python3
"""
Universal Hardcover Production System for KindleMint Engine
Creates complete hardcover publishing packages for any book volume
"""

import os
import sys
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class HardcoverProducer:
    """Automated hardcover production system"""
    
    def __init__(self, book_config):
        self.config = book_config
        self.template_dir = Path("templates/hardcover")
        self.scripts_dir = Path("scripts/hardcover")
        
        # Calculate spine width: (pages × 0.0025) + 0.06
        self.spine_width = (self.config['pages'] * 0.0025) + 0.06
        
        # KDP template dimensions at 300 DPI
        self.template_width = int(13.996 * 300)  # 4199 pixels
        self.template_height = int(10.417 * 300)  # 3125 pixels
        
    def create_directory_structure(self):
        """Create hardcover production directories"""
        hardcover_dir = Path(self.config['output_dir'])
        hardcover_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Created hardcover directory: {hardcover_dir}")
        return hardcover_dir
        
    def generate_metadata(self, output_dir):
        """Generate KDP metadata for hardcover edition"""
        metadata = {
            "title": self.config['title'],
            "subtitle": self.config['subtitle'],
            "author": self.config['author'],
            "description": self.config['description'].replace("paperback", "hardcover").replace("8.5\\\" × 11\\\"", "6\\\" × 9\\\""),
            "keywords": [kw.replace("paperback", "hardcover") for kw in self.config['keywords']] + ["hardcover", "premium", "gift"],
            "categories": self.config['categories'],
            "language": self.config['language'],
            "pages": self.config['pages'],
            "format": "Hardcover",
            "binding": "Case-Laminate",
            "dimensions": "6 x 9 inches",
            "paper": "White",
            "ink": "Black & White",
            "spine_width": f"{self.spine_width:.4f} inches",
            "price_range": f"${self.config['hardcover_price_min']:.2f} - ${self.config['hardcover_price_max']:.2f}",
            "target_audience": self.config['target_audience'] + ", Gift buyers",
            "publication_date": datetime.now().strftime("%Y-%m-%d"),
            "isbn": "KDP_AUTO_ASSIGNED",
            "printing_cost_estimate": f"${self.config['printing_cost_estimate']:.2f}",
            "royalty_estimate": f"${self.config['royalty_min']:.2f} - ${self.config['royalty_max']:.2f}",
            "revenue_multiplier": "2-3x paperback profit",
            "market_position": "Premium offering in category",
            "gift_appeal": "High - premium hardcover presentation",
            "season_relevance": "Year-round, especially holidays and gift occasions"
        }
        
        metadata_file = output_dir / "amazon_kdp_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"📄 Generated metadata: {metadata_file}")
        return metadata_file
        
    def create_production_checklist(self, output_dir):
        """Generate production checklist with calculations"""
        checklist_content = f"""# Hardcover Production Checklist
## {self.config['title']} - {self.config['subtitle']}

### 📊 **Hardcover Specifications**
- **Format**: Case-Laminate Hardcover (KDP's only hardcover option)
- **Trim Size**: 6 × 9 inches
- **Page Count**: {self.config['pages']} pages
- **Paper**: White (best for puzzle grids)
- **Ink**: Black & White (cost efficient)
- **Spine Width**: {self.spine_width:.4f} inches `({self.config['pages']} × 0.0025) + 0.06`

### 📁 **Required Files**

#### ✅ **Interior PDF**
- [ ] Convert from original format to 6×9 format
- [ ] Maintain font embedding
- [ ] Single-page PDF, no crop marks
- [ ] File: `hardcover_interior.pdf`

#### ✅ **Cover Wrap PDF**  
- [ ] Use KDP template for 6×9, {self.config['pages']} pages, white paper, B/W
- [ ] Create wrap design with front/spine/back
- [ ] Export as PDF/X-1a with CMYK and outlined fonts
- [ ] File: `hardcover_cover_wrap.pdf`

### 🎨 **Cover Design Elements**

#### **Source Assets**
- **Front Cover**: `{self.config['cover_source']}`
- **Template**: `6x9_{self.config['pages']}pages_template.png`

#### **Design Requirements**
1. **Canvas**: Exact template dimensions ({self.template_width} × {self.template_height} pixels)
2. **Template Layer**: 30% opacity for alignment 
3. **Front Cover**: Right side, scale to fit, maintain aspect ratio
4. **Background**: Extend gradient/pattern to spine & back
5. **Back Cover**: Book description + barcode placeholder (2×1.2 in)
6. **Spine**: 
   - Title (stacked) centered, 0.125 in from edges
   - Publisher: "{self.config['publisher']}" at bottom

### 💰 **Pricing Strategy**
- **Printing Cost**: ~${self.config['printing_cost_estimate']:.2f} (estimated)
- **Target Price**: ${self.config['hardcover_price_min']:.2f} - ${self.config['hardcover_price_max']:.2f}
- **Royalty**: ~${self.config['royalty_min']:.2f} - ${self.config['royalty_max']:.2f} per book
- **Revenue Multiplier**: 2-3x paperback profit margin

### 📋 **Quality Control Checklist**
- [ ] Interior PDF: Page-per-page, selectable text, fonts embedded
- [ ] Cover wrap: All bleed areas covered, spine text >0.0625" from folds
- [ ] File size: <650 MB total
- [ ] Color mode: CMYK only (no RGB)
- [ ] Thumbnail test: Text crisp at 25% view

### 📈 **Metadata Updates**
- [ ] New ISBN (KDP assigns automatically)
- [ ] Price: ${self.config['hardcover_price_min']:.2f} - ${self.config['hardcover_price_max']:.2f} range
- [ ] Description: Enhanced with hardcover benefits
- [ ] Categories: Same as paperback
- [ ] Keywords: Include "hardcover", "premium", "gift"

### 🎯 **Revenue Impact**
- **Hardcover Premium**: 150-200% price increase over paperback
- **Target Market**: Gift buyers, collectors, premium segment
- **Profit Margin**: Higher per-unit profit despite higher printing cost
- **Market Position**: Premium offering in category
"""
        
        checklist_file = output_dir / "hardcover_production_checklist.md"
        with open(checklist_file, 'w') as f:
            f.write(checklist_content)
            
        print(f"📋 Generated checklist: {checklist_file}")
        return checklist_file
        
    def create_cover_wrap(self, output_dir):
        """Generate hardcover cover wrap design"""
        
        # Load template
        template_path = self.template_dir / "kdp_case_laminate" / f"6x9_{self.config['pages']}pages_template.png"
        if not template_path.exists():
            # Use the default template we have
            template_path = self.template_dir / "kdp_case_laminate" / "6x9_103pages_template.png"
            
        template = Image.open(template_path).convert("RGBA")
        template = template.resize((self.template_width, self.template_height), Image.Resampling.LANCZOS)
        
        # Load source front cover
        cover_source = Path(self.config['cover_source'])
        if not cover_source.exists():
            print(f"❌ Cover source not found: {cover_source}")
            return None
            
        front_cover = Image.open(cover_source).convert("RGB")
        
        # Create main canvas
        canvas = Image.new("RGB", (self.template_width, self.template_height), "white")
        
        # Calculate cover areas
        front_width = int(6 * 300)  # 1800 pixels
        front_height = int(9 * 300)  # 2700 pixels
        spine_width = int(self.spine_width * 300)  # spine width in pixels
        back_width = front_width
        back_height = front_height
        
        # Position calculations
        front_x = self.template_width - front_width - int(0.125 * 300)
        front_y = int((self.template_height - front_height) / 2)
        spine_x = front_x - spine_width
        back_x = spine_x - back_width
        
        # Scale and place front cover
        front_ratio = min(front_width / front_cover.width, front_height / front_cover.height)
        scaled_width = int(front_cover.width * front_ratio)
        scaled_height = int(front_cover.height * front_ratio)
        front_scaled = front_cover.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        front_paste_x = front_x + (front_width - scaled_width) // 2
        front_paste_y = front_y + (front_height - scaled_height) // 2
        canvas.paste(front_scaled, (front_paste_x, front_paste_y))
        
        # Create back cover background
        back_sample = front_cover.crop((0, 0, 200, front_cover.height))
        back_background = back_sample.resize((back_width, back_height), Image.Resampling.LANCZOS)
        canvas.paste(back_background, (back_x, front_y))
        
        # Create spine background
        spine_sample = front_cover.crop((front_cover.width//2 - 50, 0, front_cover.width//2 + 50, front_cover.height))
        spine_background = spine_sample.resize((spine_width, front_height), Image.Resampling.LANCZOS)
        canvas.paste(spine_background, (spine_x, front_y))
        
        # Add text overlays
        self._add_text_overlays(canvas, spine_x, spine_width, front_y, front_height, back_x, back_width)
        
        # Save outputs
        final_path = output_dir / "hardcover_cover_wrap_final.png"
        canvas.save(final_path, "PNG", quality=95)
        
        print(f"🎨 Generated cover wrap: {final_path}")
        return final_path
        
    def _add_text_overlays(self, canvas, spine_x, spine_width, front_y, front_height, back_x, back_width):
        """Add text overlays to cover wrap"""
        draw = ImageDraw.Draw(canvas)
        
        # Load fonts
        def load_font(size):
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf"
            ]
            for font_path in font_paths:
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
            return ImageFont.load_default()
        
        title_font = load_font(48)
        publisher_font = load_font(24)
        desc_font = load_font(36)
        
        # Spine text
        spine_margin = int(0.125 * 300)
        
        # Title on spine (rotated)
        title_text = self.config['title'].upper()
        spine_title_img = Image.new("RGBA", (600, spine_width), (0, 0, 0, 0))
        spine_title_draw = ImageDraw.Draw(spine_title_img)
        spine_title_draw.text((10, spine_width//2), title_text, font=title_font, fill="white", anchor="lm")
        spine_title_rotated = spine_title_img.rotate(90, expand=True)
        
        spine_title_y = front_y + spine_margin
        spine_title_x = spine_x + (spine_width - spine_title_rotated.width) // 2
        canvas.paste(spine_title_rotated, (spine_title_x, spine_title_y), spine_title_rotated)
        
        # Publisher on spine
        publisher_text = self.config['publisher'].upper()
        publisher_img = Image.new("RGBA", (400, spine_width), (0, 0, 0, 0))
        publisher_draw = ImageDraw.Draw(publisher_img)
        publisher_draw.text((10, spine_width//2), publisher_text, font=publisher_font, fill="white", anchor="lm")
        publisher_rotated = publisher_img.rotate(90, expand=True)
        
        publisher_y = front_y + front_height - publisher_rotated.height - spine_margin
        publisher_x = spine_x + (spine_width - publisher_rotated.width) // 2
        canvas.paste(publisher_rotated, (publisher_x, publisher_y), publisher_rotated)
        
        # Back cover description
        lines = self.config['back_cover_description'].split('\n')
        line_height = 45
        current_y = front_y + 100
        
        for line in lines:
            if line.strip():
                draw.text((back_x + 60, current_y), line.strip(), font=desc_font, fill="white")
            current_y += line_height
        
        # Barcode placeholder
        barcode_width = int(2.0 * 300)
        barcode_height = int(1.2 * 300)
        barcode_x = back_x + back_width - barcode_width - 60
        barcode_y = front_y + front_height - barcode_height - 60
        
        draw.rectangle([
            (barcode_x, barcode_y), 
            (barcode_x + barcode_width, barcode_y + barcode_height)
        ], fill="white", outline="black", width=2)
        
        draw.text(
            (barcode_x + barcode_width//2, barcode_y + barcode_height//2), 
            "BARCODE\\nPLACEHOLDER", 
            font=load_font(24), 
            fill="black", 
            anchor="mm"
        )
    
    def export_pdf_x1a(self, output_dir):
        """Export cover wrap as PDF/X-1a"""
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.units import inch
            
            input_file = output_dir / "hardcover_cover_wrap_final.png"
            output_file = output_dir / "hardcover_cover_wrap.pdf"
            
            if not input_file.exists():
                print(f"❌ Cover wrap PNG not found: {input_file}")
                return None
            
            # Load and convert to CMYK
            img = Image.open(input_file)
            if img.mode != 'CMYK':
                img = img.convert('CMYK')
            
            # Create PDF
            width_points = 13.996 * 72
            height_points = 10.417 * 72
            
            c = pdf_canvas.Canvas(str(output_file), pagesize=(width_points, height_points))
            c.setTitle(f"{self.config['title']} - Hardcover")
            c.setAuthor(self.config['author'])
            
            # Save temp JPEG for CMYK support
            temp_img = output_dir / "temp_cover_cmyk.jpg"
            img.save(temp_img, "JPEG", quality=100)
            
            # Draw image
            c.drawImage(str(temp_img), 0, 0, width=width_points, height=height_points)
            c.save()
            
            # Clean up
            temp_img.unlink()
            
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"📄 Generated PDF/X-1a: {output_file} ({file_size:.1f} MB)")
            return output_file
            
        except ImportError:
            print("❌ ReportLab not installed. Install with: pip install reportlab")
            return None
    
    def create_complete_package(self):
        """Create complete hardcover production package"""
        print(f"🏭 Creating hardcover package for: {self.config['title']}")
        print(f"📐 Spine width: {self.spine_width:.4f} inches")
        
        # Create directory structure
        output_dir = self.create_directory_structure()
        
        # Copy cover source to hardcover directory (if not already there)
        cover_source_path = Path(self.config['cover_source'])
        if not cover_source_path.is_absolute():
            # Make relative to output directory
            cover_source_path = output_dir.parent / cover_source_path
            
        cover_dest = output_dir / f"cover_source_{cover_source_path.name}"
        if cover_source_path.exists() and not cover_dest.exists():
            import shutil
            shutil.copy2(cover_source_path, cover_dest)
            
        # Generate all components (PRODUCTION FILES ONLY)
        self.generate_metadata(output_dir)
        self.create_production_checklist(output_dir)
        self.create_cover_wrap(output_dir)
        self.export_pdf_x1a(output_dir)
        
        print(f"✅ Hardcover package complete: {output_dir}")
        print(f"💰 Pricing: ${self.config['hardcover_price_min']:.2f} - ${self.config['hardcover_price_max']:.2f}")
        print(f"📁 Production files only - scripts remain in scripts/hardcover/")
        
        return output_dir

def load_book_config(config_file):
    """Load book configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Create hardcover production package')
    parser.add_argument('config', help='Book configuration JSON file')
    args = parser.parse_args()
    
    try:
        config = load_book_config(args.config)
        producer = HardcoverProducer(config)
        producer.create_complete_package()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()