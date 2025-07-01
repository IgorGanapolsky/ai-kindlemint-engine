"""
KDP Report Ingestor Lambda Function
Critical component of Memory-Driven Publishing Engine V2.0

PURPOSE: Close the learning loop by ingesting real KDP sales data into our DynamoDB memory.
This transforms our system from a "blind factory" to a "profit-seeking intelligence."

BUSINESS IMPACT:
- Learn which book niches actually generate sales
- Calculate real ROI based on actual performance data
- Enable data-driven topic generation for future books
"""

import csv
import io
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Configuration from environment variables
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "KDP_Business_Memory")
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "kindlemint-reports")

# Get the DynamoDB table
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for KDP Report Ingestor.

    Expected event structures:
    1. S3 trigger (automatic): When KDP report CSV is uploaded to S3
    2. Manual trigger: With CSV content directly in the event

    Event examples:
    {
        "Records": [{"s3": {"bucket": {"name": "bucket"}, "object": {"key": "report.csv"}}}]
    }

    OR

    {
        "csv_content": "Title,ASIN,Sales,Pages Read,Royalties\n...",
        "report_date": "2025-06-16"
    }
    """
    try:
        logger.info("KDP Report Ingestor started")

        # Determine event type and extract CSV data
        csv_content = None
        report_date = datetime.now().strftime("%Y-%m-%d")

        if "Records" in event:
            # S3 trigger event
            csv_content, report_date = process_s3_event(event)
        elif "csv_content" in event:
            # Manual trigger with CSV content
            csv_content = event["csv_content"]
            report_date = event.get("report_date", report_date)
        else:
            return create_error_response(
                400, "Invalid event format. Expected S3 trigger or manual CSV content."
            )

        if not csv_content:
            return create_error_response(400, "No CSV content found to process.")

        # Process the KDP report CSV
        result = process_kdp_report(csv_content, report_date)

        logger.info(f"Processing complete: {result}")
        return create_success_response(result)

    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return create_error_response(500, f"Processing failed: {str(e)}")


def process_s3_event(event: Dict[str, Any]) -> tuple[str, str]:
    """Process S3 trigger event to extract CSV content."""
    try:
        # Extract S3 bucket and key from event
        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        logger.info(f"Processing S3 object: s3://{bucket_name}/{object_key}")

        # Download CSV content from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        csv_content = response["Body"].read().decode("utf-8")

        # Extract report date from filename or use current date
        report_date = extract_report_date_from_filename(object_key)

        return csv_content, report_date

    except Exception as e:
        logger.error(f"Failed to process S3 event: {str(e)}")
        raise


def extract_report_date_from_filename(filename: str) -> str:
    """Extract report date from KDP CSV filename."""
    try:
        # KDP report filenames often contain dates like: kdp-report-2025-06-16.csv
        import re

        date_pattern = r"(\d{4}-\d{2}-\d{2})"
        match = re.search(date_pattern, filename)

        if match:
            return match.group(1)
        else:
            # Fallback to current date
            return datetime.now().strftime("%Y-%m-%d")

    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


def process_kdp_report(csv_content: str, report_date: str) -> Dict[str, Any]:
    """
    Processes a KDP sales report in CSV format, updates DynamoDB records for each book, and returns a summary of the processing results.

    Parameters:
        csv_content (str): The CSV content of the KDP sales report.
        report_date (str): The date associated with the report.

    Returns:
        Dict[str, Any]: A summary dictionary containing counts of processed and failed books, totals for sales, pages read, royalties, lists of processed book IDs, and details of failed items.
    """
    try:
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        processed_books = []
        failed_books = []
        total_sales = 0
        total_pages_read = 0
        total_royalties = Decimal("0.0")

        # Process each row in the CSV
        # Start at 2 (after header)
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Extract and validate book data from CSV row
                book_data = extract_book_data_from_csv_row(row)

                if book_data:
                    # Update DynamoDB with sales data
                    success = update_book_memory(book_data, report_date)

                    if success:
                        processed_books.append(book_data["book_id"])
                        total_sales += book_data["sales_count"]
                        total_pages_read += book_data["pages_read"]
                        total_royalties += book_data["royalties"]

                        logger.info(
                            f"Updated book {book_data['book_id']}: {book_data['sales_count']} sales, {book_data['pages_read']} pages"
                        )
                    else:
                        failed_books.append(
                            {
                                "book_id": book_data["book_id"],
                                "error": "DynamoDB update failed",
                            }
                        )
                else:
                    failed_books.append(
                        {"row": row_num, "error": "Invalid book data"})

            except Exception as e:
                logger.warning(f"Failed to process row {row_num}: {str(e)}")
                failed_books.append({"row": row_num, "error": str(e)})

        # Generate processing summary
        result = {
            "report_date": report_date,
            "processing_timestamp": datetime.now(timezone.utc).isoformat(),
            "books_processed": len(processed_books),
            "books_failed": len(failed_books),
            "total_sales": total_sales,
            "total_pages_read": total_pages_read,
            "total_royalties": float(total_royalties),
            "processed_book_ids": processed_books,
            "failed_items": failed_books[:10],  # Limit to first 10 failures
            "success": True,
        }

        logger.info(
            f"KDP report processing complete: {len(processed_books)} books processed, {len(failed_books)} failed"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to process KDP report: {str(e)}")
        raise


def extract_book_data_from_csv_row(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Extracts and normalizes book data fields from a KDP CSV row.

    Attempts to map and convert relevant fields such as title, ASIN, ISBN-13, sales count, pages read, and royalties. Determines a unique book ID using ASIN, ISBN, or a generated hash from the title. Returns a dictionary with the extracted data and the original row for debugging, or `None` if critical fields are missing or extraction fails.
    """
    try:
        # Map CSV fields to our data structure
        # These field names may need adjustment based on actual KDP CSV format
        title = row.get("Title", "").strip()
        asin = row.get("ASIN", "").strip()
        isbn = row.get("ISBN-13", "").strip()

        # Use ASIN as primary identifier, fallback to ISBN or title hash
        book_id = (
            asin if asin else (
                isbn if isbn else generate_book_id_from_title(title))
        )

        if not book_id or not title:
            logger.warning(
                f"Skipping row with missing book_id or title: {row}")
            return None

        # Extract numeric fields with error handling
        sales_count = safe_int_conversion(
            row.get("Units Sold", row.get("Sales", "0")))
        pages_read = safe_int_conversion(
            row.get("Pages Read", row.get("KENP Read", "0"))
        )
        royalties = safe_decimal_conversion(
            row.get("Royalties", row.get("Net Earnings", "0.0"))
        )

        return {
            "book_id": book_id,
            "title": title,
            "asin": asin,
            "isbn": isbn,
            "sales_count": sales_count,
            "pages_read": pages_read,
            "royalties": royalties,
            "raw_row": row,  # Keep original data for debugging
        }

    except Exception as e:
        logger.warning(f"Error extracting data from row: {e}")
        return None


