# AI KindleMint Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

An AI-powered automation engine for KDP (Kindle Direct Publishing) that streamlines the book publishing process from start to finish.

## 🚀 Features

- **Automated Book Generation**: Generate book content using AI
- **Cover Design**: Automated cover creation with customizable templates
- **Metadata Management**: Handle book metadata, categories, and keywords
- **Publishing Workflow**: Automate the KDP publishing process
- **Batch Processing**: Publish multiple books in sequence
- **Analytics**: Track book performance and sales metrics

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/IgorGanapolsky/ai-kindlemint-engine.git
cd ai-kindlemint-engine

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## 📋 Prerequisites

- Python 3.8+
- KDP Seller Account
- Amazon API credentials
- (Optional) OpenAI API key for AI content generation

## 🚦 Usage

```bash
# Run the main application
python -m kindlemint

# For command-line options
python -m kindlemint --help
```

## 🔧 Configuration

Create a `.env` file in the root directory with your credentials:

```
KDP_EMAIL=your@email.com
KDP_PASSWORD=your_password
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
OPENAI_API_KEY=your_openai_key  # Optional
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for self-published authors
- Powered by modern AI and automation technologies
