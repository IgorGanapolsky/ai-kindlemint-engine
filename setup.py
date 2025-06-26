import setuptools

setuptools.setup(
    name="ai_kindlemint_engine",
    version="0.1.0",
    description="AI KindleMint Engine for automated content generation and formatting",
    packages=setuptools.find_packages(exclude=["tests", "scripts", "docs", "assets"]),
    install_requires=[
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.10.0",
        "lxml>=4.6.3",
        "PyYAML>=6.0",
        "playwright>=1.40.0",
        "nova-act>=0.1.0",
        "boto3>=1.34.0",
        # Selenium and webdriver-manager removed. Using Playwright for browser automation.
        "openai>=1.3.0",
        "nltk>=3.6.5",
        "markdown2>=2.4.3",
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "PyPDF2>=3.0.0",
        "PyMuPDF>=1.23.0",
        "google-api-python-client>=2.100.0",
        "google-auth-httplib2>=0.2.0",
        "google-auth-oauthlib>=1.1.0",
        "sentry-sdk>=1.40.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.1.0",
            "flake8>=4.0.1",
            "isort>=5.10.1",
            "mypy>=0.931",
            "pre-commit>=2.17.0",
        ]
    },
    python_requires=">=3.8",
)
