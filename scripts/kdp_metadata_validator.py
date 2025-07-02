#!/usr/bin/env python3
"""
KDP Metadata Validator - Ensures all KDP requirements are met for maximum discoverability
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class KDPMetadataValidator:
    """Validates KDP metadata against Amazon's requirements and best practices"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_metadata_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Validate a KDP metadata JSON file"""
        try:
            with open(filepath, 'r') as f:
                metadata = json.load(f)
            
            return self.validate_metadata(metadata)
        except Exception as e:
            self.errors.append(f"Failed to load metadata: {e}")
            return False, self.errors
    
    def validate_metadata(self, metadata: Dict) -> Tuple[bool, List[str]]:
        """Validate KDP metadata structure and content"""
        # Reset for new validation
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Required fields
        required_fields = [
            'title', 'author', 'description', 'keywords', 
            'categories', 'language', 'price'
        ]
        
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate specific fields
        if 'title' in metadata:
            self._validate_title(metadata['title'])
        
        if 'subtitle' in metadata:
            self._validate_subtitle(metadata['subtitle'])
        
        if 'description' in metadata:
            self._validate_description(metadata['description'])
        
        if 'keywords' in metadata:
            self._validate_keywords(metadata['keywords'])
        
        if 'categories' in metadata:
            self._validate_categories(metadata['categories'])
        
        if 'price' in metadata:
            self._validate_price(metadata['price'])
        
        # Compile results
        all_issues = []
        if self.errors:
            all_issues.extend([f"❌ ERROR: {e}" for e in self.errors])
        if self.warnings:
            all_issues.extend([f"⚠️  WARNING: {w}" for w in self.warnings])
        if self.info:
            all_issues.extend([f"ℹ️  INFO: {i}" for i in self.info])
        
        return len(self.errors) == 0, all_issues
    
    def _validate_title(self, title: str):
        """Validate title requirements"""
        if len(title) > 200:
            self.errors.append(f"Title too long ({len(title)} chars, max 200)")
        if len(title) < 1:
            self.errors.append("Title cannot be empty")
        if title.isupper():
            self.warnings.append("Title is all caps - consider title case")
    
    def _validate_subtitle(self, subtitle: str):
        """Validate subtitle requirements"""
        if len(subtitle) > 200:
            self.errors.append(f"Subtitle too long ({len(subtitle)} chars, max 200)")
        if '|' in subtitle:
            self.info.append("Subtitle uses | separator - good for keyword optimization")
    
    def _validate_description(self, description: str):
        """Validate description requirements"""
        if len(description) > 4000:
            self.errors.append(f"Description too long ({len(description)} chars, max 4000)")
        if len(description) < 100:
            self.warnings.append("Description is very short - consider expanding for better conversion")
        
        # Check for good practices
        if '✓' in description or '•' in description:
            self.info.append("Description uses bullets/checkmarks - good for readability")
        if description.count('\n\n') > 0:
            self.info.append("Description has paragraph breaks - good formatting")
    
    def _validate_keywords(self, keywords: List[str]):
        """Validate keywords"""
        if len(keywords) != 7:
            self.errors.append(f"KDP requires exactly 7 keywords (found {len(keywords)})")
        
        for i, keyword in enumerate(keywords):
            if len(keyword) > 50:
                self.errors.append(f"Keyword {i+1} too long ({len(keyword)} chars, max 50)")
            if ',' in keyword:
                self.errors.append(f"Keyword {i+1} contains comma - not allowed")
    
    def _validate_categories(self, categories):
        """Validate categories - CRITICAL FOR DISCOVERABILITY"""
        if isinstance(categories, dict):
            # Old format with primary/secondary only
            self.errors.append("Categories should be a list of 3 items, not primary/secondary dict")
            self.warnings.append("You're missing out on 33% more discoverability!")
            return
        
        if not isinstance(categories, list):
            self.errors.append("Categories must be a list")
            return
        
        if len(categories) < 3:
            self.errors.append(f"KDP allows 3 categories but only {len(categories)} provided")
            self.warnings.append("Missing categories = missing sales opportunities!")
        elif len(categories) > 3:
            self.errors.append(f"KDP allows maximum 3 categories (found {len(categories)})")
        
        # Validate each category
        for i, cat in enumerate(categories):
            if not isinstance(cat, dict):
                self.errors.append(f"Category {i+1} must be a dict with 'id' and 'name'")
                continue
            
            if 'name' not in cat:
                self.errors.append(f"Category {i+1} missing 'name' field")
            elif not cat['name'].startswith('Games & Activities'):
                self.warnings.append(f"Category {i+1} may not be in correct browse path")
    
    def _validate_price(self, price):
        """Validate pricing structure"""
        if isinstance(price, dict):
            if 'us' in price:
                if price['us'] < 0.99:
                    self.errors.append("US price below KDP minimum ($0.99)")
                elif price['us'] > 9.99:
                    self.warnings.append("Price above $9.99 gets lower royalty rate (35% vs 70%)")
        else:
            self.errors.append("Price should be a dict with regional pricing")


def validate_all_kdp_metadata():
    """Find and validate all KDP metadata files in the project"""
    validator = KDPMetadataValidator()
    
    # Find all KDP metadata files
    metadata_files = list(Path('.').glob('**/kdp_metadata*.json'))
    metadata_files.extend(list(Path('.').glob('**/amazon_kdp_metadata.json')))
    
    print("🔍 KDP Metadata Validation Report")
    print("=" * 70)
    
    total_errors = 0
    
    for filepath in metadata_files:
        print(f"\n📄 Validating: {filepath}")
        print("-" * 50)
        
        valid, issues = validator.validate_metadata_file(filepath)
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ All checks passed!")
        
        if not valid:
            total_errors += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Summary: Validated {len(metadata_files)} files")
    
    if total_errors > 0:
        print(f"❌ Found errors in {total_errors} files")
        return False
    else:
        print("✅ All KDP metadata files are valid!")
        return True


if __name__ == "__main__":
    success = validate_all_kdp_metadata()
    sys.exit(0 if success else 1)