from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kindlemint",
    version="0.1.0",
    author="Igor Ganapolsky",
    author_email="your.email@example.com",
    description="An AI-powered automation engine for KDP (Kindle Direct Publishing)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IgorGanapolsky/ai-kindlemint-engine",
    packages=find_packages(),
    package_data={
        "kindlemint": ["templates/*"],
    },
    install_requires=[
        "python-dotenv>=1.0.0",       # Updated
        "requests>=2.31.0",           # Updated
        "beautifulsoup4>=4.10.0",     # No change from reqs.txt
        "lxml>=4.6.3",                # No change from reqs.txt
        "playwright>=1.40.0",         # Added
        "boto3>=1.34.0",              # Updated
        "selenium>=4.15.0",           # Updated
        "webdriver-manager>=4.0.0",   # Updated
        "openai>=1.3.0",              # Updated
        "google-generativeai>=0.3.0", # No change
        "nltk>=3.6.5",                # No change from reqs.txt
        "markdown2>=2.4.3",           # No change from reqs.txt
        "reportlab>=4.0.0",           # Added
        "pillow>=10.0.0",             # Added
        "google-api-python-client>=2.100.0", # Added
        "google-auth-httplib2>=0.2.0",     # Added
        "google-auth-oauthlib>=1.1.0",     # Added
        # "security==1.3.1", # Removed
    ],
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'pytest-cov>=3.0.0',
            'pytest-mock>=3.10.0',
            'black>=22.1.0',
            'flake8>=4.0.1',
            'isort>=5.10.1',
            'mypy>=0.931',
            'pre-commit>=2.17.0',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "kindlemint=kindlemint.cli.main:main",
        ],
    },
)