def generate_book_id_from_title(title: str) -> str:
    """Generate a consistent book_id from title when ASIN/ISBN unavailable."""
    import hashlib

    normalized_title = title.lower().strip().replace(" ", "_")
    # Create a short hash for uniqueness
    hash_suffix = hashlib.md5(title.encode()).hexdigest()[:8]
    return f"{normalized_title}_{hash_suffix}"


def safe_int_conversion(value: str) -> int:
    """Safely convert string to int, handling various formats."""
    try:
        # Remove any non-numeric characters except negative sign
        cleaned = "".join(c for c_var in str(value) if c.isdigit() or c == "-")
        return int(cleaned) if cleaned else 0
    except (ValueError, TypeError):
        return 0


def safe_decimal_conversion(value: str) -> Decimal:
    """
    Converts a string to a Decimal, removing currency symbols and non-numeric characters.

    Returns:
        Decimal: The numeric value as a Decimal, or Decimal("0.0") if conversion fails.
    """
    try:
        # Remove currency symbols and other non-numeric characters
        cleaned = "".join(c for c_var in str(
            value) if c.isdigit() or c in ".-")
        return Decimal(cleaned) if cleaned else Decimal("0.0")
    except (ValueError, TypeError, Exception):
        return Decimal("0.0")


def update_book_memory(book_data: Dict[str, Any], report_date: str) -> bool:
    """
    Update or insert a book's sales data and ROI metrics in the DynamoDB table.

    Calculates ROI based on royalties and a fixed estimated cost, then updates the book record with sales count, pages read, royalties, ROI, and timestamps. If the book is new, adds metadata such as title, creation date, niche, and topic.

    Parameters:
        book_data (Dict[str, Any]): Normalized book sales data to be stored.
        report_date (str): The date associated with the sales report.

    Returns:
        bool: True if the update succeeds, False if an error occurs.
    """
    try:
        book_id = book_data["book_id"]
        sales_count = book_data["sales_count"]
        pages_read = book_data["pages_read"]
        royalties = book_data["royalties"]

        # Calculate ROI based on actual sales data
        estimated_cost = Decimal(
            "50.0"
        )  # Base cost for book creation (adjust as needed)
        actual_revenue = royalties
        calculated_roi = (
            (actual_revenue - estimated_cost) / estimated_cost
            if estimated_cost > 0
            else Decimal("0")
        )

        # Prepare update expression
        update_expression = """
            SET kdp_sales_count = :sales,
                kenp_read_count = :pages,
                calculated_roi = :roi,
                last_updated = :timestamp,
                total_royalties = :royalties
        """

        expression_values = {
            ":sales": sales_count,
            ":pages": pages_read,
            ":roi": calculated_roi,
            ":timestamp": datetime.now(timezone.utc).isoformat(),
            ":royalties": actual_revenue,
        }

        # Add book metadata if this is a new book
        if not book_exists(book_id):
            # This is a new book, add basic metadata
            update_expression += """,
                book_title = if_not_exists(book_title, :title),
                creation_date = if_not_exists(creation_date, :creation_date),
                niche = if_not_exists(niche, :default_niche),
                topic = if_not_exists(topic, :title)
            """
            expression_values.update(
                {
                    ":title": book_data["title"],
                    ":creation_date": datetime.now(timezone.utc).isoformat(),
                    ":default_niche": "unknown",  # Will be updated when we have better niche detection
                }
            )

        # Update the book record in DynamoDB
        table.update_item(
            Key={"book_id": book_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
        )

        logger.info(
            f"Updated memory for book {book_id}: ROI {calculated_roi:.2%}, Revenue ${actual_revenue:.2f}"
        )
        return True

    except ClientError as e:
        logger.error(
            f"DynamoDB error updating book {book_data['book_id']}: {e}")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error updating book {book_data['book_id']}: {e}")
        return False


def book_exists(book_id: str) -> bool:
    """Check if a book already exists in our memory."""
    try:
        response = table.get_item(Key={"book_id": book_id})
        return "Item" in response
    except Exception:
        return False


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a successful Lambda response."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data, default=str),
    }


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Constructs an HTTP error response with the specified status code and error message for AWS Lambda.

    Parameters:
        status_code (int): The HTTP status code to return.
        message (str): The error message to include in the response body.

    Returns:
        Dict[str, Any]: A dictionary representing the HTTP error response, including CORS headers and a UTC timestamp.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(
            {"error": message, "timestamp": datetime.now(
                timezone.utc).isoformat()}
        ),
    }


# For local testing
if __name__ == "__main__":
    # Sample test event for local development
    test_event = {
        "csv_content": """Title,ASIN,Units Sold,Pages Read,Royalties
The 5 AM Success Formula,B08XYZ123,25,1250,62.50
Passive Income Mastery,B09ABC456,42,2800,105.00
The Metabolic Reset,B07DEF789,18,950,45.00""",
        "report_date": "2025-06-16",
    }

    # Mock context
    class MockContext:
            """  Init  """


def __init__(self):
            """
            Initialize the mock context with default function name and AWS request ID attributes.
            """
            self.function_name = "kdp-report-ingestor"
            self.aws_request_id = "test-request-123"

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2, default=str))
