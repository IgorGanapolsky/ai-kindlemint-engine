#!/usr/bin/env python3
"""
Test AWS deployment status and functionality
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any


def check_stack_status(
    stack_name: str = "kindlemint-autonomous-orchestration",
) -> Dict[str, Any]:
    """Check CloudFormation stack status"""
    try:
        # Use AWS CLI to check stack status
        result = subprocess.run(
            [
                "aws",
                "cloudformation",
                "describe-stacks",
                "--stack-name",
                stack_name,
                "--region",
                "us-east-1",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("Stacks"):
                stack = data["Stacks"][0]
                return {
                    "status": "available",
                    "stack_status": stack.get("StackStatus"),
                    "stack_name": stack.get("StackName"),
                    "creation_time": stack.get("CreationTime"),
                    "last_updated": stack.get("LastUpdatedTime"),
                    "outputs": stack.get("Outputs", []),
                }

        return {"status": "unavailable", "error": result.stderr or "Stack not found"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def test_lambda_functions(stack_outputs: list) -> Dict[str, Any]:
    """Test deployed Lambda functions"""
    results = {"ci_orchestration": None, "alert_orchestration": None}

    # Extract function ARNs from stack outputs
    function_arns = {}
    for output in stack_outputs:
        key = output.get("OutputKey", "")
        if "Function" in key and "Arn" in key:
            function_arns[key] = output.get("OutputValue", "")

    # Test each function
    for output_key, arn in function_arns.items():
        if "CIOrchestration" in output_key:
            result = test_lambda_function(arn, "ci_orchestration")
            results["ci_orchestration"] = result
        elif "AlertOrchestration" in output_key:
            result = test_lambda_function(arn, "alert_orchestration")
            results["alert_orchestration"] = result

    return results


def test_lambda_function(arn: str, function_type: str) -> Dict[str, Any]:
    """Test a specific Lambda function"""
    try:
        function_name = arn.split(":")[-1]

        # Create test payload
        test_payload = {
            "source": "test",
            "trigger": "deployment_verification",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Invoke function
        result = subprocess.run(
            [
                "aws",
                "lambda",
                "invoke",
                "--function-name",
                function_name,
                "--region",
                "us-east-1",
                "--payload",
                json.dumps(test_payload),
                "/tmp/lambda_test_response.json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Read response
            try:
                with open("/tmp/lambda_test_response.json", "r") as f:
                    response = json.load(f)

                return {
                    "status": "success",
                    "function_name": function_name,
                    "response": response,
                    "test_time": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                return {
                    "status": "partial_success",
                    "function_name": function_name,
                    "error": f"Could not read response: {e}",
                }
        else:
            return {
                "status": "failed",
                "function_name": function_name,
                "error": result.stderr,
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_dynamodb_tables(stack_outputs: list) -> Dict[str, Any]:
    """Check DynamoDB tables"""
    results = {}

    # Extract table names from stack outputs
    for output in stack_outputs:
        key = output.get("OutputKey", "")
        if "TableName" in key:
            table_name = output.get("OutputValue", "")
            result = check_dynamodb_table(table_name)
            results[key] = result

    return results


def check_dynamodb_table(table_name: str) -> Dict[str, Any]:
    """Check a specific DynamoDB table"""
    try:
        result = subprocess.run(
            [
                "aws",
                "dynamodb",
                "describe-table",
                "--table-name",
                table_name,
                "--region",
                "us-east-1",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            table = data.get("Table", {})
            return {
                "status": "available",
                "table_name": table.get("TableName"),
                "table_status": table.get("TableStatus"),
                "creation_time": table.get("CreationDateTime"),
                "item_count": table.get("ItemCount", 0),
            }
        else:
            return {"status": "unavailable", "error": result.stderr}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    """Main test execution"""
    print("🧪 Testing AWS Infrastructure Deployment")
    print("=" * 50)

    # Check stack status
    print("\n1. Checking CloudFormation Stack...")
    stack_info = check_stack_status()

    if stack_info["status"] != "available":
        print(f"❌ Stack not available: {stack_info.get('error', 'Unknown error')}")
        return False

    stack_status = stack_info["stack_status"]
    print(f"✅ Stack Status: {stack_status}")

    if stack_status != "CREATE_COMPLETE":
        print(f"⚠️  Stack not fully deployed yet. Current status: {stack_status}")
        if stack_status == "CREATE_IN_PROGRESS":
            print("   Deployment is still in progress. Please wait and try again.")
        return False

    # Test Lambda functions
    print("\n2. Testing Lambda Functions...")
    lambda_results = test_lambda_functions(stack_info["outputs"])

    for func_type, result in lambda_results.items():
        if result:
            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"   {status_emoji} {func_type}: {result['status']}")
            if result["status"] != "success":
                print(f"      Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ⚠️  {func_type}: Not found in outputs")

    # Test DynamoDB tables
    print("\n3. Testing DynamoDB Tables...")
    dynamodb_results = check_dynamodb_tables(stack_info["outputs"])

    for table_key, result in dynamodb_results.items():
        status_emoji = "✅" if result["status"] == "available" else "❌"
        table_name = result.get("table_name", "Unknown")
        print(f"   {status_emoji} {table_name}: {result['status']}")
        if result["status"] != "available":
            print(f"      Error: {result.get('error', 'Unknown error')}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("=" * 50)

    total_tests = 1 + len(lambda_results) + len(dynamodb_results)
    passed_tests = 1  # Stack status

    # Count passed Lambda tests
    for result in lambda_results.values():
        if result and result["status"] == "success":
            passed_tests += 1

    # Count passed DynamoDB tests
    for result in dynamodb_results.values():
        if result["status"] == "available":
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("\n🎉 Deployment test PASSED! Infrastructure is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
