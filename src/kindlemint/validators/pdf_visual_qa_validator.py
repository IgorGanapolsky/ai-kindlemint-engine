#!/usr/bin/env python3
"""
PDF Visual QA Validator
Validates PDFs for visual issues: text overlap, margin violations, layout problems
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image
import cv2
import pytesseract
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime


class PDFVisualQAValidator:
    """Comprehensive visual QA for PDF files"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        self.visual_issues = []
        
        # Layout constraints
        self.MIN_MARGIN_INCHES = 0.5
        self.MIN_TEXT_SPACING_PIXELS = 10
        self.MIN_FONT_SIZE_POINTS = 10
        self.MAX_TEXT_DENSITY = 0.8  # Max % of page covered by text
        
    def validate_pdf_visual_quality(self, pdf_path: Path, save_report: bool = True) -> Dict:
        """Main validation entry point"""
        print(f"🔍 Starting Visual QA Validation for: {pdf_path}")
        
        report = {
            "pdf_path": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "status": "PASS",
            "total_pages": 0,
            "visual_issues": [],
            "layout_violations": [],
            "text_overlaps": [],
            "margin_violations": [],
            "ocr_results": [],
            "recommendations": []
        }
        
        try:
            # Convert PDF to images
            images = self._convert_pdf_to_images(pdf_path)
            report["total_pages"] = len(images)
            
            # Run visual checks on each page
            for page_num, image in enumerate(images, 1):
                print(f"  Analyzing page {page_num}/{len(images)}...")
                
                # 1. Check for text overlaps using OCR
                overlaps = self._check_text_overlaps(image, page_num)
                if overlaps:
                    report["text_overlaps"].extend(overlaps)
                    
                # 2. Check margins
                margin_issues = self._check_margins(image, page_num)
                if margin_issues:
                    report["margin_violations"].extend(margin_issues)
                    
                # 3. Check layout spacing
                layout_issues = self._check_layout_spacing(image, page_num)
                if layout_issues:
                    report["layout_violations"].extend(layout_issues)
                    
                # 4. Detect visual anomalies
                anomalies = self._detect_visual_anomalies(image, page_num)
                if anomalies:
                    report["visual_issues"].extend(anomalies)
                    
                # Save annotated image if issues found
                if overlaps or margin_issues or layout_issues:
                    self._save_annotated_image(image, page_num, overlaps, margin_issues)
                    
        except Exception as e:
            self.errors.append(f"Visual QA failed: {str(e)}")
            report["status"] = "ERROR"
            report["error"] = str(e)
            
        # Compile final report
        if report["text_overlaps"] or report["margin_violations"] or report["layout_violations"]:
            report["status"] = "FAIL"
            
        report["errors"] = self.errors
        report["warnings"] = self.warnings
        report["passed_checks"] = self.passed_checks
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        # Save report
        if save_report:
            report_path = pdf_path.parent / f"{pdf_path.stem}_visual_qa_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Visual QA report saved to: {report_path}")
            
        return report
        
    def _convert_pdf_to_images(self, pdf_path: Path, dpi: int = 150) -> List[np.ndarray]:
        """Convert PDF pages to images for analysis"""
        try:
            pil_images = convert_from_path(pdf_path, dpi=dpi)
            images = []
            for pil_img in pil_images:
                # Convert PIL to numpy array for OpenCV
                img_array = np.array(pil_img)
                images.append(img_array)
            self.passed_checks.append(f"Successfully converted {len(images)} pages to images")
            return images
        except Exception as e:
            self.errors.append(f"PDF to image conversion failed: {str(e)}")
            raise
            
    def _check_text_overlaps(self, image: np.ndarray, page_num: int) -> List[Dict]:
        """Use OCR to detect overlapping text"""
        overlaps = []
        
        try:
            # Get OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text boxes with confidence > 50
            text_boxes = []
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 50 and ocr_data['text'][i].strip():
                    box = {
                        'text': ocr_data['text'][i],
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i],
                        'right': ocr_data['left'][i] + ocr_data['width'][i],
                        'bottom': ocr_data['top'][i] + ocr_data['height'][i]
                    }
                    text_boxes.append(box)
                    
            # Check for overlaps
            for i, box1 in enumerate(text_boxes):
                for j, box2 in enumerate(text_boxes[i+1:], i+1):
                    if self._boxes_overlap(box1, box2):
                        overlap = {
                            'page': page_num,
                            'text1': box1['text'],
                            'text2': box2['text'],
                            'location': f"({box1['x']},{box1['y']}) overlaps ({box2['x']},{box2['y']})",
                            'severity': 'HIGH'
                        }
                        overlaps.append(overlap)
                        self.errors.append(f"Page {page_num}: Text overlap detected - '{box1['text']}' overlaps with '{box2['text']}'")
                        
            if not overlaps:
                self.passed_checks.append(f"Page {page_num}: No text overlaps detected")
                
        except Exception as e:
            self.warnings.append(f"Page {page_num}: OCR check failed - {str(e)}")
            
        return overlaps
        
    def _boxes_overlap(self, box1: Dict, box2: Dict) -> bool:
        """Check if two bounding boxes overlap"""
        # Check if one box is to the left of the other
        if box1['right'] < box2['x'] or box2['right'] < box1['x']:
            return False
        # Check if one box is above the other
        if box1['bottom'] < box2['y'] or box2['bottom'] < box1['y']:
            return False
        return True
        
    def _check_margins(self, image: np.ndarray, page_num: int) -> List[Dict]:
        """Check if content respects margin requirements"""
        issues = []
        height, width = image.shape[:2]
        
        # Define margin boundaries (assuming 150 DPI)
        dpi = 150
        margin_pixels = int(self.MIN_MARGIN_INCHES * dpi)
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find content boundaries
        # Top margin
        top_content = 0
        for y in range(height):
            if np.any(gray[y, :] < 250):  # Non-white content
                top_content = y
                break
                
        # Bottom margin
        bottom_content = height
        for y in range(height-1, -1, -1):
            if np.any(gray[y, :] < 250):
                bottom_content = y
                break
                
        # Left margin
        left_content = 0
        for x in range(width):
            if np.any(gray[:, x] < 250):
                left_content = x
                break
                
        # Right margin
        right_content = width
        for x in range(width-1, -1, -1):
            if np.any(gray[:, x] < 250):
                right_content = x
                break
                
        # Check violations
        if top_content < margin_pixels:
            issues.append({
                'page': page_num,
                'type': 'top_margin',
                'expected': f"{self.MIN_MARGIN_INCHES} inches",
                'actual': f"{top_content/dpi:.2f} inches",
                'severity': 'MEDIUM'
            })
            
        if (height - bottom_content) < margin_pixels:
            issues.append({
                'page': page_num,
                'type': 'bottom_margin',
                'expected': f"{self.MIN_MARGIN_INCHES} inches",
                'actual': f"{(height-bottom_content)/dpi:.2f} inches",
                'severity': 'MEDIUM'
            })
            
        if left_content < margin_pixels:
            issues.append({
                'page': page_num,
                'type': 'left_margin',
                'expected': f"{self.MIN_MARGIN_INCHES} inches",
                'actual': f"{left_content/dpi:.2f} inches",
                'severity': 'MEDIUM'
            })
            
        if (width - right_content) < margin_pixels:
            issues.append({
                'page': page_num,
                'type': 'right_margin',
                'expected': f"{self.MIN_MARGIN_INCHES} inches",
                'actual': f"{(width-right_content)/dpi:.2f} inches",
                'severity': 'MEDIUM'
            })
            
        if not issues:
            self.passed_checks.append(f"Page {page_num}: All margins OK")
        else:
            for issue in issues:
                self.errors.append(f"Page {page_num}: {issue['type']} violation - expected {issue['expected']}, got {issue['actual']}")
                
        return issues
        
    def _check_layout_spacing(self, image: np.ndarray, page_num: int) -> List[Dict]:
        """Check for proper spacing between elements"""
        issues = []
        
        try:
            # Use edge detection to find content blocks
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (content blocks)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Get bounding boxes for significant contours
            boxes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small noise
                    x, y, w, h = cv2.boundingRect(contour)
                    boxes.append((x, y, w, h))
                    
            # Check spacing between elements
            boxes.sort(key=lambda b: (b[1], b[0]))  # Sort by y, then x
            
            for i in range(len(boxes)-1):
                box1 = boxes[i]
                box2 = boxes[i+1]
                
                # Vertical spacing
                vertical_gap = box2[1] - (box1[1] + box1[3])
                if 0 < vertical_gap < self.MIN_TEXT_SPACING_PIXELS:
                    issues.append({
                        'page': page_num,
                        'type': 'insufficient_vertical_spacing',
                        'location': f"Between elements at y={box1[1]} and y={box2[1]}",
                        'gap_pixels': vertical_gap,
                        'severity': 'LOW'
                    })
                    
        except Exception as e:
            self.warnings.append(f"Page {page_num}: Layout spacing check failed - {str(e)}")
            
        if not issues:
            self.passed_checks.append(f"Page {page_num}: Layout spacing OK")
            
        return issues
        
    def _detect_visual_anomalies(self, image: np.ndarray, page_num: int) -> List[Dict]:
        """Detect other visual issues like cutoff text, strange alignments"""
        anomalies = []
        
        try:
            # Check for text cut off at edges
            height, width = image.shape[:2]
            edge_margin = 20  # pixels
            
            # Get OCR data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 50 and ocr_data['text'][i].strip():
                    # Check if text is too close to edges
                    if ocr_data['left'][i] < edge_margin:
                        anomalies.append({
                            'page': page_num,
                            'type': 'text_near_left_edge',
                            'text': ocr_data['text'][i],
                            'distance': ocr_data['left'][i],
                            'severity': 'HIGH'
                        })
                        
                    if (ocr_data['left'][i] + ocr_data['width'][i]) > (width - edge_margin):
                        anomalies.append({
                            'page': page_num,
                            'type': 'text_near_right_edge',
                            'text': ocr_data['text'][i],
                            'distance': width - (ocr_data['left'][i] + ocr_data['width'][i]),
                            'severity': 'HIGH'
                        })
                        
        except Exception as e:
            self.warnings.append(f"Page {page_num}: Visual anomaly detection failed - {str(e)}")
            
        return anomalies
        
    def _save_annotated_image(self, image: np.ndarray, page_num: int, 
                             overlaps: List[Dict], margin_issues: List[Dict]):
        """Save image with visual issues highlighted"""
        try:
            fig, ax = plt.subplots(1, 1, figsize=(10, 14))
            ax.imshow(image)
            
            # Draw overlap boxes in red
            if overlaps:
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                for i in range(len(ocr_data['text'])):
                    if int(ocr_data['conf'][i]) > 50 and ocr_data['text'][i].strip():
                        # Check if this text is involved in overlap
                        for overlap in overlaps:
                            if ocr_data['text'][i] in [overlap['text1'], overlap['text2']]:
                                rect = patches.Rectangle(
                                    (ocr_data['left'][i], ocr_data['top'][i]),
                                    ocr_data['width'][i], ocr_data['height'][i],
                                    linewidth=2, edgecolor='red', facecolor='none'
                                )
                                ax.add_patch(rect)
                                
            # Draw margin lines in yellow
            if margin_issues:
                height, width = image.shape[:2]
                dpi = 150
                margin_pixels = int(self.MIN_MARGIN_INCHES * dpi)
                
                ax.axhline(y=margin_pixels, color='yellow', linestyle='--', linewidth=2)
                ax.axhline(y=height-margin_pixels, color='yellow', linestyle='--', linewidth=2)
                ax.axvline(x=margin_pixels, color='yellow', linestyle='--', linewidth=2)
                ax.axvline(x=width-margin_pixels, color='yellow', linestyle='--', linewidth=2)
                
            ax.set_title(f"Page {page_num} - Visual Issues Detected")
            ax.axis('off')
            
            # Save annotated image
            output_path = Path(f"visual_qa_page_{page_num}_annotated.png")
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.passed_checks.append(f"Saved annotated image: {output_path}")
            
        except Exception as e:
            self.warnings.append(f"Failed to save annotated image: {str(e)}")
            
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations based on issues found"""
        recommendations = []
        
        if report['text_overlaps']:
            recommendations.append("CRITICAL: Fix text overlap issues by adjusting spacing between elements")
            recommendations.append("- Increase vertical spacing between title and content")
            recommendations.append("- Ensure proper line height for text blocks")
            
        if report['margin_violations']:
            recommendations.append("IMPORTANT: Adjust page margins to meet minimum requirements")
            recommendations.append("- Ensure at least 0.5 inch margins on all sides")
            recommendations.append("- Move content away from page edges")
            
        if report['layout_violations']:
            recommendations.append("MEDIUM: Improve layout spacing for better readability")
            recommendations.append("- Add more space between content blocks")
            recommendations.append("- Ensure consistent spacing throughout document")
            
        if report['visual_issues']:
            recommendations.append("CHECK: Review visual anomalies")
            recommendations.append("- Ensure no text is cut off at page edges")
            recommendations.append("- Verify all content is properly aligned")
            
        if not recommendations:
            recommendations.append("✅ No visual issues detected - PDF layout appears good!")
            
        return recommendations


def compare_pdf_screenshots(pdf1_path: Path, pdf2_path: Path, 
                          threshold: float = 0.95) -> Dict:
    """Compare two PDFs visually for regression testing"""
    validator = PDFVisualQAValidator()
    
    try:
        # Convert both PDFs to images
        images1 = validator._convert_pdf_to_images(pdf1_path)
        images2 = validator._convert_pdf_to_images(pdf2_path)
        
        results = {
            'status': 'PASS',
            'similarity_scores': [],
            'differences': []
        }
        
        # Compare each page
        for i, (img1, img2) in enumerate(zip(images1, images2)):
            # Convert to grayscale for comparison
            gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            
            # Calculate structural similarity
            from skimage.metrics import structural_similarity as ssim
            score, diff = ssim(gray1, gray2, full=True)
            
            results['similarity_scores'].append({
                'page': i + 1,
                'score': score
            })
            
            if score < threshold:
                results['status'] = 'FAIL'
                results['differences'].append({
                    'page': i + 1,
                    'score': score,
                    'message': f'Page {i+1} differs significantly (score: {score:.3f})'
                })
                
                # Save difference image
                diff = (diff * 255).astype("uint8")
                cv2.imwrite(f"diff_page_{i+1}.png", diff)
                
        return results
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_visual_qa_validator.py <pdf_path>")
        sys.exit(1)
        
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
        
    validator = PDFVisualQAValidator()
    report = validator.validate_pdf_visual_quality(pdf_path)
    
    # Print summary
    print("\n" + "="*60)
    print(f"Visual QA Report Summary for: {pdf_path.name}")
    print("="*60)
    print(f"Status: {report['status']}")
    print(f"Total Pages: {report['total_pages']}")
    print(f"Text Overlaps: {len(report['text_overlaps'])}")
    print(f"Margin Violations: {len(report['margin_violations'])}")
    print(f"Layout Issues: {len(report['layout_violations'])}")
    print(f"Visual Anomalies: {len(report['visual_issues'])}")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")