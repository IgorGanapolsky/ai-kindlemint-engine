# 🚨 URGENT: Web Scraping & Browser Automation Cleanup Plan

## ✅ CLEANUP EXECUTED - July 1, 2025

### Files Removed:
- ✅ `src/kindlemint/automation/kdp_automation_engine.py` - Selenium automation
- ✅ `scripts/reddit_market_scraper.py` - Reddit scraping
- ✅ `src/kindlemint/automation/kdp_automation_free.py` - Requests-based automation
- ✅ `complete_a2a_cleanup_20250701_133226/` - Old A2A backup
- ✅ `a2a_backup_20250701_122413/` - Old A2A backup

### Dependencies Removed from setup.py:
- ✅ beautifulsoup4
- ✅ playwright

### Additional Cleanup:
- ✅ Updated README.md to remove A2A Protocol references
- ✅ Removed old A2A directories
- ✅ Ran hygiene orchestrator (found 28 root files to clean)

### Files Still Containing Scraping Code:
- ⚠️ `src/kindlemint/agents/kdp_performance_agent.py` - Modified but still has BeautifulSoup
- ⚠️ `src/kindlemint/agents/market_research_agent.py` - Modified but still has BeautifulSoup

---

# 🚨 URGENT: Web Scraping & Browser Automation Cleanup Plan

## Summary of Problematic Technologies Found

### 1. **Web Scraping Libraries**
- **BeautifulSoup4** - Used for scraping Amazon product pages
- **requests** - Used for making HTTP requests to external sites
- **aiohttp** - Used for async web requests

### 2. **Browser Automation**
- **Selenium WebDriver** - Used for automating KDP uploads
- **Playwright** - Listed in dependencies but usage not found yet

## Files to Remove/Clean

### HIGH PRIORITY - Contains Web Scraping Code

1. **`src/kindlemint/agents/kdp_performance_agent.py`**
   - Lines 21, 156-184: BeautifulSoup Amazon scraping
   - Scrapes Amazon product pages for BSR, reviews, pricing
   - **Action: DELETE or completely rewrite without scraping**

2. **`src/kindlemint/agents/market_research_agent.py`**
   - Line 22: BeautifulSoup import
   - Contains market research scraping functionality
   - **Action: DELETE or rewrite to use official APIs only**

3. **`src/kindlemint/automation/kdp_automation_engine.py`**
   - Lines 17-21: Selenium WebDriver imports
   - Lines 143-304: Browser automation bot for KDP uploads
   - **Action: DELETE - This violates Amazon TOS**

4. **`scripts/reddit_market_scraper.py`**
   - Scrapes Reddit for market research
   - **Action: Review and possibly remove**

### MEDIUM PRIORITY - Dependencies to Remove

5. **`setup.py`**
   - Line 19: beautifulsoup4
   - Line 30: playwright
   - **Action: Remove these dependencies**

6. **`src/kindlemint/automation/kdp_automation_free.py`**
   - Uses requests library for market research
   - **Action: Review and clean**

### Configuration Files to Check

7. **Requirements files** (if any exist)
   - Remove selenium, beautifulsoup4, playwright

## Recommended Actions

1. **Immediate Actions:**
   - Delete all KDP automation files that use browser automation
   - Remove BeautifulSoup scraping from agents
   - Update setup.py to remove problematic dependencies

2. **Replace with Legitimate Approaches:**
   - Use official Amazon SP-API for product data
   - Use Google Books API for book research
   - Use legitimate keyword research APIs
   - Manual KDP uploads or official KDP API when available

3. **Code Audit:**
   - Search for any remaining web scraping patterns
   - Ensure no Terms of Service violations remain
   - Document approved data sources only

## Commands to Execute Cleanup

```bash
# Remove problematic files
rm src/kindlemint/agents/kdp_performance_agent.py
rm src/kindlemint/agents/market_research_agent.py
rm src/kindlemint/automation/kdp_automation_engine.py
rm scripts/reddit_market_scraper.py

# Update dependencies
# Edit setup.py to remove beautifulsoup4, playwright, selenium

# Search for any remaining issues
grep -r "selenium\|webdriver\|BeautifulSoup\|bs4\|playwright\|scrape\|scraping" src/ scripts/
```

## Next Steps

1. Review each file individually before deletion
2. Backup important business logic that can be salvaged
3. Implement proper API-based solutions
4. Update documentation to reflect new approach
5. Train team on acceptable data collection methods

**WARNING: Current code violates Amazon TOS and could result in account suspension!**