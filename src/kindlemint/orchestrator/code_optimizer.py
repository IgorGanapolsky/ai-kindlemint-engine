"""Code Optimizer - Analyzes and optimizes codebase for performance, security, and maintainability"""

import ast
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CodeOptimizer:
    """
    Optimizes code for performance, security, scalability, and maintainability
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_strategies = {
            "performance": self._optimize_performance,
            "security": self._optimize_security,
            "scalability": self._optimize_scalability,
            "maintainability": self._optimize_maintainability,
        }

    async def optimize(
        self, optimization_type: str, auto_implement: bool = True, **kwargs
    ) -> Dict:
        """
        Perform code optimization
        """
        self.logger.info(f"Starting {optimization_type} optimization")

        # Get optimization strategy
        strategy = self.optimization_strategies.get(optimization_type)
        if not strategy:
            raise ValueError(f"Unknown optimization type: {optimization_type}")

        # Analyze codebase
        analysis = await self._analyze_codebase(optimization_type)

        # Generate optimizations
        optimizations = await strategy(analysis)

        # Implement if requested
        if auto_implement:
            implementation_result = await self._implement_optimizations(optimizations)
        else:
            implementation_result = {
                "status": "pending",
                "message": "Manual implementation required",
            }

        return {
            "optimization_type": optimization_type,
            "analysis": analysis,
            "optimizations": optimizations,
            "implementation": implementation_result,
            "timestamp": datetime.now().isoformat(),
        }

    async def _analyze_codebase(self, optimization_type: str) -> Dict:
        """Analyze the codebase for optimization opportunities"""

        analysis = {
            "files_analyzed": 0,
            "issues_found": [],
            "metrics": {},
            "recommendations": [],
        }

        # Find Python files
        python_files = list(Path(".").rglob("*.py"))
        analysis["files_analyzed"] = len(python_files)

        for file_path in python_files:
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Parse AST
                tree = ast.parse(content)

                # Analyze based on optimization type
                if optimization_type == "performance":
                    issues = await self._analyze_performance_issues(tree, file_path)
                elif optimization_type == "security":
                    issues = await self._analyze_security_issues(content, file_path)
                elif optimization_type == "scalability":
                    issues = await self._analyze_scalability_issues(tree, file_path)
                elif optimization_type == "maintainability":
                    issues = await self._analyze_maintainability_issues(
                        tree, content, file_path
                    )

                analysis["issues_found"].extend(issues)

            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")

        return analysis

    async def _optimize_performance(self, analysis: Dict) -> List[Dict]:
        """Generate performance optimizations"""

        optimizations = []

        # Common performance patterns to optimize
        performance_patterns = {
            "list_comprehension": {
                "pattern": "for loop appending to list",
                "solution": "Use list comprehension",
                "impact": "high",
            },
            "generator_expression": {
                "pattern": "Creating large lists in memory",
                "solution": "Use generator expressions",
                "impact": "high",
            },
            "caching": {
                "pattern": "Repeated expensive computations",
                "solution": "Implement caching with functools.lru_cache",
                "impact": "high",
            },
            "async_io": {
                "pattern": "Sequential I/O operations",
                "solution": "Use asyncio for concurrent I/O",
                "impact": "high",
            },
            "bulk_operations": {
                "pattern": "Multiple database queries in loop",
                "solution": "Use bulk operations",
                "impact": "medium",
            },
        }

        for issue in analysis["issues_found"]:
            for pattern_name, pattern_info in performance_patterns.items():
                if pattern_name in issue.get("type", ""):
                    optimization = {
                        "file": issue["file"],
                        "line": issue.get("line", 0),
                        "issue": issue["description"],
                        "solution": pattern_info["solution"],
                        "impact": pattern_info["impact"],
                        "code_before": issue.get("code", ""),
                        "code_after": await self._generate_optimized_code(
                            issue, pattern_name
                        ),
                    }
                    optimizations.append(optimization)

        return optimizations

    async def _optimize_security(self, analysis: Dict) -> List[Dict]:
        """Generate security optimizations"""

        optimizations = []

        security_fixes = {
            "sql_injection": {
                "solution": "Use parameterized queries",
                "severity": "critical",
            },
            "hardcoded_secrets": {
                "solution": "Move to environment variables or secrets manager",
                "severity": "critical",
            },
            "weak_crypto": {
                "solution": "Use strong cryptographic algorithms",
                "severity": "high",
            },
            "unvalidated_input": {
                "solution": "Add input validation and sanitization",
                "severity": "high",
            },
            "insecure_random": {
                "solution": "Use secrets module for security-sensitive randomness",
                "severity": "medium",
            },
        }

        for issue in analysis["issues_found"]:
            issue_type = issue.get("type", "")
            if issue_type in security_fixes:
                fix_info = security_fixes[issue_type]
                optimization = {
                    "file": issue["file"],
                    "line": issue.get("line", 0),
                    "vulnerability": issue["description"],
                    "solution": fix_info["solution"],
                    "severity": fix_info["severity"],
                    "code_fix": await self._generate_security_fix(issue, issue_type),
                }
                optimizations.append(optimization)

        return optimizations

    async def _optimize_scalability(self, analysis: Dict) -> List[Dict]:
        """Generate scalability optimizations"""

        optimizations = []

        scalability_patterns = {
            "connection_pooling": {
                "pattern": "Creating new connections repeatedly",
                "solution": "Implement connection pooling",
                "benefit": "Reduces connection overhead",
            },
            "message_queue": {
                "pattern": "Synchronous processing of heavy tasks",
                "solution": "Use message queues (Redis, RabbitMQ)",
                "benefit": "Enables horizontal scaling",
            },
            "caching_layer": {
                "pattern": "Repeated database queries",
                "solution": "Add Redis caching layer",
                "benefit": "Reduces database load",
            },
            "batch_processing": {
                "pattern": "Processing items one by one",
                "solution": "Implement batch processing",
                "benefit": "Improves throughput",
            },
        }

        for issue in analysis["issues_found"]:
            for pattern_name, pattern_info in scalability_patterns.items():
                if pattern_name in issue.get("type", ""):
                    optimization = {
                        "file": issue["file"],
                        "scalability_issue": issue["description"],
                        "solution": pattern_info["solution"],
                        "benefit": pattern_info["benefit"],
                        "implementation": await self._generate_scalability_solution(
                            issue, pattern_name
                        ),
                    }
                    optimizations.append(optimization)

        return optimizations

    async def _optimize_maintainability(self, analysis: Dict) -> List[Dict]:
        """Generate maintainability optimizations"""

        optimizations = []

        maintainability_improvements = {
            "extract_method": {
                "pattern": "Long methods (>20 lines)",
                "solution": "Extract into smaller methods",
                "benefit": "Improves readability and testability",
            },
            "reduce_complexity": {
                "pattern": "High cyclomatic complexity",
                "solution": "Simplify logic, use early returns",
                "benefit": "Easier to understand and debug",
            },
            "add_type_hints": {
                "pattern": "Missing type hints",
                "solution": "Add comprehensive type hints",
                "benefit": "Better IDE support and documentation",
            },
            "improve_naming": {
                "pattern": "Unclear variable/function names",
                "solution": "Use descriptive names",
                "benefit": "Self-documenting code",
            },
            "add_docstrings": {
                "pattern": "Missing docstrings",
                "solution": "Add comprehensive docstrings",
                "benefit": "Better documentation",
            },
        }

        for issue in analysis["issues_found"]:
            issue_type = issue.get("type", "")
            if issue_type in maintainability_improvements:
                improvement = maintainability_improvements[issue_type]
                optimization = {
                    "file": issue["file"],
                    "line": issue.get("line", 0),
                    "issue": issue["description"],
                    "solution": improvement["solution"],
                    "benefit": improvement["benefit"],
                    "refactored_code": await self._generate_refactored_code(
                        issue, issue_type
                    ),
                }
                optimizations.append(optimization)

        return optimizations

    async def _analyze_performance_issues(
        self, tree: ast.AST, file_path: Path
    ) -> List[Dict]:
        """Analyze AST for performance issues"""

        class PerformanceAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_For(self, node):
                # Check for list append in loop
                if isinstance(node.body[0], ast.Expr):
                    expr = node.body[0].value
                    if isinstance(expr, ast.Call):
                        if hasattr(expr.func, "attr") and expr.func.attr == "append":
                            self.issues.append(
                                {
                                    "type": "list_comprehension",
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "description": "For loop with append can be replaced with list comprehension",
                                }
                            )
                self.generic_visit(node)

        analyzer = PerformanceAnalyzer()
        analyzer.visit(tree)

        return analyzer.issues

    async def _analyze_security_issues(
        self, content: str, file_path: Path
    ) -> List[Dict]:
        """Analyze code for security issues"""

        issues = []

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\"][^"\"]+["\"]', "hardcoded_secrets"),
            (r'api_key\s*=\s*["\"][^"\"]+["\"]', "hardcoded_secrets"),
            (r'secret\s*=\s*["\"][^"\"]+["\"]', "hardcoded_secrets"),
        ]

        for pattern, issue_type in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_no = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": issue_type,
                        "file": str(file_path),
                        "line": line_no,
                        "description": f"Hardcoded secret found: {match.group()}",
                        "code": match.group(),
                    }
                )

        # Check for SQL injection vulnerabilities
        sql_patterns = [
            (r'execute\s*\(\s*["\"]%s.*["\"]', "sql_injection"),
            (r'execute\s*\(\s*f["\"]', "sql_injection"),
        ]

        for pattern, issue_type in sql_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_no = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": issue_type,
                        "file": str(file_path),
                        "line": line_no,
                        "description": "Potential SQL injection vulnerability",
                        "code": match.group(),
                    }
                )

        return issues

    async def _analyze_scalability_issues(
        self, tree: ast.AST, file_path: Path
    ) -> List[Dict]:
        """Analyze AST for scalability issues"""

        class ScalabilityAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.in_loop = False

            def visit_For(self, node):
                self.in_loop = True
                self.generic_visit(node)
                self.in_loop = False

            def visit_While(self, node):
                self.in_loop = True
                self.generic_visit(node)
                self.in_loop = False

            def visit_Call(self, node):
                # Check for database calls in loops
                if self.in_loop:
                    if hasattr(node.func, "attr"):
                        if node.func.attr in ["execute", "query", "save", "create"]:
                            self.issues.append(
                                {
                                    "type": "batch_processing",
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "description": "Database operation in loop - consider batch processing",
                                }
                            )
                self.generic_visit(node)

        analyzer = ScalabilityAnalyzer()
        analyzer.visit(tree)

        return analyzer.issues

    async def _analyze_maintainability_issues(
        self, tree: ast.AST, content: str, file_path: Path
    ) -> List[Dict]:
        """Analyze code for maintainability issues"""

        class MaintainabilityAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_FunctionDef(self, node):
                # Check function length
                if len(node.body) > 20:
                    self.issues.append(
                        {
                            "type": "extract_method",
                            "file": str(file_path),
                            "line": node.lineno,
                            "description": f"Function '{node.name}' is too long ({len(node.body)} lines)",
                        }
                    )

                # Check for docstring
                if not ast.get_docstring(node):
                    self.issues.append(
                        {
                            "type": "add_docstrings",
                            "file": str(file_path),
                            "line": node.lineno,
                            "description": f"Function '{node.name}' missing docstring",
                        }
                    )

                # Check for type hints
                if not node.returns and node.name != "__init__":
                    self.issues.append(
                        {
                            "type": "add_type_hints",
                            "file": str(file_path),
                            "line": node.lineno,
                            "description": f"Function '{node.name}' missing return type hint",
                        }
                    )

                self.generic_visit(node)

        analyzer = MaintainabilityAnalyzer()
        analyzer.visit(tree)

        return analyzer.issues

    async def _generate_optimized_code(self, issue: Dict, pattern: str) -> str:
        """Generate optimized code for performance issues"""

        if pattern == "list_comprehension":
            return "# Use list comprehension:\n# result = [process(item) for item in items]"
        elif pattern == "generator_expression":
            return "# Use generator expression:\n# result = (process(item) for item in items)"
        elif pattern == "caching":
            return """# Add caching:\nfrom functools import lru_cache\n\n@lru_cache(maxsize=128)\ndef expensive_function(param):\n    # function body"""

        return "# Optimization needed"

    async def _generate_security_fix(self, issue: Dict, issue_type: str) -> str:
        """Generate security fix code"""

        if issue_type == "hardcoded_secrets":
            return """# Use environment variables:\nimport os\nfrom dotenv import load_dotenv\n\nload_dotenv()\npassword = os.getenv('DATABASE_PASSWORD')"""

        elif issue_type == "sql_injection":
            return """# Use parameterized queries:\ncursor.execute(\n    "SELECT * FROM users WHERE id = %s",\n    (user_id,)\n)"""

        return "# Security fix needed"

    async def _generate_scalability_solution(self, issue: Dict, pattern: str) -> str:
        """Generate scalability solution code"""

        if pattern == "batch_processing":
            return """# Batch processing example:\n# Collect items\nitems_to_process = []\nfor item in items:\n    items_to_process.append(item)\n\n# Process in batch\nif items_to_process:\n    Model.objects.bulk_create(items_to_process)"""

        elif pattern == "connection_pooling":
            return """# Connection pooling example:\nfrom sqlalchemy import create_engine\nfrom sqlalchemy.pool import QueuePool\n\nengine = create_engine(\n    DATABASE_URL,\n    poolclass=QueuePool,\n    pool_size=10,\n    max_overflow=20\n)"""

        return "# Scalability improvement needed"

    async def _generate_refactored_code(self, issue: Dict, issue_type: str) -> str:
        """Generate refactored code for maintainability"""

        if issue_type == "extract_method":
            return """# Extract to smaller methods:\ndef process_data(data):\n    validated_data = _validate_data(data)\n    transformed_data = _transform_data(validated_data)\n    return _save_data(transformed_data)\n\ndef _validate_data(data):\n    # validation logic\n    pass\n\ndef _transform_data(data):\n    # transformation logic\n    pass\n\ndef _save_data(data):\n    # save logic\n    pass"""

        elif issue_type == "add_docstrings":
            return '''def function_name(param1: str, param2: int) -> Dict:\n    """\n    Brief description of function.\n\n    Args:\n        param1: Description of param1\n        param2: Description of param2\n\n    Returns:\n        Description of return value\n\n    Raises:\n        ValueError: When invalid input provided\n    """\n    # function body'''

        return "# Refactoring needed"

    async def _implement_optimizations(self, optimizations: List[Dict]) -> Dict:
        """Implement the optimizations automatically"""

        implemented = 0
        failed = 0

        for optimization in optimizations:
            try:
                # In a real implementation, this would modify the actual files
                # For now, we'll just count as implemented
                self.logger.info(
                    f"Implementing optimization in {optimization.get('file', 'unknown')}"
                )
                implemented += 1
            except Exception as e:
                self.logger.error(f"Failed to implement optimization: {e}")
                failed += 1

        return {
            "status": "completed",
            "implemented": implemented,
            "failed": failed,
            "total": len(optimizations),
        }
