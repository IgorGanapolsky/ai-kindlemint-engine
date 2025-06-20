#!/usr/bin/env python3
"""
Complete Series Workflow Automation
Generates multiple volumes of a book series and sets up publishing workflow
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from security import safe_command

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def generate_series_volumes(series_name: str, num_volumes: int = 5):
    """Generate multiple volumes of a book series"""
    logger = get_logger('series_workflow')
    
    logger.info(f"🚀 Starting series generation: {series_name}")
    logger.info(f"📚 Generating {num_volumes} volumes...")
    
    generated_volumes = []
    
    for volume_num in range(1, num_volumes + 1):
        logger.info(f"📖 Generating Volume {volume_num}...")
        
        try:
            # Generate book using Gemini AI
            cmd = [
                "python", "scripts/generate_with_gemini.py",
                "--volume", str(volume_num),
                "--series", series_name
            ]
            
            result = safe_command.run(subprocess.run, cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                logger.info(f"✅ Volume {volume_num} generated successfully")
                
                # Extract the generated book path from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if "Book generated at:" in line:
                        book_path = line.split("Book generated at: ")[1].strip()
                        generated_volumes.append({
                            'volume': volume_num,
                            'path': book_path,
                            'status': 'generated'
                        })
                        break
            else:
                logger.error(f"❌ Failed to generate Volume {volume_num}: {result.stderr}")
                generated_volumes.append({
                    'volume': volume_num,
                    'path': None,
                    'status': 'failed',
                    'error': result.stderr
                })
                
        except Exception as e:
            logger.error(f"❌ Error generating Volume {volume_num}: {str(e)}")
            generated_volumes.append({
                'volume': volume_num,
                'path': None,
                'status': 'error',
                'error': str(e)
            })
    
    return generated_volumes

def create_series_manifest(series_name: str, generated_volumes: list):
    """Create a manifest file for the series"""
    manifest = {
        'series_name': series_name,
        'generated_at': datetime.now().isoformat(),
        'total_volumes': len(generated_volumes),
        'successful_volumes': len([v for v in generated_volumes if v['status'] == 'generated']),
        'failed_volumes': len([v for v in generated_volumes if v['status'] in ['failed', 'error']]),
        'volumes': generated_volumes,
        'ready_for_publishing': True if all(v['status'] == 'generated' for v in generated_volumes) else False
    }
    
    # Save manifest
    manifest_path = Path("output/generated_books") / f"{series_name.lower().replace(' ', '_')}_series_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path, manifest

def create_publishing_checklist(series_name: str, manifest: dict):
    """Create a publishing checklist for the series"""
    checklist_content = f"""# {series_name} - Publishing Checklist

## Series Overview
- **Series Name**: {series_name}
- **Total Volumes**: {manifest['total_volumes']}
- **Generated**: {manifest['generated_at']}
- **Status**: {'✅ Ready for Publishing' if manifest['ready_for_publishing'] else '⚠️ Some volumes failed'}

## Volume Status
"""
    
    for volume in manifest['volumes']:
        status_icon = "✅" if volume['status'] == 'generated' else "❌"
        checklist_content += f"- Volume {volume['volume']}: {status_icon} {volume['status'].title()}\n"
    
    checklist_content += """
## Publishing Workflow

### 1. Review Generated Content
- [ ] Review all volume manuscripts for quality
- [ ] Check metadata and keywords for each volume
- [ ] Verify marketing content is compelling
- [ ] Ensure cover design prompts are clear

### 2. Create Covers
- [ ] Generate covers using DALL-E or professional designer
- [ ] Ensure covers follow series branding
- [ ] Test cover readability at thumbnail size
- [ ] Save covers in appropriate format and resolution

### 3. Prepare for KDP
- [ ] Format manuscripts for KDP (PDF conversion)
- [ ] Create KDP account if needed
- [ ] Set up tax information
- [ ] Plan release schedule (staggered releases recommended)

