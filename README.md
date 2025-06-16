# AI KindleMint Engine V2.0 - Memory-Driven Publishing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blue.svg)](https://aws.amazon.com/dynamodb/)

**A world-class, autonomous Memory-Driven Publishing Engine** that transforms from random book creation to intelligent, profit-seeking automation. This system learns from sales data, identifies profitable niches, and generates revenue autonomously through complete end-to-end KDP publishing automation.

## 🚀 Features - V2.0 Memory-Driven Engine

### 🧠 Intelligence Layer
- **Memory-Driven Niche Selection**: DynamoDB brain stores book performance data with ROI calculations
- **AI Persona Market Validation**: Prevents low-viability content creation with confidence scoring
- **Profitable Topic Generation**: CTO Agent targets high-performing niches based on historical data
- **Data-Driven Marketing**: CMO Agent uses proven angles from successful campaigns

### 🏭 Autonomous Factory
- **Complete Content Generation**: 8-chapter books with intelligent structure
- **AI Cover Generation**: Multiple providers (DALL-E 3, Gemini, Stability AI) with fallbacks
- **Asset Packaging**: KDP-ready manuscript and cover preparation
- **Quality Validation**: Automated content and asset verification

### 🚀 Shipping Department  
- **Automated KDP Publishing**: Playwright-based browser automation for zero-touch publishing
- **Complete Metadata Management**: Title, description, keywords, pricing automation
- **Live Amazon Integration**: Direct publishing to Amazon KDP marketplace
- **Publication Monitoring**: Real-time status tracking and error handling

### 📊 Learning Loop
- **Sales Data Ingestion**: CFO Agent processes KDP reports automatically
- **ROI Calculation**: Continuous performance analysis and profit optimization
- **Memory Updates**: System learns and improves from every book published
- **Niche Domination**: Focuses resources on proven profitable categories

## 🏗️ Architecture - Serverless & Scalable

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│  Lambda Function │───▶│   DynamoDB      │
│   (Scheduler)   │    │  (Orchestrator)  │    │   (Memory)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│      S3         │◀───│  KDP Publisher   │───▶│   Amazon KDP    │
│  (Assets)       │    │   (Playwright)   │    │  (Live Books)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

#### 🧠 Memory System (`kindlemint/memory.py`)
- **DynamoDB Table**: `KDP_Business_Memory` 
- **Book Records**: topic, niche, creation_date, sales_count, ROI
- **Performance Analytics**: Top-performing niches identification
- **Learning Loop**: Continuous improvement through sales data

#### 🤖 AI Agents
- **CTO Agent** (`kindlemint/core/generator.py`): Memory-driven content generation
- **CMO Agent** (`kindlemint/agents/cmo.py`): Data-driven marketing copy  
- **CFO Agent** (`kindlemint/agents/cfo.py`): Financial analysis and ROI tracking
- **Market Validator** (`kindlemint/validation/market_research.py`): AI persona validation

#### 🚀 Publishing Engine
- **KDP Publisher** (`kindlemint/publisher/kdp_agent.py`): Automated browser-based publishing
- **End-to-End Pipeline** (`scripts/publish_book_end_to_end.py`): Complete orchestration
- **Asset Management**: Automated cover generation and manuscript preparation

#### ☁️ AWS Infrastructure
- **Lambda Functions**: Serverless execution environment
- **DynamoDB**: NoSQL database for memory storage
- **S3 Buckets**: Asset storage and KDP report ingestion
- **EventBridge**: Scheduled autonomous execution
- **CloudWatch**: Logging and monitoring

## 🛠️ Installation & Setup

### Prerequisites
- AWS Account with programmatic access
- Python 3.11+
- OpenAI API key
- KDP Publisher account

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
pip install -r publisher_requirements.txt

# Install Playwright for browser automation
playwright install chromium
```

### AWS Infrastructure Deployment
```bash
# Configure AWS credentials
aws configure --profile kindlemint-keys

# Create DynamoDB table
aws dynamodb create-table \
  --table-name KDP_Business_Memory \
  --attribute-definitions AttributeName=book_id,AttributeType=S \
  --key-schema AttributeName=book_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --profile kindlemint-keys

# Deploy Lambda function
cd lambda/deployment
./deploy-kdp-ingestor.sh
```

## 🔧 Configuration

Create a `.env` file in the root directory with your credentials:

```bash
# Essential for AI operations
OPENAI_API_KEY=your_openai_api_key

# Required for KDP publishing
KDP_EMAIL=your_kdp_email
KDP_PASSWORD=your_kdp_password

# Optional for monitoring
SLACK_WEBHOOK_URL=your_slack_webhook_url

# AWS credentials (configured via AWS CLI)
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY handled by profile
```

## 🚦 Usage

### Autonomous Production Operation
```bash
# Complete memory-driven pipeline (recommended)
python scripts/publish_book_end_to_end.py --headless

# Force specific niche
python scripts/publish_book_end_to_end.py --niche "productivity" --headless

# Memory-driven content generation only
python scripts/generate_memory_driven_book.py
```

### AWS Lambda Execution
```bash
# Manual trigger via AWS CLI
aws lambda invoke \
  --function-name kindlemintEngineFn \
  --payload '{"topic": "Custom Book Topic", "source": "manual"}' \
  --profile kindlemint-keys \
  response.json

# View execution results
cat response.json
```

### Testing and Validation
```bash
# Run integration tests
python tests/test_end_to_end_pipeline.py

# Test memory system
python examples/memory_demo.py

# Test individual components
python kindlemint/notifications/slack_notifier.py
```

## 📊 Monitoring & Analytics

### CloudWatch Logs
- **Function**: `/aws/lambda/kindlemintEngineFn`
- **Real-time pipeline execution monitoring**
- **Error tracking and debugging**

### DynamoDB Memory Analytics
```python
from kindlemint.memory import KDPMemory

memory = KDPMemory()
top_niches = memory.get_top_performing_niches(limit=5)
print(f"Most profitable niches: {top_niches}")
```

### Slack Notifications
- **Pipeline start/completion alerts**  
- **Error notifications**
- **Revenue milestone notifications**
- **Daily/weekly performance summaries**

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for self-published authors
- Powered by modern AI and automation technologies
