#!/usr/bin/env python3
"""
Bundle Creator - Smart Bundle Strategy System
Creates profitable bundles only when conditions are optimal
"""
import os
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class BundleCreator:
    def __init__(self):
        self.output_dir = Path("output")
        self.bundles_dir = self.output_dir / "bundles"
        self.bundles_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_series_for_bundles(self, series_path):
        """Analyze series to determine if bundle-ready"""
        series_manifest = Path(series_path) / "series_manifest.json"
        
        if not series_manifest.exists():
            return None
            
        with open(series_manifest, 'r') as f:
            series_data = json.load(f)
        
        volume_count = len(series_data.get('volumes', []))
        
        # Bundle eligibility criteria
        bundle_ready = {
            "eligible": volume_count >= 3,
            "volume_count": volume_count,
            "series_name": series_data.get('series_name'),
            "individual_prices": [vol.get('price', 0) for vol in series_data.get('volumes', [])],
            "bundle_strategies": []
        }
        
        if volume_count >= 3:
            bundle_ready["bundle_strategies"].append({
                "type": "Starter Pack Bundle",
                "volumes": [1, 2, 3],
                "bundle_price": sum(bundle_ready["individual_prices"][:3]) * 0.7,
                "savings": sum(bundle_ready["individual_prices"][:3]) * 0.3,
                "strategy": "Customer acquisition play"
            })
            
        if volume_count >= 5:
            bundle_ready["bundle_strategies"].append({
                "type": "Complete Series Bundle", 
                "volumes": list(range(1, volume_count + 1)),
                "bundle_price": sum(bundle_ready["individual_prices"]) * 0.7,
                "savings": sum(bundle_ready["individual_prices"]) * 0.3,
                "strategy": "Higher transaction value = better ROI"
            })
            
        return bundle_ready
    
    def create_bundle_manuscript(self, series_data, bundle_strategy):
        """Create intelligent bundle manuscript with intro/outro"""
        
        series_name = series_data['series_name']
        bundle_type = bundle_strategy['type']
        volume_numbers = bundle_strategy['volumes']
        
        # Bundle-specific intro
        intro = f"""
{series_name} - {bundle_type}
The Complete Collection

🎯 WHAT YOU GET:
• {len(volume_numbers)} Complete Books (Volumes {', '.join(map(str, volume_numbers))})
• Over {len(volume_numbers) * 100} Puzzles/Activities  
• Professional Quality Content
• Hours of Entertainment
• Incredible Value: Save ${bundle_strategy['savings']:.2f}!

WHY CHOOSE THE BUNDLE?
✅ Better Value: Get {len(volume_numbers)} books for the price of {len(volume_numbers) * 0.7:.1f}
✅ Complete Experience: The full series journey
✅ Instant Access: All volumes in one purchase
✅ Gift-Ready: Perfect for puzzle lovers

HOW TO USE THIS COLLECTION:
1. Start with Volume 1 for the best experience
2. Progress through each volume at your own pace  
3. Use the difficulty progression to build skills
4. Perfect for daily brain training routines

Ready to begin your puzzle journey? Let's start!

═══════════════════════════════════════════════════
"""
        
        # Combine all volume manuscripts
        combined_content = intro
        
        for vol_num in volume_numbers:
            vol_data = next((v for v in series_data['volumes'] if v['volume_number'] == vol_num), None)
            if vol_data:
                # Load volume manuscript
                vol_dir = Path(series_data['series_directory']) / f"volume_{vol_num}"
                manuscript_file = vol_dir / "manuscript.txt"
                
                if manuscript_file.exists():
                    with open(manuscript_file, 'r') as f:
                        volume_content = f.read()
                    
                    combined_content += f"\n\n{'='*60}\n"
                    combined_content += f"VOLUME {vol_num}: {vol_data['title']}\n"
                    combined_content += f"{'='*60}\n\n"
                    combined_content += volume_content
        
        # Bundle-specific outro
        outro = f"""

{'='*60}
🎉 CONGRATULATIONS!
{'='*60}

You've completed the {series_name} {bundle_type}!

🏆 ACHIEVEMENT UNLOCKED:
• Completed {len(volume_numbers)} full volumes
• Solved 500+ puzzles/activities
• Developed advanced skills
• Joined the elite puzzle masters club

📈 WHAT'S NEXT?
1. Share your achievement with friends and family
2. Leave a review to help other puzzle lovers
3. Check out our other series for new challenges
4. Follow us for new releases and updates

🎁 BONUS TIP:
This collection makes an excellent gift! Share the puzzle love with someone special.

Thank you for choosing {series_name}. Keep puzzling!

© 2025 Puzzle Pro Studios. All rights reserved.
"""
        
        combined_content += outro
        return combined_content
    
    def generate_bundle_keywords(self, series_data, bundle_strategy):
        """Generate mega-keywords combining all books"""
        all_keywords = set()
        
        # Collect all keywords from individual volumes
        for volume in series_data['volumes']:
            if 'keywords' in volume:
                all_keywords.update(volume['keywords'])
        
        # Add bundle-specific keywords
        bundle_keywords = [
            f"{series_data['series_name'].lower()} bundle",
            f"{series_data['series_name'].lower()} collection",
            f"{series_data['series_name'].lower()} complete series",
            "puzzle bundle",
            "book bundle", 
            "value pack",
            "complete collection",
            "mega pack"
        ]
        
        all_keywords.update(bundle_keywords)
        return list(all_keywords)[:7]  # KDP limit
    
    def create_bundle(self, series_path, bundle_strategy_type="auto"):
        """Create bundle package for series"""
        
        bundle_analysis = self.analyze_series_for_bundles(series_path)
        
        if not bundle_analysis or not bundle_analysis['eligible']:
            print(f"❌ Series not eligible for bundling (need 3+ volumes)")
            return None
        
        # Load series data
        with open(Path(series_path) / "series_manifest.json", 'r') as f:
            series_data = json.load(f)
        
        # Select bundle strategy
        if bundle_strategy_type == "auto":
            bundle_strategy = bundle_analysis['bundle_strategies'][0]  # Take first available
        else:
            bundle_strategy = next((b for b in bundle_analysis['bundle_strategies'] 
                                  if b['type'] == bundle_strategy_type), None)
            
        if not bundle_strategy:
            print(f"❌ Bundle strategy '{bundle_strategy_type}' not available")
            return None
        
        # Create bundle directory
        bundle_name = f"{series_data['series_name']}_{bundle_strategy['type'].replace(' ', '_')}"
        bundle_dir = self.bundles_dir / bundle_name
        bundle_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🎁 Creating {bundle_strategy['type']} for {series_data['series_name']}")
        
        # Generate bundle manuscript
        bundle_manuscript = self.create_bundle_manuscript(series_data, bundle_strategy)
        
        # Generate mega-keywords
        bundle_keywords = self.generate_bundle_keywords(series_data, bundle_strategy)
        
        # Create bundle data
        bundle_data = {
            "bundle_name": f"{series_data['series_name']} - {bundle_strategy['type']}",
            "type": bundle_strategy['type'],
            "series_name": series_data['series_name'],
            "volumes_included": bundle_strategy['volumes'],
            "volume_count": len(bundle_strategy['volumes']),
            "individual_total": sum(bundle_analysis['individual_prices']),
            "bundle_price": bundle_strategy['bundle_price'],
            "customer_savings": bundle_strategy['savings'],
            "keywords": bundle_keywords,
            "formats": {
                "paperback": {
                    "price": bundle_strategy['bundle_price'],
                    "savings": f"Save ${bundle_strategy['savings']:.2f}",
                    "royalty_per_sale": bundle_strategy['bundle_price'] * 0.6
                },
                "kindle": {
                    "price": bundle_strategy['bundle_price'] * 0.4,
                    "savings": f"Save ${bundle_strategy['savings'] * 0.4:.2f}", 
                    "royalty_per_sale": bundle_strategy['bundle_price'] * 0.4 * 0.7
                }
            },
            "strategy": bundle_strategy['strategy'],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save bundle files
        with open(bundle_dir / "bundle_manifest.json", 'w') as f:
            json.dump(bundle_data, f, indent=2)
            
        with open(bundle_dir / "bundle_manuscript.txt", 'w') as f:
            f.write(bundle_manuscript)
        
        # Create publishing guide
        publishing_guide = f"""
📦 BUNDLE PUBLISHING GUIDE: {bundle_data['bundle_name']}

🎯 BUNDLE STRATEGY: {bundle_data['strategy']}

PRICING ADVANTAGE:
Individual Books Total: ${bundle_data['individual_total']:.2f}
Bundle Price: ${bundle_data['bundle_price']:.2f}
Customer Saves: ${bundle_data['customer_savings']:.2f} ({(bundle_data['customer_savings']/bundle_data['individual_total']*100):.0f}% off!)

KDP DETAILS:
Title: {bundle_data['bundle_name']}
Author: Puzzle Pro Studios
Description: Get {bundle_data['volume_count']} complete books in one collection! Save ${bundle_data['customer_savings']:.2f} compared to buying individually.

Keywords: {', '.join(bundle_data['keywords'][:7])}

FORMATS & PRICING:
📖 Paperback: ${bundle_data['formats']['paperback']['price']:.2f} 
   Royalty: ${bundle_data['formats']['paperback']['royalty_per_sale']:.2f} per sale

📱 Kindle: ${bundle_data['formats']['kindle']['price']:.2f}
   Royalty: ${bundle_data['formats']['kindle']['royalty_per_sale']:.2f} per sale

REVENUE PROJECTIONS (Monthly):
Conservative (20 sales): ${(bundle_data['formats']['paperback']['royalty_per_sale'] * 20):.2f}
Moderate (50 sales): ${(bundle_data['formats']['paperback']['royalty_per_sale'] * 50):.2f}
Optimistic (100 sales): ${(bundle_data['formats']['paperback']['royalty_per_sale'] * 100):.2f}

MARKETING STRATEGY:
1. List AFTER individual books prove demand
2. Cross-promote in individual book descriptions
3. Target customers who bought individual volumes
4. Emphasize savings and convenience
5. Perfect for gift buyers

TIMING: Launch this bundle when you have 5+ positive reviews on individual volumes.
"""
        
        with open(bundle_dir / "BUNDLE_PUBLISHING_GUIDE.txt", 'w') as f:
            f.write(publishing_guide)
        
        print(f"✅ Bundle created: {bundle_name}")
        print(f"💰 Bundle Price: ${bundle_data['bundle_price']:.2f} (Customer saves ${bundle_data['customer_savings']:.2f})")
        print(f"📁 Location: {bundle_dir}")
        
        return bundle_data

def main():
    parser = argparse.ArgumentParser(description='Create smart bundles for book series')
    parser.add_argument('--series-path', required=True, help='Path to series directory')
    parser.add_argument('--strategy', default='auto', 
                       choices=['auto', 'Starter Pack Bundle', 'Complete Series Bundle'],
                       help='Bundle strategy to use')
    
    args = parser.parse_args()
    
    creator = BundleCreator()
    bundle = creator.create_bundle(args.series_path, args.strategy)
    
    if bundle:
        print("\n🎁 BUNDLE CREATION SUCCESSFUL!")
        print("Ready to maximize revenue through strategic bundling!")

if __name__ == "__main__":
    main()