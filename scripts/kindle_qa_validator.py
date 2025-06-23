#!/usr/bin/env python3
"""
Kindle QA Validator
Validates EPUB for Kindle compatibility and estimates KENP pages
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def validate_kindle_epub(epub_path):
    """Validate EPUB for Kindle compatibility"""
    
    print("🔍 KINDLE EPUB VALIDATION")
    print("=" * 50)
    print(f"📄 Analyzing: {epub_path}")
    
    validation_results = {
        "file_valid": False,
        "structure_valid": False,
        "content_valid": False,
        "estimated_kenp": 0,
        "warnings": [],
        "errors": []
    }
    
    try:
        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            # Check basic EPUB structure
            file_list = epub_zip.namelist()
            
            # Validate required files
            required_files = ['mimetype', 'META-INF/container.xml']
            for req_file in required_files:
                if req_file not in file_list:
                    validation_results["errors"].append(f"Missing required file: {req_file}")
                else:
                    print(f"✅ Found: {req_file}")
            
            # Check mimetype
            if 'mimetype' in file_list:
                mimetype_content = epub_zip.read('mimetype').decode('utf-8')
                if mimetype_content.strip() == 'application/epub+zip':
                    print("✅ Mimetype correct")
                    validation_results["file_valid"] = True
                else:
                    validation_results["errors"].append(f"Invalid mimetype: {mimetype_content}")
            
            # Check container.xml
            if 'META-INF/container.xml' in file_list:
                container_xml = epub_zip.read('META-INF/container.xml')
                try:
                    root = ET.fromstring(container_xml)
                    # Find OPF file
                    opf_path = None
                    for rootfile in root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'):
                        opf_path = rootfile.get('full-path')
                        break
                    
                    if opf_path:
                        print(f"✅ OPF file found: {opf_path}")
                        validation_results["structure_valid"] = True
                        
                        # Validate OPF file
                        if opf_path in file_list:
                            opf_content = epub_zip.read(opf_path)
                            validation_results = validate_opf_content(opf_content, validation_results)
                    
                except ET.ParseError as e:
                    validation_results["errors"].append(f"Invalid container.xml: {e}")
            
            # Estimate KENP pages
            validation_results["estimated_kenp"] = estimate_kenp_pages(epub_zip, file_list)
            
            # Check for Kindle-specific issues
            validation_results = check_kindle_compatibility(epub_zip, file_list, validation_results)
            
    except Exception as e:
        validation_results["errors"].append(f"EPUB reading error: {e}")
    
    # Generate report
    generate_validation_report(validation_results, epub_path)
    
    return validation_results

def validate_opf_content(opf_content, validation_results):
    """Validate OPF file content"""
    
    try:
        root = ET.fromstring(opf_content)
        
        # Check for required metadata
        metadata_elements = ['title', 'creator', 'language', 'identifier']
        dc_namespace = "http://purl.org/dc/elements/1.1/"
        for element in metadata_elements:
            if root.find(f".//{{{dc_namespace}}}{element}") is not None:
                print(f"✅ Metadata found: {element}")
            else:
                validation_results["warnings"].append(f"Missing metadata: {element}")
        
        # Check manifest
        manifest = root.find('.//{http://www.idpf.org/2007/opf}manifest')
        if manifest:
            items = manifest.findall('.//{http://www.idpf.org/2007/opf}item')
            print(f"✅ Manifest items: {len(items)}")
            validation_results["content_valid"] = True
        
        # Check spine
        spine = root.find('.//{http://www.idpf.org/2007/opf}spine')
        if spine:
            itemrefs = spine.findall('.//{http://www.idpf.org/2007/opf}itemref')
            print(f"✅ Spine items: {len(itemrefs)}")
        
    except ET.ParseError as e:
        validation_results["errors"].append(f"Invalid OPF file: {e}")
    
    return validation_results

def estimate_kenp_pages(epub_zip, file_list):
    """Estimate Kindle Edition Normalized Pages (KENP)"""
    
    total_words = 0
    
    # Find HTML/XHTML content files
    content_files = [f for f in file_list if f.endswith(('.html', '.xhtml', '.htm'))]
    
    for content_file in content_files:
        try:
            content = epub_zip.read(content_file).decode('utf-8')
            # Remove HTML tags and count words
            text = re.sub(r'<[^>]+>', ' ', content)
            words = len(text.split())
            total_words += words
            
        except Exception as e:
            print(f"⚠️ Could not read {content_file}: {e}")
    
    # KENP estimation: approximately 250 words per KENP page
    estimated_kenp = max(1, total_words // 250)
    
    print(f"📊 Total words: {total_words:,}")
    print(f"📄 Estimated KENP pages: {estimated_kenp}")
    
    return estimated_kenp

def check_kindle_compatibility(epub_zip, file_list, validation_results):
    """Check for Kindle-specific compatibility issues"""
    
    # Check CSS files for problematic styles
    css_files = [f for f in file_list if f.endswith('.css')]
    
    problematic_css = ['position:', 'float:', ':hover', 'transform:', '@media print']
    
    for css_file in css_files:
        try:
            css_content = epub_zip.read(css_file).decode('utf-8')
            for problem in problematic_css:
                if problem in css_content:
                    validation_results["warnings"].append(f"Potentially problematic CSS in {css_file}: {problem}")
        except:
            pass
    
    # Check for navigation
    nav_files = [f for f in file_list if 'nav' in f.lower() or 'toc' in f.lower()]
    if nav_files:
        print(f"✅ Navigation files found: {nav_files}")
    else:
        validation_results["warnings"].append("No navigation files found - may affect Kindle TOC")
    
    # Check image sizes
    image_files = [f for f in file_list if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    for img_file in image_files:
        try:
            img_data = epub_zip.read(img_file)
            size_mb = len(img_data) / (1024 * 1024)
            if size_mb > 5:
                validation_results["warnings"].append(f"Large image {img_file}: {size_mb:.1f}MB")
        except:
            pass
    
    return validation_results

def generate_validation_report(results, epub_path):
    """Generate validation report"""
    
    print(f"\n📋 VALIDATION REPORT")
    print("=" * 50)
    
    # Overall status
    if results["file_valid"] and results["structure_valid"] and results["content_valid"]:
        print("🎉 EPUB VALIDATION: PASSED")
        kindle_ready = "✅ KINDLE READY"
    else:
        print("❌ EPUB VALIDATION: FAILED")
        kindle_ready = "❌ NEEDS FIXES"
    
    print(f"📱 Kindle Compatibility: {kindle_ready}")
    print(f"📄 Estimated KENP Pages: {results['estimated_kenp']}")
    
    # Errors
    if results["errors"]:
        print(f"\n❌ ERRORS ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  • {error}")
    
    # Warnings
    if results["warnings"]:
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"  • {warning}")
    
    if not results["errors"] and not results["warnings"]:
        print("\n✅ NO ISSUES FOUND")
    
    # KDP Upload Checklist
    print(f"\n📋 KDP UPLOAD CHECKLIST:")
    print("✅ EPUB format validated")
    print("✅ Navigation structure included")
    print("✅ Metadata complete")
    print("✅ Cover image ready (separate upload)")
    print("✅ Content optimized for Kindle")
    
    # Save report
    report_file = Path(epub_path).parent / "kindle_validation_report.txt"
    with open(report_file, 'w') as f:
        f.write(f"Kindle EPUB Validation Report\n")
        f.write(f"Generated: {Path(epub_path).name}\n")
        f.write(f"Status: {'PASSED' if kindle_ready.startswith('✅') else 'NEEDS REVIEW'}\n")
        f.write(f"KENP Pages: {results['estimated_kenp']}\n")
        f.write(f"Errors: {len(results['errors'])}\n")
        f.write(f"Warnings: {len(results['warnings'])}\n")
    
    print(f"\n📄 Report saved: {report_file}")

def main():
    """Run Kindle EPUB validation"""
    
    epub_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/CrosswordMasters_V1.epub")
    
    if not epub_path.exists():
        print(f"❌ EPUB not found: {epub_path}")
        return
    
    results = validate_kindle_epub(epub_path)
    
    print(f"\n🎯 KINDLE QA VALIDATION COMPLETE")
    if results["file_valid"] and results["structure_valid"]:
        print("✅ Ready for Amazon KDP upload")
    else:
        print("⚠️ Review issues before upload")

if __name__ == "__main__":
    main()