#!/usr/bin/env python3
"""
KDP Automation Engine - 100% Automated Book Publishing
No manual work required - complete automation from niche discovery to KDP upload
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from security import safe_requests


@dataclass
class NicheOpportunity:
    """Represents a profitable niche opportunity"""

    keyword: str
    search_volume: int
    competition_score: float
    profit_potential: float
    bsr_average: int
    price_range: tuple
    opportunity_score: float


@dataclass
class BookMetadata:
    """Complete book metadata for KDP upload"""

    title: str
    subtitle: str
    description: str
    keywords: List[str]
    categories: List[str]
    price: float
    author: str
    series: str = None


class AmazonProductAPI:
    """Amazon Product Advertising API wrapper"""

    def __init__(self, access_key: str, secret_key: str, partner_tag: str):
        """
        Initialize the Amazon Product API wrapper with the required credentials and base URL.
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_tag = partner_tag
        self.base_url = "https://webservices.amazon.com/paapi5"

    def search_books(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Searches for books matching the given keyword using the Amazon Product Advertising API.
        
        Parameters:
            keyword (str): The search term to query for books.
            max_results (int): The maximum number of results to return.
        
        Returns:
            List[Dict]: A list of dictionaries containing book information such as title, BSR, price, reviews, and rating. Returns an empty list if the search fails.
        """
        try:
            # Using paapi5 SDK would go here
            # For now, return mock data structure
            return [
                {
                    "title": f"Book about {keyword}",
                    "bsr": 50000,
                    "price": 8.99,
                    "reviews": 150,
                    "rating": 4.2,
                }
            ]
        except Exception as e:
            logging.error(f"Amazon API search failed: {e}")
            return []

    def get_category_bestsellers(self, category: str) -> List[Dict]:
        """
        Retrieve a list of bestseller books for a given Amazon category.
        
        Parameters:
            category (str): The Amazon category to search for bestsellers.
        
        Returns:
            List[Dict]: A list of bestseller book data for the specified category, or an empty list if unavailable.
        """
        try:
            # Implementation would use real Amazon API
            return []
        except Exception as e:
            logging.error(f"Category search failed: {e}")
            return []


class Helium10API:
    """Helium 10 Cerebro API for keyword research"""

    def __init__(self, api_key: str):
        """
        Initialize the Helium10API wrapper with the provided API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.helium10.com/v1"

    def analyze_keywords(self, keywords: List[str]) -> Dict:
        """
        Analyzes the competition and search volume for a list of keywords using the Helium 10 Cerebro API.
        
        Parameters:
        	keywords (List[str]): List of keywords to analyze.
        
        Returns:
        	Dict: JSON response containing keyword analysis data, or an empty dictionary if the API call fails.
        """
        try:
            response = requests.post(
                f"{self.base_url}/cerebro",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"keywords": keywords},
            timeout=60)
            return response.json()
        except Exception as e:
            logging.error(f"Helium 10 API failed: {e}")
            return {}

    def get_trending_keywords(self, category: str = "books") -> List[str]:
        """
        Retrieve a list of trending keywords for a specified category from the Helium 10 API.
        
        Parameters:
            category (str): The category to fetch trending keywords for. Defaults to "books".
        
        Returns:
            List[str]: A list of trending keywords, or an empty list if the request fails.
        """
        try:
            response = safe_requests.get(
                f"{self.base_url}/trends/{category}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60)
            return response.json().get("keywords", [])
        except Exception as e:
            logging.error(f"Trending keywords failed: {e}")
            return []


class JungleScoutAPI:
    """Jungle Scout API for sales estimates"""

    def __init__(self, api_key: str):
        """
        Initialize the JungleScoutAPI wrapper with the provided API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.junglescout.com/v1"

    def estimate_sales(self, bsr: int, category: str = "books") -> Dict:
        """
        Estimates book sales based on Best Seller Rank (BSR) and category using the Jungle Scout API.
        
        Parameters:
        	bsr (int): The Best Seller Rank of the book.
        	category (str): The product category to estimate sales for (default is "books").
        
        Returns:
        	Dict: A dictionary containing sales estimate data, or an empty dictionary if the request fails.
        """
        try:
            response = safe_requests.get(
                f"{self.base_url}/sales_estimates",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"bsr": bsr, "category": category},
            timeout=60)
            return response.json()
        except Exception as e:
            logging.error(f"Sales estimation failed: {e}")
            return {}


class KDPBrowserBot:
    """Automated KDP browser bot for uploads"""

    def __init__(self, headless: bool = True):
        """
        Initialize the KDPBrowserBot with an optional headless mode for browser automation.
        
        Parameters:
            headless (bool): If True, runs the browser in headless mode. Defaults to True.
        """
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """
        Initializes and configures the Chrome WebDriver for browser automation with optional headless mode.
        """
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def login_to_kdp(self, email: str, password: str) -> bool:
        """
        Logs into the Amazon KDP account using the provided email and password.
        
        Returns:
            bool: True if login is successful and the KDP dashboard is loaded, False otherwise.
        """
        try:
            self.driver.get("https://kdp.amazon.com/en_US/")

            # Wait for and click sign in
            sign_in_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Sign in')]")
                )
            )
            sign_in_btn.click()

            # Enter credentials
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "ap_email"))
            )
            email_field.send_keys(email)

            continue_btn = self.driver.find_element(By.ID, "continue")
            continue_btn.click()

            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "ap_password"))
            )
            password_field.send_keys(password)

            signin_btn = self.driver.find_element(By.ID, "signInSubmit")
            signin_btn.click()

            # Wait for dashboard
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "kdp-dashboard"))
            )
            return True

        except Exception as e:
            logging.error(f"KDP login failed: {e}")
            return False

    def upload_book(self, pdf_path: str, metadata: BookMetadata) -> bool:
        """
        Automates the process of uploading a book to Amazon KDP using the provided PDF file and metadata.
        
        Parameters:
            pdf_path (str): Path to the book's PDF file.
            metadata (BookMetadata): Metadata containing book details, keywords, categories, and pricing.
        
        Returns:
            bool: True if the upload and submission process completes successfully, False otherwise.
        """
        try:
            # Navigate to create new book
            self.driver.get("https://kdp.amazon.com/en_US/bookshelf")

            create_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[contains(text(), 'Create New Title')]")
                )
            )
            create_btn.click()

            # Select Paperback
            paperback_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[text()='Paperback']"))
            )
            paperback_btn.click()

            # Fill in metadata
            self._fill_book_details(metadata)

            # Upload content
            self._upload_content(pdf_path)

            # Set pricing
            self._set_pricing(metadata.price)

            # Submit for review
            self._submit_for_review()

            return True

        except Exception as e:
            logging.error(f"Book upload failed: {e}")
            return False

    def _fill_book_details(self, metadata: BookMetadata):
        """
        Fills the KDP book details form fields with the provided metadata, including title, subtitle, author, description, and up to seven keywords.
        """
        # Title
        title_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        title_field.clear()
        title_field.send_keys(metadata.title)

        # Subtitle
        if metadata.subtitle:
            subtitle_field = self.driver.find_element(By.NAME, "subtitle")
            subtitle_field.clear()
            subtitle_field.send_keys(metadata.subtitle)

        # Author
        author_field = self.driver.find_element(By.NAME, "author")
        author_field.clear()
        author_field.send_keys(metadata.author)

        # Description
        description_field = self.driver.find_element(By.NAME, "description")
        description_field.clear()
        description_field.send_keys(metadata.description)

        # Keywords
        # KDP allows 7 keywords
        for i, keyword in enumerate(metadata.keywords[:7]):
            keyword_field = self.driver.find_element(By.NAME, f"keyword_{i+1}")
            keyword_field.clear()
            keyword_field.send_keys(keyword)

        # Categories - would need specific KDP category IDs
        # This would require mapping our categories to KDP's dropdown values

    def _upload_content(self, pdf_path: str):
        """
        Uploads the specified PDF file as book content during the KDP publishing process.
        
        Parameters:
            pdf_path (str): Path to the PDF file to be uploaded.
        """
        upload_input = self.wait.until(
            EC.presence_of_element_located((By.INPUT, "file"))
        )
        upload_input.send_keys(str(Path(pdf_path).absolute()))

        # Wait for upload to complete
        time.sleep(10)

    def _set_pricing(self, price: float):
        """
        Sets the list price for the book in the KDP pricing form.
        
        Parameters:
            price (float): The price to set for the book.
        """
        price_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "list_price"))
        )
        price_field.clear()
        price_field.send_keys(str(price))

    def _submit_for_review(self):
        """
        Submits the book for review on KDP by clicking the publish button.
        """
        submit_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Publish')]")
            )
        )
        submit_btn.click()

    def cleanup(self):
        """
        Closes the browser driver if it has been initialized.
        """
        if self.driver:
            self.driver.quit()


class KDPAutomationEngine:
    """
    Complete KDP automation engine
    Handles everything from niche discovery to book publishing
    """

    def __init__(self, config: Dict[str, str]):
        """
        Initializes the KDPAutomationEngine with API clients and browser automation using the provided configuration.
        
        The configuration dictionary should include API keys for Amazon Product Advertising, Helium 10, Jungle Scout, and an optional headless flag for browser automation.
        """
        self.amazon_api = AmazonProductAPI(
            config.get("amazon_access_key"),
            config.get("amazon_secret_key"),
            config.get("amazon_partner_tag"),
        )

        self.helium10_api = Helium10API(config.get("helium10_api_key"))
        self.jungle_scout_api = JungleScoutAPI(
            config.get("jungle_scout_api_key"))
        self.browser_bot = KDPBrowserBot(headless=config.get("headless", True))

        self.logger = logging.getLogger(__name__)

    async def find_profitable_niches(
        self, seed_keywords: List[str] = None
    ) -> List[NicheOpportunity]:
        """
        Asynchronously discovers and ranks profitable book niches based on keyword trends and market data.
        
        If no seed keywords are provided, trending keywords are retrieved automatically. For each keyword, the method gathers Amazon and Helium 10 data, calculates an opportunity score, and returns the top 10 niches as a ranked list of `NicheOpportunity` instances.
         
        Returns:
            List[NicheOpportunity]: The top 10 profitable niches sorted by opportunity score.
        """
        self.logger.info("🔍 Starting automated niche discovery...")

        if not seed_keywords:
            # Get trending keywords automatically
            seed_keywords = self.helium10_api.get_trending_keywords("books")

        opportunities = []

        for keyword in seed_keywords:
            # Get Amazon data
            amazon_results = self.amazon_api.search_books(keyword)

            # Get Helium 10 data
            h10_data = self.helium10_api.analyze_keywords([keyword])

            # Calculate opportunity score
            opportunity = self._calculate_opportunity(
                keyword, amazon_results, h10_data)
            if opportunity:
                opportunities.append(opportunity)

        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)

        self.logger.info(
            f"✅ Found {len(opportunities)} profitable opportunities")
        return opportunities[:10]  # Return top 10

    def _calculate_opportunity(
        self, keyword: str, amazon_data: List[Dict], h10_data: Dict
    ) -> Optional[NicheOpportunity]:
        """
        Calculates and returns a NicheOpportunity for a given keyword using Amazon and Helium 10 data.
        
        Returns:
            NicheOpportunity: An instance containing calculated metrics and opportunity score, or None if no Amazon data is available.
        """
        if not amazon_data:
            return None

        # Extract metrics
        avg_bsr = sum(book.get("bsr", 100000) for book in amazon_data) / len(
            amazon_data
        )
        avg_price = sum(book.get("price", 0)
                        for book in amazon_data) / len(amazon_data)
        avg_reviews = sum(book.get("reviews", 0) for book in amazon_data) / len(
            amazon_data
        )

        search_volume = h10_data.get("search_volume", 1000)
        competition = h10_data.get("competition_score", 50)

        # Calculate opportunity score (custom algorithm)
        opportunity_score = (
            (search_volume / 1000) * 0.3  # Higher search volume = better
            + (100 - competition) / 100 * 0.3  # Lower competition = better
            + (avg_price / 10) * 0.2  # Higher price = better
            + (50000 / avg_bsr) * 0.2  # Lower BSR = better
        )

        return NicheOpportunity(
            keyword=keyword,
            search_volume=search_volume,
            competition_score=competition,
            profit_potential=avg_price * 30,  # Rough monthly estimate
            bsr_average=int(avg_bsr),
            price_range=(avg_price * 0.8, avg_price * 1.2),
            opportunity_score=opportunity_score,
        )

    def generate_book_metadata(self, niche: NicheOpportunity) -> BookMetadata:
        """
        Generate SEO-optimized book metadata for a given niche.
        
        Uses an external SEO engine to enhance base metadata, producing a `BookMetadata` instance with an optimized title, subtitle, description, keywords, categories, price (minimum $7.99), author, and series.
         
        Parameters:
            niche (NicheOpportunity): The niche opportunity for which to generate book metadata.
        
        Returns:
            BookMetadata: The generated metadata optimized for marketing and KDP listing.
        """
        self.logger.info(f"📝 Generating metadata for niche: {niche.keyword}")

        # Use your existing SEO engine if available
        from kindlemint.marketing.seo_engine_2025 import SEOOptimizedMarketing

        seo_engine = SEOOptimizedMarketing()

        base_metadata = {
            "title": f"Large Print {niche.keyword.title()} for Adults",
            "category": "puzzles",
        }

        enhanced_metadata = seo_engine.enhance_book_marketing(base_metadata)

        return BookMetadata(
            title=enhanced_metadata.get("title", base_metadata["title"]),
            subtitle=f"100 {niche.keyword.title()} Puzzles - Easy to Hard Difficulty",
            description=enhanced_metadata.get(
                "description", f"Premium {niche.keyword} puzzle book"
            ),
            keywords=enhanced_metadata.get(
                "keywords", [niche.keyword, "puzzles", "large print"]
            ),
            categories=enhanced_metadata.get(
                "categories", ["Games & Activities"]),
            price=max(niche.price_range[0], 7.99),  # Minimum $7.99
            author="Puzzle Masters Publishing",
            series=f"Large Print {niche.keyword.title()} Masters",
        )

    async def auto_generate_and_publish(self, niche: NicheOpportunity) -> bool:
        """
        Performs the complete automation workflow for a given niche: generates book metadata and content, creates a PDF, logs into KDP, uploads the book, and submits it for review.
        
        Parameters:
            niche (NicheOpportunity): The niche opportunity for which to generate and publish a book.
        
        Returns:
            bool: True if the book was successfully published, False otherwise.
        """
        self.logger.info(f"🚀 Starting full automation for: {niche.keyword}")

        try:
            # 1. Generate metadata
            metadata = self.generate_book_metadata(niche)

            # 2. Generate book content using existing system
            from scripts.generate_book import generate_book

            pdf_path = await asyncio.to_thread(generate_book)

            # 3. Setup browser automation
            self.browser_bot.setup_driver()

            # 4. Login to KDP (credentials from environment)
            kdp_email = os.getenv("KDP_EMAIL")
            kdp_password = os.getenv("KDP_PASSWORD")

            if not kdp_email or not kdp_password:
                raise ValueError("KDP credentials not found in environment")

            login_success = self.browser_bot.login_to_kdp(
                kdp_email, kdp_password)
            if not login_success:
                raise Exception("KDP login failed")

            # 5. Upload book automatically
            upload_success = self.browser_bot.upload_book(pdf_path, metadata)

            if upload_success:
                self.logger.info(
                    f"✅ Book published successfully: {metadata.title}")
                return True
            else:
                raise Exception("Book upload failed")

        except Exception as e:
            self.logger.error(f"❌ Automation failed: {e}")
            return False
        finally:
            self.browser_bot.cleanup()

    async def run_full_automation(self, max_books: int = 3) -> List[Dict]:
        """
        Runs the full KDP automation pipeline to discover profitable niches, generate books, and publish them to KDP.
        
        Parameters:
            max_books (int): The maximum number of books to generate and publish in this run.
        
        Returns:
            List[Dict]: A list of dictionaries containing the niche keyword, opportunity score, success status, and timestamp for each attempted publication.
        """
        self.logger.info(
            f"🎯 Starting full KDP automation pipeline (max {max_books} books)"
        )

        results = []

        # 1. Find profitable niches
        niches = await self.find_profitable_niches()

        # 2. Process top niches
        for i, niche in enumerate(niches[:max_books]):
            self.logger.info(
                f"📚 Processing niche {i+1}/{max_books}: {niche.keyword}")

            success = await self.auto_generate_and_publish(niche)

            results.append(
                {
                    "niche": niche.keyword,
                    "opportunity_score": niche.opportunity_score,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Wait between uploads to avoid rate limiting
            if i < len(niches) - 1:
                await asyncio.sleep(300)  # 5 minute delay

        # 3. Generate report
        success_rate = sum(
            1 for r in results if r["success"]) / len(results) * 100
        self.logger.info(
            f"🎉 Automation complete! Success rate: {success_rate:.1f}%")

        return results


# Configuration loader
def load_automation_config() -> Dict[str, str]:
    """
    Load required API keys and settings from environment variables for automation.
    
    Raises:
        ValueError: If any required API key is missing.
    
    Returns:
        config (Dict[str, str]): Dictionary containing API keys and configuration settings.
    """
    import os

    config = {
        "amazon_access_key": os.getenv("AMAZON_ACCESS_KEY"),
        "amazon_secret_key": os.getenv("AMAZON_SECRET_KEY"),
        "amazon_partner_tag": os.getenv("AMAZON_PARTNER_TAG"),
        "helium10_api_key": os.getenv("HELIUM10_API_KEY"),
        "jungle_scout_api_key": os.getenv("JUNGLE_SCOUT_API_KEY"),
        "headless": os.getenv("HEADLESS_BROWSER", "true").lower() == "true",
    }

    # Check for required keys
    required_keys = ["helium10_api_key", "jungle_scout_api_key"]
    missing_keys = [k for k in required_keys if not config.get(k)]

    if missing_keys:
        raise ValueError(f"Missing required API keys: {missing_keys}")

    return config


# CLI interface
async def main():
    """
    Runs the command-line interface for the KDP automation engine, allowing users to discover profitable niches, publish a book, or execute the full automation pipeline.
    
    Returns:
        int: Exit code indicating success (0) or failure (1).
    """
    import argparse

    parser = argparse.ArgumentParser(description="KDP Automation Engine")
    parser.add_argument(
        "--mode",
        choices=["discover", "publish", "full"],
        default="discover",
        help="Automation mode to run",
    )
    parser.add_argument(
        "--max-books", type=int, default=3, help="Maximum books to publish"
    )
    parser.add_argument(
        "--keywords", nargs="+", help="Seed keywords for niche discovery"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    try:
        # Load configuration
        config = load_automation_config()

        # Initialize engine
        engine = KDPAutomationEngine(config)

        if args.mode == "discover":
            niches = await engine.find_profitable_niches(args.keywords)
            print("\n🎯 Top Profitable Niches:")
            for i, niche in enumerate(niches, 1):
                print(f"{i}. {niche.keyword} (Score: {niche.opportunity_score:.2f})")

        elif args.mode == "publish":
            # Use top niche for publishing
            niches = await engine.find_profitable_niches(args.keywords)
            if niches:
                success = await engine.auto_generate_and_publish(niches[0])
                print(f"Publishing {'succeeded' if success else 'failed'}")

        elif args.mode == "full":
            results = await engine.run_full_automation(args.max_books)
            print(f"\n✅ Full automation complete: {results}")

    except Exception as e:
        print(f"❌ Automation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    asyncio.run(main())
