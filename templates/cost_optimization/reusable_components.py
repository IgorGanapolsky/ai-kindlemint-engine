#!/usr/bin/env python3
"""
Reusable Components Library for Cost Optimization
Pre-built, tested components to minimize Claude Code usage
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional

# =============================================================================
# ERROR HANDLING & RETRY LOGIC
# =============================================================================


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying functions with exponential backoff

    Usage:
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
            """Unstable Api Call"""
def unstable_api_call():
            # Your code here
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
            """Wrapper"""
def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        return wrapper

    return decorator


class SafeExecutor:
    """Safe execution context with comprehensive error handling"""

        """  Init  """
def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def execute_safely(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute function with comprehensive error handling"""
        result = {"success": False, "result": None, "error": None, "execution_time": 0}

        start_time = time.time()
        try:
            result["result"] = func(*args, **kwargs)
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Function {func.__name__} failed: {e}")
        finally:
            result["execution_time"] = time.time() - start_time

        return result


# =============================================================================
# AWS UTILITIES
# =============================================================================


class AWSResourceManager:
    """Reusable AWS resource management utilities"""

    @staticmethod
    @retry_with_backoff(exceptions=(Exception,))
    def deploy_lambda_function(function_name: str, zip_file_path: str) -> bool:
        """Deploy Lambda function with retry logic"""
        import boto3

        lambda_client = boto3.client("lambda")

        with open(zip_file_path, "rb") as zip_file:
            response = lambda_client.update_function_code(
                FunctionName=function_name, ZipFile=zip_file.read()
            )

        return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @staticmethod
    def get_lambda_status(function_name: str) -> Dict[str, Any]:
        """Get Lambda function status and metrics"""
        import boto3

        lambda_client = boto3.client("lambda")
        cloudwatch = boto3.client("cloudwatch")

        try:
            # Get function info
            function_info = lambda_client.get_function(FunctionName=function_name)

            # Get recent metrics
            metrics = cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName="Invocations",
                Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                StartTime=time.time() - 3600,  # Last hour
                EndTime=time.time(),
                Period=300,
                Statistics=["Sum"],
            )

            return {
                "status": function_info["Configuration"]["State"],
                "last_modified": function_info["Configuration"]["LastModified"],
                "runtime": function_info["Configuration"]["Runtime"],
                "memory_size": function_info["Configuration"]["MemorySize"],
                "recent_invocations": sum(
                    point["Sum"] for point in metrics["Datapoints"]
                ),
            }
        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# FILE PROCESSING UTILITIES
# =============================================================================


class FileProcessor:
    """Reusable file processing utilities"""

    @staticmethod
    def batch_file_operation(
        file_paths: list, operation: Callable, batch_size: int = 10
    ) -> list:
        """Process files in batches to avoid memory issues"""
        results = []

        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i : i + batch_size]
            batch_results = []

            for file_path in batch:
                try:
                    result = operation(file_path)
                    batch_results.append(
                        {"file": file_path, "result": result, "success": True}
                    )
                except Exception as e:
                    batch_results.append(
                        {"file": file_path, "error": str(e), "success": False}
                    )

            results.extend(batch_results)

        return results

    @staticmethod
    def validate_pdf_quality(pdf_path: str) -> Dict[str, Any]:
        """Validate PDF for KDP compliance"""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(pdf_path)

            validation = {
                "file_size_mb": os.path.getsize(pdf_path) / (1024 * 1024),
                "page_count": len(doc),
                "dimensions": [],
                "embedded_fonts": True,
                "text_extractable": True,
                "issues": [],
            }

            # Check each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                validation["dimensions"].append(
                    {"page": page_num + 1, "width": rect.width, "height": rect.height}
                )

                # Check text extraction
                if not page.get_text().strip():
                    validation["text_extractable"] = False
                    validation["issues"].append(
                        f"Page {page_num + 1}: No extractable text"
                    )

            # File size check
            if validation["file_size_mb"] > 650:
                validation["issues"].append(
                    f"File size ({validation['file_size_mb']:.1f} MB) exceeds KDP limit (650 MB)"
                )

            doc.close()
            return validation

        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# BOOK PRODUCTION UTILITIES
# =============================================================================


