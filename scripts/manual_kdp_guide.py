#!/usr/bin/env python3
"""
Manual KDP Publishing Guide Generator
Creates step-by-step instructions for publishing books to Amazon KDP
"""

import os
import json
from datetime import datetime

def parse_kpf_file(kpf_file_path):
    """Parse KPF file to extract book metadata"""
    try:
        with open(kpf_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract title from first line or filename
        lines = content.split('\n')
        title = lines[0].replace('Title:', '').strip() if lines and 'Title:' in lines[0] else os.path.basename(kpf_file_path).replace('.kpf', '').replace('_', ' ').title()
        
        # Extract description/summary
        description = ""
        for i, line in enumerate(lines):
            if 'Description:' in line or 'Summary:' in line:
                description = line.split(':', 1)[1].strip()
                break
        
        if not description:
            description = f"An engaging children's story about {title.lower()}, designed to inspire young readers with adventure and imagination."
        
        return {
            'title': title,
            'description': description,
            'file_size': os.path.getsize(kpf_file_path),
            'file_path': kpf_file_path
        }
    except Exception as e:
        return {
            'title': 'Generated Book',
            'description': 'An AI-generated children\'s book ready for publishing',
            'file_size': 0,
            'file_path': kpf_file_path
        }

def generate_publishing_guide(kpf_file_path):
    """Generate complete KDP publishing guide"""
    book_data = parse_kpf_file(kpf_file_path)
    
    guide = f"""
📚 AMAZON KDP PUBLISHING GUIDE
{'='*50}

Book Details:
• Title: {book_data['title']}
• File: {book_data['file_path']}
• Size: {book_data['file_size']:,} bytes
• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STEP-BY-STEP PUBLISHING INSTRUCTIONS:
{'='*50}

1. LOGIN TO KDP
   • Go to: https://kdp.amazon.com
   • Sign in with your Amazon account
   • Navigate to your KDP dashboard

2. CREATE NEW TITLE
   • Click "Create a New Title"
   • Select "Kindle eBook"

3. ENTER BOOK DETAILS
   • Book Title: {book_data['title']}
   • Description: {book_data['description']}
   • Contributors: [Your Name]
   • Language: English
   • Categories: Children's Books > Adventure, Children's Books > Education

4. UPLOAD YOUR MANUSCRIPT
   • Click "Upload eBook Manuscript"
   • Select file: {book_data['file_path']}
   • Wait for processing (2-5 minutes)

5. SET UP BOOK COVER
   • Use KDP Cover Creator (recommended)
   • Title: {book_data['title']}
   • Style: Children's Adventure Theme
   • Or upload your own cover image (1600x2560 pixels minimum)

6. VERIFY BOOK DETAILS
   • Check title and author information
   • Review book description
   • Verify categories and keywords

7. SET PRICING AND DISTRIBUTION
   • Territories: Worldwide rights
   • Primary marketplace: Amazon.com
   • Price: $2.99 (recommended for 70% royalty)
   • Enrollment in KDP Select: Optional

8. PUBLISH YOUR BOOK
   • Review all information
   • Click "Publish Your Kindle eBook"
   • Book will be live within 24-72 hours

OPTIMIZATION TIPS:
{'='*20}
• Keywords: children's books, adventure, puzzle, educational, young readers
• Price point: $2.99-$4.99 for optimal sales
• Categories: Select 2 most relevant categories
• Book description: Use bullet points and emotional appeal

EXPECTED RESULTS:
{'='*20}
• Review period: 24-72 hours
• Royalty rate: 70% (at $2.99 price)
• Estimated earnings: $2.09 per sale
• Global distribution: 12+ Amazon marketplaces

Your book is ready for publishing! Follow these steps to get your AI-generated book live on Amazon.
"""
    
    # Save guide to file
    guide_filename = f"kdp_guide_{book_data['title'].lower().replace(' ', '_')}.txt"
    with open(guide_filename, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(guide)
    print(f"\n📄 Publishing guide saved to: {guide_filename}")
    
    return guide_filename

def log_manual_publishing(book_title, kpf_file):
    """Log manual publishing instructions provided"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"\n[{timestamp}] MANUAL PUBLISHING GUIDE GENERATED\n"
    log_entry += f"Book: {book_title}\n"
    log_entry += f"File: {kpf_file}\n"
    log_entry += f"Status: Instructions provided for manual KDP upload\n"
    log_entry += f"Next: User will manually publish to Amazon KDP\n"
    log_entry += "-" * 50 + "\n"
    
    with open('mission_log.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python manual_kdp_guide.py <kpf_file_path>")
        sys.exit(1)
    
    kpf_file = sys.argv[1]
    
    if not os.path.exists(kpf_file):
        print(f"Error: File {kpf_file} not found")
        sys.exit(1)
    
    book_data = parse_kpf_file(kpf_file)
    guide_file = generate_publishing_guide(kpf_file)
    log_manual_publishing(book_data['title'], kpf_file)
    
    print(f"\n✅ Ready to publish '{book_data['title']}' to Amazon KDP")
    print("Follow the guide above for step-by-step instructions")