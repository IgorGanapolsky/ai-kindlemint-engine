#!/usr/bin/env python3
"""
Multi-Format Book Generator
Command: python generate_book.py --formats kindle,paperback
"""
import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import importlib.util
import os

# Import modules directly
spec = importlib.util.spec_from_file_location("daily_series_generator", "scripts/daily_series_generator.py")
daily_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily_gen)

spec = importlib.util.spec_from_file_location("bundle_creator", "scripts/bundle_creator.py")
bundle_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle_mod)

spec = importlib.util.spec_from_file_location("profit_tracker", "scripts/profit_tracker.py")
profit_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profit_mod)

def main():
    parser = argparse.ArgumentParser(description='Generate books in multiple formats')
    parser.add_argument('--formats', default='kindle,paperback',
                       help='Comma-separated formats: kindle,paperback,bundle')
    parser.add_argument('--series-name', help='Specific series name to generate')
    parser.add_argument('--analyze-profit', action='store_true',
                       help='Run profit analysis after generation')
    parser.add_argument('--create-bundles', action='store_true',
                       help='Create bundles for eligible series')
    
    args = parser.parse_args()
    
    formats = [f.strip() for f in args.formats.split(',')]
    
    print(f"🚀 MULTI-FORMAT BOOK GENERATOR")
    print(f"📋 Formats: {', '.join(formats)}")
    print("="*50)
    
    # Generate series
    generator = daily_gen.DailySeriesGenerator()
    series_data = generator.generate_daily_series_batch()
    
    print(f"\n✅ Generated: {series_data['series_name']}")
    print(f"📚 Volumes: {len(series_data['volumes'])}")
    
    # Show format breakdown
    for volume in series_data['volumes']:
        print(f"\n📖 {volume['title']}:")
        for format_type, format_data in volume['formats'].items():
            if format_type in formats:
                print(f"  {format_type.title()}: ${format_data['price']:.2f} (${format_data['royalty_per_sale']:.2f} royalty)")
    
    # Create bundles if requested
    if args.create_bundles and len(series_data['volumes']) >= 3:
        print(f"\n🎁 Creating bundles...")
        bundle_creator = bundle_mod.BundleCreator()
        bundle = bundle_creator.create_bundle(series_data['series_directory'])
        if bundle:
            print(f"✅ Bundle created: {bundle['bundle_name']}")
    
    # Run profit analysis if requested
    if args.analyze_profit:
        print(f"\n📊 Running profit analysis...")
        tracker = profit_mod.MultiFormatProfitTracker()
        report = tracker.create_performance_report([series_data['series_directory']])
        
        print(f"💰 Conservative daily projection: ${report['financial_projections']['conservative']['daily_total']:.2f}")
        print(f"🚀 Aggressive daily projection: ${report['financial_projections']['aggressive']['daily_total']:.2f}")
        
        tracker.save_report(report)
    
    print(f"\n🎯 READY FOR PUBLISHING!")
    print(f"📁 Location: {series_data['series_directory']}")
    print("\n💡 Next steps:")
    print("1. Create covers using provided prompts")
    print("2. Publish paperback first, then Kindle within 24 hours")
    print("3. Monitor format performance ratios")
    print("4. Create bundles after 3+ volumes prove demand")

if __name__ == "__main__":
    main()