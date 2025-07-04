import setuptools

"""
setup.py: Defines package metadata and dependencies for the ai_kindlemint_engine project.
"""

setuptools.setup(
    name="ai_kindlemint_engine",
    version="0.1.0",
    description="AI KindleMint Engine for automated content generation and formatting",
    # Our source code lives in the `src/` directory.
    package_dir={"": "src"},
    packages=setuptools.find_packages(
        where="src",
        exclude=["tests*", "scripts*", "docs*", "assets*"],
    ),
    install_requires=[
        # Alphabetical order for readability
        "click>=8.0.0",
        "google-api-python-client>=2.100.0",
        "google-auth-httplib2>=0.2.0",
        "google-auth-oauthlib>=1.1.0",
        "lxml>=4.6.3",
        "markdown2>=2.4.3",
        "nltk>=3.6.5",
        "nova-act>=0.1.0",
        "openai>=1.3.0",
        "pillow>=10.0.0",
        "psutil>=5.9.8",
        "PyMuPDF>=1.23.0",
        "PyPDF2>=3.0.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "reportlab>=4.0.0",
        "requests>=2.31.0",
        "sentry-sdk>=1.40.0",
        "stripe>=6.0.0",
    ],
    extras_require={
        "dev": [
            "black>=22.1.0",
            "flake8>=4.0.1",
            "isort>=5.10.1",
            "mypy>=0.931",
            "pre-commit>=2.17.0",
            "pytest>=6.2.5",
            "pytest-cov>=3.0.0",
            "pytest-json-report>=1.4.0",
            "pytest-mock>=3.10.0",
            "schedule>=1.2.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            # Primary CLI entrypoint
            "kindlemint=kindlemint.cli:cli",
        ],
    },
)