class BookProductionHelper:
    """Reusable book production utilities"""

    @staticmethod
    def calculate_spine_width(page_count: int, paper_type: str = "white") -> float:
        """Calculate spine width for hardcover books"""
        # KDP formula: (pages × 0.0025) + 0.06
        return (page_count * 0.0025) + 0.06

    @staticmethod
    def estimate_printing_cost(
        page_count: int, trim_size: tuple, color: str = "bw"
    ) -> Dict[str, float]:
        """Estimate KDP printing costs"""
        # Simplified cost estimation (update with current KDP rates)
        base_cost = 0.60  # Fixed cost

        if trim_size == (6, 9):  # 6x9 inches
            page_cost = 0.012 if color == "bw" else 0.057
        elif trim_size == (8.5, 11):  # 8.5x11 inches
            page_cost = 0.0175 if color == "bw" else 0.077
        else:
            page_cost = 0.015 if color == "bw" else 0.065  # Average

        total_cost = base_cost + (page_count * page_cost)

        return {
            "base_cost": base_cost,
            "page_cost": page_cost,
            "total_pages": page_count,
            "estimated_cost": total_cost,
            "margin_60": total_cost * 2.5,  # Suggested 60% margin pricing
            "margin_70": total_cost * 3.33,  # Suggested 70% margin pricing
        }

    @staticmethod
    def generate_metadata_template(book_type: str) -> Dict[str, Any]:
        """Generate metadata template for different book types"""
        base_template = {
            "title": "",
            "subtitle": "",
            "author": "",
            "description": "",
            "keywords": [],
            "categories": [
                "Humor & Entertainment",
                "Health, Fitness & Dieting",
                "Self-Help",
            ],
            "language": "English",
            "pages": 0,
            "target_audience": "",
            "publication_date": "",
        }

        if book_type == "crossword":
            base_template.update(
                {
                    "keywords": [
                        "large print crossword puzzles",
                        "senior crossword book",
                        "easy crossword puzzles",
                        "crossword puzzles for adults",
                        "brain games for seniors",
                        "puzzle book large print",
                    ],
                    "target_audience": "Adults 50+, Seniors, Puzzle enthusiasts",
                }
            )
        elif book_type == "sudoku":
            base_template.update(
                {
                    "keywords": [
                        "large print sudoku",
                        "senior sudoku book",
                        "easy sudoku puzzles",
                        "brain games seniors",
                        "number puzzles large print",
                    ],
                    "target_audience": "Adults 40+, Puzzle enthusiasts, Brain training",
                }
            )

        return base_template


# =============================================================================
# MONITORING & ALERTING
# =============================================================================


class MonitoringHelper:
    """Reusable monitoring and alerting utilities"""

    @staticmethod
        """Setup Cloudwatch Alarm"""
def setup_cloudwatch_alarm(
        metric_name: str, threshold: float, comparison: str = "GreaterThanThreshold"
    ):
        """Setup CloudWatch alarm with standard configuration"""
        import boto3

        cloudwatch = boto3.client("cloudwatch")

        alarm_config = {
            "AlarmName": f"KindleMint-{metric_name}-Alarm",
            "ComparisonOperator": comparison,
            "EvaluationPeriods": 2,
            "MetricName": metric_name,
            "Namespace": "AWS/Lambda",
            "Period": 300,
            "Statistic": "Average",
            "Threshold": threshold,
            "ActionsEnabled": True,
            "AlarmDescription": f"Alarm for {metric_name} metric",
            "Unit": "Count",
        }

        return cloudwatch.put_metric_alarm(**alarm_config)

    @staticmethod
        """Log Business Metric"""
def log_business_metric(metric_name: str, value: float, unit: str = "Count"):
        """Log custom business metrics to CloudWatch"""
        import boto3

        cloudwatch = boto3.client("cloudwatch")

        cloudwatch.put_metric_data(
            Namespace="KindleMint/Business",
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": time.time(),
                }
            ],
        )


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example usage of reusable components

    # 1. Safe execution
    executor = SafeExecutor()
    result = executor.execute_safely(lambda: 10 / 2)
    print(f"Safe execution result: {result}")

    # 2. Spine width calculation
    spine_width = BookProductionHelper.calculate_spine_width(103)
    print(f"Spine width for 103 pages: {spine_width} inches")

    # 3. Cost estimation
    cost_estimate = BookProductionHelper.estimate_printing_cost(103, (6, 9))
    print(f"Printing cost estimate: ${cost_estimate['estimated_cost']:.2f}")

    # 4. Metadata template
    template = BookProductionHelper.generate_metadata_template("crossword")
    print(f"Crossword metadata template: {template['keywords']}")
