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
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "beautifulsoup4>=4.10.0",
        "lxml>=4.6.3",
        "boto3>=1.20.0",
        "selenium>=4.1.0",
        "webdriver-manager>=3.5.2",
        "openai>=0.27.0",
        "nltk>=3.6.5",
        "markdown2>=2.4.3",
        "security==1.3.1",
    ],
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
