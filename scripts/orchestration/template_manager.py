#!/usr/bin/env python3
"""
Template Management System
Enables rapid creation of book variants while maintaining consistent branding
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BookTemplate:
    """Represents a book template configuration"""
    name: str
    version: str
    description: str
    category: str
    defaults: Dict[str, Any]
    layout: Dict[str, Any]
    branding: Dict[str, Any]
    features: Dict[str, Any]
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BookTemplate':
        """Create template from dictionary"""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class TemplateManager:
    """Manages book templates and variations"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, BookTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from disk"""
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                config_path = template_dir / "config.json"
                if config_path.exists():
                    with open(config_path) as f:
                        data = json.load(f)
                        template = BookTemplate.from_dict(data)
                        self.templates[template_dir.name] = template
                        logger.info(f"Loaded template: {template.name}")
    
    def get_template(self, template_id: str) -> Optional[BookTemplate]:
        """Get a specific template"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                "id": template_id,
                "name": template.name,
                "category": template.category,
                "description": template.description
            }
            for template_id, template in self.templates.items()
        ]
    
    def create_template(self, template_id: str, template: BookTemplate) -> bool:
        """Create a new template"""
        template_dir = self.templates_dir / template_id
        if template_dir.exists():
            logger.error(f"Template {template_id} already exists")
            return False
        
        template_dir.mkdir(parents=True)
        config_path = template_dir / "config.json"
        
        with open(config_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
        
        self.templates[template_id] = template
        logger.info(f"Created template: {template_id}")
        return True
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template"""
        if template_id not in self.templates:
            logger.error(f"Template {template_id} not found")
            return False
        
        template = self.templates[template_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.now()
        
        # Save to disk
        config_path = self.templates_dir / template_id / "config.json"
        with open(config_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
        
        logger.info(f"Updated template: {template_id}")
        return True
    
    def create_variant(self, base_template_id: str, variant_name: str, 
                      modifications: Dict[str, Any]) -> Optional[str]:
        """Create a variant of an existing template"""
        base_template = self.get_template(base_template_id)
        if not base_template:
            logger.error(f"Base template {base_template_id} not found")
            return None
        
        # Create new template based on base
        variant_id = f"{base_template_id}_{variant_name}"
        variant_data = base_template.to_dict()
        
        # Apply modifications
        for key, value in modifications.items():
            if key in variant_data:
                if isinstance(variant_data[key], dict) and isinstance(value, dict):
                    variant_data[key].update(value)
                else:
                    variant_data[key] = value
        
        variant_data['name'] = f"{base_template.name} - {variant_name}"
        variant_data['description'] = f"Variant of {base_template.name}"
        
        # Create the variant
        variant_template = BookTemplate.from_dict(variant_data)
        if self.create_template(variant_id, variant_template):
            return variant_id
        
        return None
    
    def apply_template(self, template_id: str, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a template to book generation parameters"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Start with template defaults
        result = {
            "template_id": template_id,
            "template_name": template.name,
            **template.defaults,
            "layout": template.layout.copy(),
            "branding": template.branding.copy(),
            "features": template.features.copy()
        }
        
        # Override with book-specific parameters
        for key, value in book_params.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        
        return result
    
    def validate_template(self, template_id: str) -> List[str]:
        """Validate a template configuration"""
        template = self.get_template(template_id)
        if not template:
            return [f"Template {template_id} not found"]
        
        errors = []
        
        # Check required fields
        required_fields = ['name', 'version', 'category', 'defaults', 'layout', 'branding']
        for field in required_fields:
            if not getattr(template, field, None):
                errors.append(f"Missing required field: {field}")
        
        # Validate layout
        if 'page_size' not in template.layout:
            errors.append("Layout must include page_size")
        
        if 'margins' not in template.layout:
            errors.append("Layout must include margins")
        
        # Validate branding
        if 'website_url' not in template.branding:
            errors.append("Branding must include website_url")
        
        return errors
    
    def export_template(self, template_id: str, export_path: str) -> bool:
        """Export a template to a file"""
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template {template_id} not found")
            return False
        
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(export_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
        
        logger.info(f"Exported template {template_id} to {export_path}")
        return True
    
    def import_template(self, import_path: str, template_id: Optional[str] = None) -> Optional[str]:
        """Import a template from a file"""
        import_path = Path(import_path)
        if not import_path.exists():
            logger.error(f"Import file {import_path} not found")
            return None
        
        with open(import_path) as f:
            data = json.load(f)
        
        template = BookTemplate.from_dict(data)
        
        if not template_id:
            template_id = template.name.lower().replace(' ', '_')
        
        if self.create_template(template_id, template):
            return template_id
        
        return None


# Example usage
def main():
    """Example of template management"""
    manager = TemplateManager()
    
    # List available templates
    templates = manager.list_templates()
    print("Available templates:")
    for t in templates:
        print(f"  - {t['id']}: {t['name']} ({t['category']})")
    
    # Create a seasonal variant
    variant_id = manager.create_variant(
        base_template_id="premium_puzzle_pack",
        variant_name="holiday_edition",
        modifications={
            "defaults": {
                "puzzle_types": ["sudoku", "holiday_crossword", "festive_word_search"],
                "bonus_content": "holiday_themed"
            },
            "branding": {
                "series_name": "Holiday Special Edition"
            },
            "features": {
                "seasonal_graphics": True,
                "gift_certificate": True
            }
        }
    )
    
    if variant_id:
        print(f"\nCreated variant: {variant_id}")
    
    # Apply template to book generation
    book_params = {
        "title": "Christmas Puzzles 2025",
        "puzzle_count": 100,
        "difficulty_levels": ["easy", "medium"]
    }
    
    generation_params = manager.apply_template("premium_puzzle_pack", book_params)
    print(f"\nGeneration parameters: {json.dumps(generation_params, indent=2)}")


if __name__ == "__main__":
    main()