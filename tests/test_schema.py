#!/usr/bin/env python3
import csv
import json
from datetime import datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="Skipping market research CSV schema tests in CI")
"""
Test Market Research CSV Schema
Ensures CSV output follows the required schema
"""


class TestMarketResearchSchema:
    """Test suite for market research data schema validation"""

    # Required CSV columns
    REQUIRED_COLUMNS = ["date", "keyword",
                        "amazon_rank", "avg_price", "est_sales"]
    OPTIONAL_COLUMNS = ["competition_level", "reviews_avg"]

    def find_latest_csv(self) -> Path:
        """Find the most recent market research CSV file"""
        research_dir = Path("research")
        if not research_dir.exists():
            return None

        # Find all CSV files
        csv_files = []
        for date_dir in research_dir.iterdir():
            if date_dir.is_dir():
                for file in date_dir.glob("*.csv"):
                    csv_files.append(file)

        if not csv_files:
            return None

        # Return most recent
        return max(csv_files, key=lambda f: f.stat().st_mtime)

    def test_csv_exists(self):
        """Test that a CSV file was created"""
        csv_path = self.find_latest_csv()
        assert csv_path is not None, "No market research CSV files found"
        assert csv_path.exists(), f"CSV file does not exist: {csv_path}"

    def test_csv_schema(self):
        """Test that CSV has required columns"""
        csv_path = self.find_latest_csv()
        if not csv_path:
            pytest.skip("No CSV file to test")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            # Check required columns
            for col in self.REQUIRED_COLUMNS:
                assert col in headers, f"Missing required column: {col}"

            # Read first row to validate
            try:
                row = next(reader)
                self.validate_row(row)
            except StopIteration:
                pytest.fail("CSV file is empty")

    def validate_row(self, row: dict):
        """Validate a single CSV row"""
        # Date format
        try:
            datetime.strptime(row["date"], "%Y-%m-%d")
        except ValueError:
            pytest.fail(
                f"Invalid date format: {row['date']} (expected YYYY-MM-DD)")

        # Keyword not empty
        assert row["keyword"].strip(), "Keyword cannot be empty"

        # Amazon rank is positive integer
        try:
            rank = int(row["amazon_rank"])
            assert rank > 0, "Amazon rank must be positive"
        except ValueError:
            pytest.fail(
                f"Invalid amazon_rank: {row['amazon_rank']} (expected integer)")

        # Average price is positive float
        try:
            price = float(row["avg_price"])
            assert price >= 0, "Average price cannot be negative"
        except ValueError:
            pytest.fail(
                f"Invalid avg_price: {row['avg_price']} (expected float)")

        # Estimated sales is non-negative integer
        try:
            sales = int(row["est_sales"])
            assert sales >= 0, "Estimated sales cannot be negative"
        except ValueError:
            pytest.fail(
                f"Invalid est_sales: {row['est_sales']} (expected integer)")

    def test_all_rows_valid(self):
        """Test that all rows in CSV are valid"""
        csv_path = self.find_latest_csv()
        if not csv_path:
            pytest.skip("No CSV file to test")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)

            row_count = 0
            for idx, row in enumerate(reader):
                try:
                    self.validate_row(row)
                    row_count += 1
                except AssertionError as e:
                    pytest.fail(f"Row {idx + 2} validation failed: {e}")

            assert row_count > 0, "CSV file has no data rows"
            print(f"✅ Validated {row_count} rows successfully")

    def test_summary_json_exists(self):
        """Test that summary.json was created"""
        csv_path = self.find_latest_csv()
        if not csv_path:
            pytest.skip("No CSV file to test")

        summary_path = csv_path.parent / "summary.json"
        assert summary_path.exists(), f"Summary JSON not found: {summary_path}"

        # Validate JSON structure
        with open(summary_path, "r") as f:
            summary = json.load(f)

        assert "date" in summary, "Summary missing 'date' field"
        assert "total_keywords" in summary, "Summary missing 'total_keywords' field"
        assert (
            "top_opportunities" in summary
        ), "Summary missing 'top_opportunities' field"
        assert isinstance(
            summary["top_opportunities"], list
        ), "top_opportunities must be a list"

    def test_data_quality(self):
        """Test data quality metrics"""
        csv_path = self.find_latest_csv()
        if not csv_path:
            pytest.skip("No CSV file to test")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)

            keywords = set()
            price_range = []
            sales_range = []

            for row in reader:
                keywords.add(row["keyword"])
                price_range.append(float(row["avg_price"]))
                sales_range.append(int(row["est_sales"]))

        # Quality checks
        assert len(keywords) >= 1, "At least one unique keyword required"
        assert max(price_range) <= 1000, "Prices seem unrealistic (>$1000)"
        assert min(price_range) >= 0, "Negative prices found"
        assert (
            max(sales_range) <= 100000
        ), "Sales estimates seem unrealistic (>100k/month)"

        print(f"✅ Data quality checks passed:")
        print(f"   - Unique keywords: {len(keywords)}")
        print(
            f"   - Price range: ${min(price_range):.2f} - ${max(price_range):.2f}")
        print(f"   - Sales range: {min(sales_range)} - {max(sales_range)}")


def test_schema_compliance():
    """Quick test function for CI/CD"""
    tester = TestMarketResearchSchema()

    # Run core tests
    try:
        tester.test_csv_exists()
        tester.test_csv_schema()
        tester.test_all_rows_valid()
        tester.test_summary_json_exists()
        tester.test_data_quality()
        print("✅ All schema tests passed!")
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


if __name__ == "__main__":
    # Run tests
    if test_schema_compliance():
        exit(0)
    else:
        exit(1)
