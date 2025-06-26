# 🚀 KindleMint Engine - Immediate Action Plan

## 🎯 Revenue-Focused Implementation Strategy

### 📅 TODAY: Fix CI for Automated Volume Generation

#### 1. GitHub Action for Auto-Generation
```yaml
# .github/workflows/auto_generate_next_volume.yml
name: Auto Generate Next Volume

on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9 AM
  workflow_dispatch:
    inputs:
      volume_number:
        description: 'Volume number to generate'
        required: true
        default: '5'

jobs:
  generate-volume:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Get previous volume feedback
        id: feedback
        run: |
          # Pull sales data and reviews from S3/API
          python scripts/get_volume_feedback.py --volume ${{ github.event.inputs.volume_number || '5' }}
          
      - name: Generate next volume with Claude
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python scripts/generate_next_volume.py \
            --volume ${{ github.event.inputs.volume_number || '5' }} \
            --feedback "${{ steps.feedback.outputs.feedback }}" \
            --market-data "${{ steps.feedback.outputs.market_trends }}"
            
      - name: Validate generated content
        run: |
          python scripts/enhanced_qa_validator.py \
            books/active_production/Large_Print_Crossword_Masters/volume_${{ github.event.inputs.volume_number || '5' }}/
            
      - name: Create PR with new volume
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🤖 Auto-generated Volume ${{ github.event.inputs.volume_number || '5' }}"
          body: |
            ## Auto-generated crossword volume
            
            Based on:
            - Previous volume sales data
            - Customer feedback analysis
            - Current market trends
            
            Please review before merging.
          branch: auto-gen-volume-${{ github.event.inputs.volume_number || '5' }}
```

#### 2. Volume Generation Script
```python
# scripts/generate_next_volume.py
import argparse
from api_manager_enhanced import EnhancedAPIManager

def generate_next_volume(volume_num, feedback_data, market_data):
    api_manager = EnhancedAPIManager()
    
    # Analyze what worked in previous volumes
    prompt = f"""
    Generate Volume {volume_num} of Large Print Crossword Masters.
    
    Previous volume feedback:
    {feedback_data}
    
    Current market trends:
    {market_data}
    
    Requirements:
    - 50 unique crossword puzzles
    - Incorporate popular themes from feedback
    - Avoid themes with negative reviews
    - Target difficulty based on customer preferences
    """
    
    result = api_manager.generate_text(
        prompt=prompt,
        task_name=f"generate_volume_{volume_num}",
        model="gpt-4",
        max_tokens=8000
    )
    
    # Generate actual puzzles
    generate_puzzles_from_outline(result['text'], volume_num)
```

### 📅 THIS WEEK: Firebase Genkit Market Research Endpoint

#### 1. Deploy Keyword Research Function
```javascript
// functions/marketResearch.js
const { onRequest } = require("firebase-functions/v2/https");
const { genkit } = require("@genkit-ai/genkit");
const { googleAI } = require("@genkit-ai/googleai");

// Initialize Genkit
const ai = genkit({
  plugins: [googleAI()],
  model: "gemini-pro"
});

exports.getMarketKeywords = onRequest(async (request, response) => {
  const { niche = "crossword puzzle books" } = request.query;
  
  // Real-time scraping logic
  const redditTrends = await scrapeReddit(niche);
  const amazonBestsellers = await scrapeAmazonBestsellers(niche);
  
  // AI analysis
  const analysis = await ai.generate({
    prompt: `
      Analyze these market trends and provide:
      1. Top 20 keywords for ${niche}
      2. Emerging sub-niches
      3. Content gaps in the market
      
      Reddit trends: ${redditTrends}
      Amazon bestsellers: ${amazonBestsellers}
    `,
    model: "gemini-pro"
  });
  
  // Store in Firestore
  await db.collection('market_research').add({
    niche,
    keywords: analysis.keywords,
    opportunities: analysis.opportunities,
    timestamp: new Date()
  });
  
  response.json(analysis);
});
```

#### 2. Quick Deploy
```bash
# Install Firebase tools
npm install -g firebase-tools

# Initialize Firebase
firebase init functions

# Add Genkit
cd functions && npm install @genkit-ai/genkit @genkit-ai/googleai

# Deploy
firebase deploy --only functions:getMarketKeywords
```

