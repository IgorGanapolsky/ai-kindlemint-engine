#!/usr/bin/env python3
"""
AWS Infrastructure Status Checker
Generates status badges and health checks for AWS services
"""

import json
import subprocess
from datetime import datetime
from typing import Any, Dict


def get_aws_region() -> str:
    """Get the AWS region from configuration"""
    try:
        result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "us-east-1"


def check_cloudformation_stack(stack_name: str, region: str = None) -> Dict[str, Any]:
    """Check CloudFormation stack status"""
    region = region or get_aws_region()

    try:
        result = subprocess.run(
            [
                "aws",
                "--profile",
                "kindlemint-keys",
                "cloudformation",
                "describe-stacks",
                "--stack-name",
                stack_name,
                "--region",
                region,
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
                    "last_updated": stack.get(
                        "LastUpdatedTime", stack.get("CreationTime")
                    ),
                    "outputs": stack.get("Outputs", []),
                }

        return {"status": "unavailable", "error": result.stderr or "Unknown error"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_lambda_functions(region: str = None) -> Dict[str, Any]:
    """Check Lambda functions status"""
    region = region or get_aws_region()

    try:
        result = subprocess.run(
            [
                "aws",
                "--profile",
                "kindlemint-keys",
                "lambda",
                "list-functions",
                "--region",
                region,
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            functions = data.get("Functions", [])

            # Filter for KindleMint functions
            kindlemint_functions = [
                f
                for f in functions
                if "kindlemint" in f.get("FunctionName", "").lower()
            ]

            return {
                "status": "available" if kindlemint_functions else "unavailable",
                "function_count": len(kindlemint_functions),
                "functions": [
                    {
                        "name": f.get("FunctionName"),
                        "runtime": f.get("Runtime"),
                        "last_modified": f.get("LastModified"),
                    }
                    for f in kindlemint_functions
                ],
            }

        return {"status": "unavailable", "error": result.stderr or "Unknown error"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_status_summary() -> Dict[str, Any]:
    """Generate comprehensive AWS status summary"""
    region = get_aws_region()

    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "region": region,
        "services": {},
    }

    # Check CloudFormation stacks
    cf_stacks = [
        "Sentry-Monitoring-Stack",
        "autonomous-orchestration-production",
    ]

    for stack_name in cf_stacks:
        status["services"][f"cloudformation_{stack_name}"] = check_cloudformation_stack(
            stack_name, region
        )

    # Check Lambda functions
    status["services"]["lambda"] = check_lambda_functions(region)

    # Overall health
    all_services = status["services"]
    healthy_services = sum(
        1 for s in all_services.values() if s.get("status") == "available"
    )
    total_services = len(all_services)

    status["overall"] = {
        "healthy_services": healthy_services,
        "total_services": total_services,
        "health_percentage": (
            round((healthy_services / total_services) * 100, 1)
            if total_services > 0
            else 0
        ),
        "status": (
            "healthy"
            if healthy_services == total_services
            else "degraded" if healthy_services > 0 else "down"
        ),
    }

    return status


def generate_badge_json(status: Dict[str, Any]) -> Dict[str, Any]:
    """Generate GitHub badge JSON"""
    overall = status.get("overall", {})
    health_pct = overall.get("health_percentage", 0)

    if health_pct == 100:
        color = "brightgreen"
        message = "Operational"
    elif health_pct >= 80:
        color = "green"
        message = "Mostly Operational"
    elif health_pct >= 60:
        color = "yellow"
        message = "Degraded"
    elif health_pct > 0:
        color = "orange"
        message = "Partial Outage"
    else:
        color = "red"
        message = "Down"

    return {
        "schemaVersion": 1,
        "label": "AWS Infrastructure",
        "message": f"{message} ({health_pct}%)",
        "color": color,
        "cacheSeconds": 300,
    }


def main():
    """Main execution"""
    print("🔍 Checking AWS Infrastructure Status...")

    # Generate status summary
    try:
        status = generate_status_summary()

        # Save status file
        with open("aws_status.json", "w") as f:
            json.dump(status, f, indent=2, default=str)

        # Generate badge JSON
        badge = generate_badge_json(status)
        with open("aws_badge.json", "w") as f:
            json.dump(badge, f, indent=2)

        # Print summary
        overall = status.get("overall", {})
        print(f"✅ Status: {overall.get('status', 'unknown')}")
        print(f"📊 Health: {overall.get('health_percentage', 0)}%")
        print(
            f"🔧 Services: {overall.get('healthy_services', 0)
                           }/{overall.get('total_services', 0)}"
        )

        # Print service details
        for service_name, service_status in status.get("services", {}).items():
            status_emoji = "✅" if service_status.get(
                "status") == "available" else "❌"
            print(
                f"  {status_emoji} {service_name}: {
                    service_status.get('status', 'unknown')}"
            )

        return status

    except Exception as e:
        print(f"❌ Error checking AWS status: {e}")
        return None


if __name__ == "__main__":
    main()