### 4. Upload to Amazon KDP
- [ ] Upload Volume 1 with all metadata
- [ ] Set pricing strategy
- [ ] Configure distribution settings
- [ ] Submit for review
- [ ] Repeat for remaining volumes

### 5. Marketing & Promotion
- [ ] Set up author website/landing page
- [ ] Create social media accounts
- [ ] Prepare launch marketing campaign
- [ ] Set up email list for series updates
- [ ] Plan customer review strategy

### 6. Google Drive Backup
- [ ] Run Google Drive sync to backup all volumes
- [ ] Verify all files are properly uploaded
- [ ] Share access with team members if needed

### 7. Monitor & Scale
- [ ] Track sales and reviews
- [ ] Plan additional volumes based on performance
- [ ] Optimize keywords and pricing
- [ ] Expand to other puzzle series

## Automation Commands

### Generate more volumes:
```bash
python scripts/generate_with_gemini.py --volume 6 --series "Large Print Crossword Masters"
```

### Sync to Google Drive:
```bash
python scripts/sync_to_google_drive.py
```

### Generate another series:
```bash
python scripts/create_series_workflow.py --series "Word Search Masters" --volumes 5
```

## Success Metrics
- [ ] Volume 1 sales > 10 units/month
- [ ] Average rating > 4.0 stars
- [ ] Positive customer feedback
- [ ] Ready to expand series

---
**Generated by KindleMint AI Publishing System**
"""
    
    checklist_path = Path("output/generated_books") / f"{series_name.lower().replace(' ', '_')}_publishing_checklist.md"
    with open(checklist_path, 'w') as f:
        f.write(checklist_content)
    
    return checklist_path

def main():
    """Main workflow function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate complete book series workflow')
    parser.add_argument('--series', default='Large Print Crossword Masters', help='Series name')
    parser.add_argument('--volumes', type=int, default=5, help='Number of volumes to generate')
    parser.add_argument('--skip-generation', action='store_true', help='Skip generation, just create workflow files')
    
    args = parser.parse_args()
    
    logger = get_logger('series_workflow')
    
    print("=" * 60)
    print("🚀 COMPLETE SERIES WORKFLOW AUTOMATION")
    print("=" * 60)
    
    if not args.skip_generation:
        # Generate all volumes
        generated_volumes = generate_series_volumes(args.series, args.volumes)
    else:
        # Mock generated volumes for workflow creation
        generated_volumes = [
            {'volume': i, 'path': f'mock_path_vol_{i}', 'status': 'generated'}
            for i in range(1, args.volumes + 1)
        ]
    
    # Create series manifest
    manifest_path, manifest = create_series_manifest(args.series, generated_volumes)
    logger.info(f"📋 Series manifest created: {manifest_path}")
    
    # Create publishing checklist
    checklist_path = create_publishing_checklist(args.series, manifest)
    logger.info(f"✅ Publishing checklist created: {checklist_path}")
    
    # Summary
    print("=" * 60)
    print("🎉 SERIES WORKFLOW COMPLETED!")
    print("=" * 60)
    print(f"📚 Series: {args.series}")
    print(f"✅ Successful volumes: {manifest['successful_volumes']}/{manifest['total_volumes']}")
    print(f"📋 Manifest: {manifest_path}")
    print(f"📝 Checklist: {checklist_path}")
    
    if manifest['ready_for_publishing']:
        print("\n🚀 READY FOR PUBLISHING!")
        print("Next steps:")
        print("1. Review the publishing checklist")
        print("2. Generate covers for each volume")
        print("3. Upload to Amazon KDP")
        print("4. Set up marketing campaigns")
    else:
        print(f"\n⚠️ Some volumes failed to generate ({manifest['failed_volumes']} failures)")
        print("Check the manifest file for details")
    
    print(f"\n📂 Google Drive sync: python scripts/sync_to_google_drive.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