### 📅 NEXT 7 DAYS: Daily Regeneration Agent

#### Firebase Studio Agent Configuration
```javascript
// agents/dailyBookGenerator.js
const { onSchedule } = require("firebase-functions/v2/scheduler");
const { logger } = require("firebase-functions");

exports.dailyBookRegeneration = onSchedule("every day 06:00", async (event) => {
  const formats = ['paperback', 'kindle', 'hardcover'];
  const results = [];
  
  for (const format of formats) {
    try {
      // Get latest market data
      const marketData = await getLatestMarketTrends();
      
      // Generate optimized content
      const content = await generateOptimizedContent(format, marketData);
      
      // Store in Firestore
      const docRef = await db.collection('daily_generations').add({
        format,
        content,
        marketData,
        timestamp: new Date(),
        status: 'generated'
      });
      
      results.push({
        format,
        success: true,
        docId: docRef.id
      });
      
      logger.info(`Generated ${format} successfully`, { docId: docRef.id });
      
    } catch (error) {
      logger.error(`Failed to generate ${format}`, error);
      results.push({
        format,
        success: false,
        error: error.message
      });
    }
  }
  
  // Send summary to Slack
  await notifySlack('Daily generation complete', results);
});
```

### 📅 ONGOING: BookBolt/KDP Integration

#### Automated Keyword Ranking
```python
# scripts/keyword_ranker.py
import bookbolt_api  # hypothetical API wrapper
from kdp_scraper import KDPKeywordExtractor

class AutomatedKeywordRanker:
    def __init__(self):
        self.bookbolt = bookbolt_api.Client()
        self.kdp_extractor = KDPKeywordExtractor()
        
    def get_trending_keywords(self, category="crossword puzzles"):
        # Get data from multiple sources
        bookbolt_keywords = self.bookbolt.get_keywords(category)
        kdp_keywords = self.kdp_extractor.extract_bestseller_keywords(category)
        
        # Combine and rank
        all_keywords = self.merge_and_rank(bookbolt_keywords, kdp_keywords)
        
        # Store for Claude prompts
        self.update_prompt_templates(all_keywords[:20])
        
        return all_keywords
    
    def update_prompt_templates(self, top_keywords):
        # Update system prompts with trending keywords
        prompt_template = f"""
        Generate content optimized for these trending keywords:
        {', '.join(top_keywords)}
        
        Focus on the top 5 for maximum visibility.
        """
        
        # Save to config
        with open('config/prompt_templates.json', 'w') as f:
            json.dump({
                'keywords': top_keywords,
                'updated': datetime.now().isoformat(),
                'prompt_template': prompt_template
            }, f)
```

## 🎯 Success Metrics (Track Daily)

```python
# scripts/track_metrics.py
metrics = {
    "volumes_generated": 0,
    "ci_success_rate": 0.0,
    "keyword_api_calls": 0,
    "daily_regenerations": 0,
    "revenue_per_volume": 0.0
}

# Log to Firebase Analytics
analytics.log_event('daily_metrics', metrics)
```

## 🚨 Immediate Next Steps

### 1. RIGHT NOW (Next 30 minutes)
```bash
# Create the CI workflow
mkdir -p .github/workflows
# Copy the auto_generate_next_volume.yml content above

# Test locally
python scripts/generate_next_volume.py --volume 5 --feedback "test" --market-data "test"
```

### 2. TODAY (Next 2-4 hours)
```bash
# Set up Firebase project
firebase init
# Select: Functions, Firestore, Hosting

# Install Genkit
npm install @genkit-ai/genkit
```

### 3. THIS WEEK
- Deploy keyword endpoint
- Test with real market data
- Set up daily agent
- Connect to Firestore

## 💰 Expected ROI

- **Week 1**: Automated volume generation saves 10 hours/week
- **Week 2**: Market keywords increase visibility by 30%
- **Week 3**: Daily regeneration captures trending topics
- **Week 4**: Full automation = 5x more books published

---

**Remember**: Every hour spent on features that don't directly generate books or improve sales is wasted. Focus only on the automation that puts books on KDP faster and smarter.