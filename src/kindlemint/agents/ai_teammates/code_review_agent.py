"""
AI Code Review Agent - Autonomous PR analysis with deep architectural understanding

This agent acts as a senior developer teammate, analyzing PRs with full context of:
- System architecture and design patterns
- Code quality and best practices
- Business impact and technical debt
- Integration with existing orchestrators
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import anthropic
from github import Github


@dataclass
class CodeReviewInsight:
    """Represents a code review insight with context"""

    category: str  # architecture, quality, security, business_impact
    severity: str  # critical, high, medium, low, info
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    confidence: float = 0.85
    business_impact: str = "medium"


@dataclass
class ArchitecturalPattern:
    """Represents an architectural pattern in the codebase"""

    pattern_type: str  # orchestrator, agent, integration, automation
    description: str
    files: List[str]
    consistency_score: float
    violations: List[str]


class AICodeReviewAgent:
    """
    Autonomous AI teammate that performs intelligent code reviews

    Capabilities:
    - Deep architectural understanding of orchestrator patterns
    - Business impact assessment using competitive intelligence
    - Quality analysis with professional standards integration
    - Security review with vulnerability detection
    - Technical debt and maintainability analysis
    """

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger(__name__)

        # Load architectural patterns and conventions
        self.architectural_patterns = self._load_architectural_patterns()
        self.quality_standards = self._load_quality_standards()
        self.security_patterns = self._load_security_patterns()

    def _load_architectural_patterns(self) -> Dict[str, ArchitecturalPattern]:
        """Load known architectural patterns from the codebase"""
        patterns = {
            "orchestrator_pattern": ArchitecturalPattern(
                pattern_type="orchestrator",
                description="Multi-agent orchestration with competitive intelligence",
                files=[
                    "src/kindlemint/orchestrator/competitive_intelligence_orchestrator.py",
                    "src/kindlemint/orchestrator/tactical_advantage_orchestrator.py",
                    "src/kindlemint/orchestrator/professional_quality_orchestrator.py",
                    "src/kindlemint/orchestrator/tactical_seo_orchestrator.py",
                ],
                consistency_score=0.92,
                violations=[],
            ),
            "agent_communication": ArchitecturalPattern(
                pattern_type="agent",
                description="Agent-to-agent messaging and coordination",
                files=[
                    "src/kindlemint/agents/message_protocol.py",
                    "src/kindlemint/agents/health_monitoring.py",
                    "src/kindlemint/agents/task_coordinator.py",
                ],
                consistency_score=0.88,
                violations=["Missing heartbeat in some agents"],
            ),
            "automation_pipeline": ArchitecturalPattern(
                pattern_type="automation",
                description="KDP automation with market intelligence",
                files=[
                    "src/kindlemint/automation/kdp_automation_engine.py",
                    "src/kindlemint/automation/kdp_automation_free.py",
                ],
                consistency_score=0.85,
                violations=[],
            ),
        }
        return patterns

    def _load_quality_standards(self) -> Dict[str, float]:
        """Load quality thresholds aligned with professional standards"""
        return {
            "code_complexity": 10,  # Max cyclomatic complexity
            "function_length": 50,  # Max lines per function
            "class_length": 500,  # Max lines per class
            "test_coverage": 85,  # Minimum test coverage %
            "documentation_ratio": 0.15,  # Comments to code ratio
            "type_annotation_coverage": 90,  # Type hints coverage %
        }

    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns and anti-patterns"""
        return {
            "secrets_patterns": [
                r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
            ],
            "injection_patterns": [
                r"exec\s*\(",
                r"eval\s*\(",
                r"subprocess\.call.*shell\s*=\s*True",
                r"os\.system\s*\(",
            ],
            "unsafe_patterns": [
                r"pickle\.loads?\s*\(",
                r"yaml\.load\s*\(",
                r"shell\s*=\s*True",
            ],
        }

    async def review_pull_request(self, repo_name: str, pr_number: int) -> Dict:
        """
        Comprehensive autonomous PR review with business intelligence

        Returns complete analysis including:
        - Architectural consistency assessment
        - Business impact evaluation using orchestrator intelligence
        - Security and quality analysis
        - Merge recommendation with confidence score
        """
        self.logger.info(f"🤖 Starting autonomous review of PR #{pr_number}")

        try:
            # Get PR details
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Analyze PR changes
            files_analysis = await self._analyze_changed_files(pr)
            architectural_analysis = await self._analyze_architectural_impact(
                pr, files_analysis
            )
            business_analysis = await self._analyze_business_impact(pr, files_analysis)
            security_analysis = await self._analyze_security_implications(
                pr, files_analysis
            )
            quality_analysis = await self._analyze_code_quality(pr, files_analysis)

            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(
                pr,
                {
                    "files": files_analysis,
                    "architecture": architectural_analysis,
                    "business": business_analysis,
                    "security": security_analysis,
                    "quality": quality_analysis,
                },
            )

            # Make autonomous merge decision
            merge_decision = await self._make_merge_decision(
                {
                    "pr": pr,
                    "files_analysis": files_analysis,
                    "architectural_analysis": architectural_analysis,
                    "business_analysis": business_analysis,
                    "security_analysis": security_analysis,
                    "quality_analysis": quality_analysis,
                    "ai_insights": ai_insights,
                }
            )

            review_result = {
                "pr_number": pr_number,
                "pr_title": pr.title,
                "pr_author": pr.user.login,
                "review_timestamp": datetime.now().isoformat(),
                "reviewer": "AI Code Review Agent",
                "files_analysis": files_analysis,
                "architectural_analysis": architectural_analysis,
                "business_analysis": business_analysis,
                "security_analysis": security_analysis,
                "quality_analysis": quality_analysis,
                "ai_insights": ai_insights,
                "merge_decision": merge_decision,
                "overall_score": merge_decision["confidence"],
                "recommendation": merge_decision["action"],
            }

            # Post review comment
            await self._post_review_comment(pr, review_result)

            return review_result

        except Exception as e:
            self.logger.error(f"PR review failed: {e}")
            return {"error": str(e), "pr_number": pr_number, "status": "failed"}

    async def _analyze_changed_files(self, pr) -> Dict:
        """Analyze all changed files for patterns and impact"""
        files_data = []
        total_additions = 0
        total_deletions = 0

        for file in pr.get_files():
            file_analysis = {
                "filename": file.filename,
                "status": file.status,  # added, modified, removed
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch if hasattr(file, "patch") else None,
                # Categorize by type
                "file_type": self._categorize_file_type(file.filename),
                "is_critical": self._is_critical_file(file.filename),
                "impact_level": self._assess_file_impact(file.filename, file.changes),
                # Extract specific changes
                "functions_modified": (
                    self._extract_function_changes(file.patch)
                    if hasattr(file, "patch")
                    else []
                ),
                "imports_added": (
                    self._extract_import_changes(file.patch)
                    if hasattr(file, "patch")
                    else []
                ),
                "security_sensitive": (
                    self._check_security_sensitive_changes(file.patch)
                    if hasattr(file, "patch")
                    else False
                ),
            }

            files_data.append(file_analysis)
            total_additions += file.additions
            total_deletions += file.deletions

        return {
            "total_files": len(files_data),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "files": files_data,
            "change_magnitude": self._calculate_change_magnitude(
                total_additions, total_deletions
            ),
            "risk_level": self._calculate_file_risk_level(files_data),
        }

    def _categorize_file_type(self, filename: str) -> str:
        """Categorize file by type and purpose"""
        if "/orchestrator/" in filename:
            return "orchestrator"
        elif "/agents/" in filename:
            return "agent"
        elif "/automation/" in filename:
            return "automation"
        elif "test" in filename.lower():
            return "test"
        elif filename.endswith((".md", ".rst", ".txt")):
            return "documentation"
        elif filename.endswith((".yml", ".yaml", ".json")):
            return "configuration"
        elif filename.endswith(".py"):
            return "source_code"
        else:
            return "other"

    def _is_critical_file(self, filename: str) -> bool:
        """Determine if file is critical to system operation"""
        critical_patterns = [
            "/orchestrator/",
            "/agents/message_protocol.py",
            "/agents/health_monitoring.py",
            "/automation/kdp_automation_engine.py",
            ".github/workflows/",
            "setup.py",
            "requirements.txt",
        ]
        return any(pattern in filename for pattern in critical_patterns)

    def _assess_file_impact(self, filename: str, changes: int) -> str:
        """Assess the impact level of file changes"""
        if self._is_critical_file(filename):
            if changes > 100:
                return "high"
            elif changes > 50:
                return "medium"
            else:
                return "low"
        else:
            if changes > 200:
                return "medium"
            else:
                return "low"

    def _extract_function_changes(self, patch: str) -> List[str]:
        """Extract function/method names that were modified"""
        if not patch:
            return []

        function_pattern = r"^[+-].*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        functions = []

        for line in patch.split("\n"):
            match = re.search(function_pattern, line)
            if match:
                functions.append(match.group(1))

        return list(set(functions))

    def _extract_import_changes(self, patch: str) -> List[str]:
        """Extract import changes"""
        if not patch:
            return []

        import_pattern = r"^[+].*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_.]*)"
        imports = []

        for line in patch.split("\n"):
            match = re.search(import_pattern, line)
            if match:
                imports.append(match.group(1))

        return list(set(imports))

    def _check_security_sensitive_changes(self, patch: str) -> bool:
        """Check for security-sensitive changes"""
        if not patch:
            return False

        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, patch, re.IGNORECASE):
                    return True

        return False

    def _calculate_change_magnitude(self, additions: int, deletions: int) -> str:
        """Calculate overall change magnitude"""
        total_changes = additions + deletions

        if total_changes > 1000:
            return "major"
        elif total_changes > 300:
            return "significant"
        elif total_changes > 100:
            return "moderate"
        else:
            return "minor"

    def _calculate_file_risk_level(self, files_data: List[Dict]) -> str:
        """Calculate overall risk level based on files changed"""
        high_risk_count = sum(
            1 for f in files_data if f["impact_level"] == "high")
        critical_files_count = sum(1 for f in files_data if f["is_critical"])

        if high_risk_count > 2 or critical_files_count > 3:
            return "high"
        elif high_risk_count > 0 or critical_files_count > 1:
            return "medium"
        else:
            return "low"

    async def _analyze_architectural_impact(self, pr, files_analysis: Dict) -> Dict:
        """Analyze impact on system architecture"""
        orchestrator_files = [
            f for f in files_analysis["files"] if f["file_type"] == "orchestrator"
        ]
        agent_files = [f for f in files_analysis["files"]
                       if f["file_type"] == "agent"]

        architectural_impact = {
            "orchestrator_changes": len(orchestrator_files),
            "agent_changes": len(agent_files),
            "pattern_violations": [],
            "consistency_score": 0.85,  # Default
            "integration_risk": "low",
        }

        # Check for pattern violations
        if orchestrator_files:
            violations = await self._check_orchestrator_patterns(orchestrator_files)
            architectural_impact["pattern_violations"].extend(violations)

        if agent_files:
            violations = await self._check_agent_patterns(agent_files)
            architectural_impact["pattern_violations"].extend(violations)

        # Calculate consistency score
        if architectural_impact["pattern_violations"]:
            architectural_impact["consistency_score"] -= (
                len(architectural_impact["pattern_violations"]) * 0.1
            )
            architectural_impact["consistency_score"] = max(
                0.5, architectural_impact["consistency_score"]
            )

        # Assess integration risk
        if orchestrator_files and agent_files:
            architectural_impact["integration_risk"] = "medium"
        elif len(orchestrator_files) > 2:
            architectural_impact["integration_risk"] = "high"

        return architectural_impact

    async def _check_orchestrator_patterns(
        self, orchestrator_files: List[Dict]
    ) -> List[str]:
        """Check orchestrator-specific patterns"""
        violations = []

        for file_data in orchestrator_files:
            filename = file_data["filename"]

            # Check for required methods in orchestrators
            if file_data.get("patch"):
                patch_content = file_data["patch"]

                # Check for async methods (orchestrators should be async)
                if "def " in patch_content and "async def" not in patch_content:
                    violations.append(
                        f"{filename}: Orchestrator methods should be async"
                    )

                # Check for proper error handling
                if "try:" not in patch_content and "except" not in patch_content:
                    violations.append(
                        f"{filename}: Missing error handling in orchestrator"
                    )

                # Check for logging
                if "self.logger" not in patch_content:
                    violations.append(
                        f"{filename}: Orchestrator should include logging"
                    )

        return violations

    async def _check_agent_patterns(self, agent_files: List[Dict]) -> List[str]:
        """Check agent-specific patterns"""
        violations = []

        for file_data in agent_files:
            filename = file_data["filename"]

            # Check for message protocol usage
            if "message_protocol" in filename or "coordinator" in filename:
                if file_data.get("patch"):
                    patch_content = file_data["patch"]

                    # Check for proper message handling
                    if (
                        "MessageType" not in patch_content
                        and "Message" in patch_content
                    ):
                        violations.append(
                            f"{filename}: Should use MessageType enum")

        return violations

    async def _analyze_business_impact(self, pr, files_analysis: Dict) -> Dict:
        """Analyze business impact using orchestrator intelligence"""

        # Categorize changes by business function
        automation_changes = [
            f for f in files_analysis["files"] if "automation" in f["filename"]
        ]
        orchestrator_changes = [
            f for f in files_analysis["files"] if "orchestrator" in f["filename"]
        ]
        quality_changes = [
            f
            for f in files_analysis["files"]
            if "quality" in f["filename"] or "test" in f["filename"]
        ]

        business_impact = {
            "revenue_impact": "low",
            "automation_impact": "none",
            "quality_impact": "none",
            "competitive_impact": "none",
            "user_experience_impact": "none",
            "risk_to_operations": "low",
        }

        # Assess automation impact
        if automation_changes:
            business_impact["automation_impact"] = (
                "high" if len(automation_changes) > 1 else "medium"
            )
            # Automation affects revenue
            business_impact["revenue_impact"] = "medium"

        # Assess orchestrator impact
        if orchestrator_changes:
            business_impact["competitive_impact"] = "high"
            business_impact["revenue_impact"] = "medium"

        # Assess quality impact
        if quality_changes:
            business_impact["quality_impact"] = "high"
            business_impact["user_experience_impact"] = "medium"

        # Calculate overall business risk
        high_impact_areas = sum(
            1 for impact in business_impact.values() if impact == "high"
        )
        if high_impact_areas > 2:
            business_impact["risk_to_operations"] = "high"
        elif high_impact_areas > 0:
            business_impact["risk_to_operations"] = "medium"

        return business_impact

    async def _analyze_security_implications(self, pr, files_analysis: Dict) -> Dict:
        """Analyze security implications of changes"""
        security_analysis = {
            "security_risk": "low",
            "vulnerabilities_detected": [],
            "secrets_exposed": False,
            "injection_risks": [],
            "authentication_changes": False,
            "data_access_changes": False,
        }

        for file_data in files_analysis["files"]:
            if file_data.get("patch"):
                patch = file_data["patch"]
                filename = file_data["filename"]

                # Check for secrets
                for pattern in self.security_patterns["secrets_patterns"]:
                    if re.search(pattern, patch, re.IGNORECASE):
                        security_analysis["secrets_exposed"] = True
                        security_analysis["vulnerabilities_detected"].append(
                            f"Potential secret in {filename}"
                        )

                # Check for injection risks
                for pattern in self.security_patterns["injection_patterns"]:
                    if re.search(pattern, patch, re.IGNORECASE):
                        security_analysis["injection_risks"].append(
                            f"Injection risk in {filename}"
                        )

                # Check for unsafe patterns
                for pattern in self.security_patterns["unsafe_patterns"]:
                    if re.search(pattern, patch, re.IGNORECASE):
                        security_analysis["vulnerabilities_detected"].append(
                            f"Unsafe pattern in {filename}"
                        )

                # Check for authentication changes
                if any(
                    auth_keyword in patch.lower()
                    for auth_keyword in ["password", "token", "auth", "login"]
                ):
                    security_analysis["authentication_changes"] = True

                # Check for data access changes
                if any(
                    data_keyword in patch.lower()
                    for data_keyword in ["database", "sql", "query", "api_key"]
                ):
                    security_analysis["data_access_changes"] = True

        # Calculate overall security risk
        risk_factors = [
            security_analysis["secrets_exposed"],
            len(security_analysis["injection_risks"]) > 0,
            len(security_analysis["vulnerabilities_detected"]) > 0,
            security_analysis["authentication_changes"],
            security_analysis["data_access_changes"],
        ]

        risk_count = sum(risk_factors)
        if risk_count >= 3:
            security_analysis["security_risk"] = "high"
        elif risk_count >= 1:
            security_analysis["security_risk"] = "medium"

        return security_analysis

    async def _analyze_code_quality(self, pr, files_analysis: Dict) -> Dict:
        """Analyze code quality metrics"""
        quality_analysis = {
            "quality_score": 85,  # Default
            "complexity_issues": [],
            "style_issues": [],
            "documentation_gaps": [],
            "test_coverage_impact": "neutral",
            "maintainability_score": 80,
        }

        for file_data in files_analysis["files"]:
            if file_data["file_type"] == "source_code" and file_data.get("patch"):
                patch = file_data["patch"]
                filename = file_data["filename"]

                # Check for complexity issues
                if file_data["changes"] > self.quality_standards["function_length"]:
                    quality_analysis["complexity_issues"].append(
                        f"Large function changes in {filename}"
                    )

                # Check for documentation
                if '"""' not in patch and file_data["additions"] > 20:
                    quality_analysis["documentation_gaps"].append(
                        f"Missing docstrings in {filename}"
                    )

                # Check for test coverage
                if "test" in filename:
                    quality_analysis["test_coverage_impact"] = "positive"
                elif file_data["file_type"] == "source_code" and "test" not in filename:
                    # Check if there are corresponding test files being added
                    test_file_exists = any(
                        f["filename"].replace(".py", "_test.py")
                        == filename.replace(".py", "_test.py")
                        for f in files_analysis["files"]
                        if "test" in f["filename"]
                    )
                    if not test_file_exists and file_data["additions"] > 50:
                        quality_analysis["test_coverage_impact"] = "negative"

        # Calculate quality score adjustments
        quality_penalties = (
            len(quality_analysis["complexity_issues"]) * 5
            + len(quality_analysis["documentation_gaps"]) * 3
            + (10 if quality_analysis["test_coverage_impact"] == "negative" else 0)
        )

        quality_analysis["quality_score"] = max(50, 85 - quality_penalties)
        quality_analysis["maintainability_score"] = max(
            40, 80 - quality_penalties)

        return quality_analysis

    async def _generate_ai_insights(self, pr, analysis_data: Dict) -> Dict:
        """Generate AI-powered insights using Claude"""

        # Prepare context for AI analysis
        context = f"""
        Analyzing Pull Request: {pr.title}
        Author: {pr.user.login}
        Files Changed: {analysis_data['files']['total_files']}
        Total Changes: +{analysis_data['files']['total_additions']} -{analysis_data['files']['total_deletions']}
        
        Architectural Analysis:
        - Orchestrator changes: {analysis_data['architecture']['orchestrator_changes']}
        - Pattern violations: {len(analysis_data['architecture']['pattern_violations'])}
        - Integration risk: {analysis_data['architecture']['integration_risk']}
        
        Business Impact:
        - Revenue impact: {analysis_data['business']['revenue_impact']}
        - Automation impact: {analysis_data['business']['automation_impact']}
        - Competitive impact: {analysis_data['business']['competitive_impact']}
        
        Security Analysis:
        - Security risk: {analysis_data['security']['security_risk']}
        - Vulnerabilities: {len(analysis_data['security']['vulnerabilities_detected'])}
        
        Quality Analysis:
        - Quality score: {analysis_data['quality']['quality_score']}
        - Test coverage impact: {analysis_data['quality']['test_coverage_impact']}
        """

        prompt = f"""
        As a senior AI development teammate reviewing this PR for an AI-KindleMint orchestration system, provide strategic insights:

        {context}

        Please analyze:
        1. Strategic value of these changes to the business
        2. Technical risks and mitigation strategies
        3. Integration impact with existing orchestrators
        4. Long-term maintainability considerations
        5. Specific recommendation on merge decision

        Respond with actionable insights in a concise, technical manner.
        """

        try:
            response = await self.anthropic.messages.acreate(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            ai_insights = {
                "strategic_assessment": response.content[0].text,
                "confidence": 0.85,
                "key_recommendations": self._extract_recommendations(
                    response.content[0].text
                ),
                "risk_mitigation": self._extract_risk_mitigation(
                    response.content[0].text
                ),
            }

        except Exception as e:
            self.logger.warning(f"AI insights generation failed: {e}")
            ai_insights = {
                "strategic_assessment": "AI analysis unavailable",
                "confidence": 0.5,
                "key_recommendations": ["Manual review recommended"],
                "risk_mitigation": ["Standard review process"],
            }

        return ai_insights

    def _extract_recommendations(self, ai_response: str) -> List[str]:
        """Extract key recommendations from AI response"""
        # Simple keyword-based extraction - could be enhanced with NLP
        recommendations = []

        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "must"]
            ):
                recommendations.append(line.strip())

        return recommendations[:5]  # Top 5 recommendations

    def _extract_risk_mitigation(self, ai_response: str) -> List[str]:
        """Extract risk mitigation strategies from AI response"""
        mitigation = []

        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["mitigate", "reduce", "prevent", "ensure"]
            ):
                mitigation.append(line.strip())

        return mitigation[:3]  # Top 3 mitigation strategies

    async def _make_merge_decision(self, analysis_data: Dict) -> Dict:
        """Make autonomous merge decision based on comprehensive analysis"""

        pr = analysis_data["pr"]
        files_analysis = analysis_data["files_analysis"]
        architectural_analysis = analysis_data["architectural_analysis"]
        business_analysis = analysis_data["business_analysis"]
        security_analysis = analysis_data["security_analysis"]
        quality_analysis = analysis_data["quality_analysis"]
        ai_insights = analysis_data["ai_insights"]

        # Initialize decision factors
        decision_factors = {
            "size_factor": 0.0,
            "quality_factor": 0.0,
            "security_factor": 0.0,
            "architecture_factor": 0.0,
            "business_factor": 0.0,
            "ai_factor": 0.0,
        }

        # Size factor (smaller changes are safer)
        change_magnitude = files_analysis["change_magnitude"]
        if change_magnitude == "minor":
            decision_factors["size_factor"] = 0.9
        elif change_magnitude == "moderate":
            decision_factors["size_factor"] = 0.7
        elif change_magnitude == "significant":
            decision_factors["size_factor"] = 0.5
        else:  # major
            decision_factors["size_factor"] = 0.3

        # Quality factor
        quality_score = quality_analysis["quality_score"]
        decision_factors["quality_factor"] = quality_score / 100.0

        # Security factor
        security_risk = security_analysis["security_risk"]
        if security_risk == "low":
            decision_factors["security_factor"] = 0.9
        elif security_risk == "medium":
            decision_factors["security_factor"] = 0.6
        else:  # high
            decision_factors["security_factor"] = 0.2

        # Architecture factor
        consistency_score = architectural_analysis["consistency_score"]
        decision_factors["architecture_factor"] = consistency_score

        # Business factor
        business_risk = business_analysis["risk_to_operations"]
        if business_risk == "low":
            decision_factors["business_factor"] = 0.9
        elif business_risk == "medium":
            decision_factors["business_factor"] = 0.6
        else:  # high
            decision_factors["business_factor"] = 0.4

        # AI factor
        decision_factors["ai_factor"] = ai_insights["confidence"]

        # Calculate weighted confidence score
        weights = {
            "size_factor": 0.15,
            "quality_factor": 0.20,
            "security_factor": 0.25,
            "architecture_factor": 0.20,
            "business_factor": 0.15,
            "ai_factor": 0.05,
        }

        confidence = sum(
            factor * weights[name] for name, factor in decision_factors.items()
        )

        # Make decision based on confidence and additional criteria
        action = "wait"
        reasoning = []

        # High confidence auto-merge criteria
        if confidence >= 0.85:
            action = "merge"
            reasoning.append("High confidence based on comprehensive analysis")
        elif confidence >= 0.75:
            # Check additional criteria for medium-high confidence
            if (
                security_analysis["security_risk"] == "low"
                and quality_analysis["quality_score"] >= 80
                and len(architectural_analysis["pattern_violations"]) == 0
            ):
                action = "merge"
                reasoning.append(
                    "Medium-high confidence with strong security and quality"
                )
            else:
                action = "review_required"
                reasoning.append("Medium confidence requires human review")
        elif confidence >= 0.60:
            action = "review_required"
            reasoning.append("Moderate confidence requires manual review")
        else:
            action = "reject"
            reasoning.append("Low confidence indicates significant issues")

        # Override rules
        if security_analysis["secrets_exposed"]:
            action = "reject"
            reasoning.append("BLOCKED: Secrets detected in code")

        if len(security_analysis["vulnerabilities_detected"]) > 2:
            action = "reject"
            reasoning.append("BLOCKED: Multiple security vulnerabilities")

        # Check for PR author trust level
        trusted_authors = ["dependabot[bot]",
                           "renovate[bot]", "github-actions[bot]"]
        if pr.user.login in trusted_authors and confidence >= 0.7:
            action = "merge"
            reasoning.append("Trusted bot author with acceptable confidence")

        return {
            "action": action,
            "confidence": round(confidence, 3),
            "decision_factors": decision_factors,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "reviewer": "AI Code Review Agent",
        }

    async def _post_review_comment(self, pr, review_result: Dict) -> None:
        """Post comprehensive review comment to PR"""

        # Format review comment
        comment = f"""## 🤖 AI Code Review Agent - Autonomous Analysis

**Overall Assessment:** {review_result['merge_decision']['action'].upper()} (Confidence: {review_result['merge_decision']['confidence']:.1%})

### 📊 Analysis Summary
- **Files Changed:** {review_result['files_analysis']['total_files']} ({review_result['files_analysis']['change_magnitude']} magnitude)
- **Architecture Impact:** {review_result['architectural_analysis']['integration_risk']} risk
- **Business Impact:** {review_result['business_analysis']['risk_to_operations']} operational risk
- **Security Risk:** {review_result['security_analysis']['security_risk']}
- **Quality Score:** {review_result['quality_analysis']['quality_score']}/100

### 🏗️ Architectural Analysis
- **Orchestrator Changes:** {review_result['architectural_analysis']['orchestrator_changes']}
- **Agent Changes:** {review_result['architectural_analysis']['agent_changes']}
- **Pattern Consistency:** {review_result['architectural_analysis']['consistency_score']:.2f}
"""

        if review_result["architectural_analysis"]["pattern_violations"]:
            comment += f"\n**⚠️ Pattern Violations:**\n"
            for violation in review_result["architectural_analysis"][
                "pattern_violations"
            ]:
                comment += f"- {violation}\n"

        comment += f"""
### 💼 Business Impact Assessment
- **Revenue Impact:** {review_result['business_analysis']['revenue_impact']}
- **Automation Impact:** {review_result['business_analysis']['automation_impact']}
- **Competitive Impact:** {review_result['business_analysis']['competitive_impact']}
- **Quality Impact:** {review_result['business_analysis']['quality_impact']}

### 🔒 Security Analysis
"""

        if review_result["security_analysis"]["vulnerabilities_detected"]:
            comment += "**🚨 Vulnerabilities Detected:**\n"
            for vuln in review_result["security_analysis"]["vulnerabilities_detected"]:
                comment += f"- {vuln}\n"

        if review_result["security_analysis"]["injection_risks"]:
            comment += "**⚠️ Injection Risks:**\n"
            for risk in review_result["security_analysis"]["injection_risks"]:
                comment += f"- {risk}\n"

        comment += f"""
### 📈 Quality Assessment
- **Quality Score:** {review_result['quality_analysis']['quality_score']}/100
- **Maintainability:** {review_result['quality_analysis']['maintainability_score']}/100
- **Test Coverage Impact:** {review_result['quality_analysis']['test_coverage_impact']}
"""

        if review_result["quality_analysis"]["complexity_issues"]:
            comment += "\n**Complexity Issues:**\n"
            for issue in review_result["quality_analysis"]["complexity_issues"]:
                comment += f"- {issue}\n"

        comment += f"""
### 🧠 AI Strategic Insights
{review_result['ai_insights']['strategic_assessment'][:300]}...

### 🎯 Decision Reasoning
"""
        for reason in review_result["merge_decision"]["reasoning"]:
            comment += f"- {reason}\n"

        comment += f"""
### 🚀 Next Steps
"""

        if review_result["merge_decision"]["action"] == "merge":
            comment += "✅ **APPROVED FOR AUTO-MERGE** - All criteria met for autonomous merge\n"
        elif review_result["merge_decision"]["action"] == "review_required":
            comment += "👥 **HUMAN REVIEW REQUIRED** - Please review the analysis above before merging\n"
        elif review_result["merge_decision"]["action"] == "reject":
            comment += (
                "❌ **MERGE BLOCKED** - Critical issues must be resolved before merge\n"
            )
        else:
            comment += "⏳ **WAITING** - Additional criteria must be met\n"

        comment += f"""
---
*Reviewed by AI Code Review Agent at {review_result['review_timestamp']}*
*AI Teammate - Autonomous Development Intelligence*
"""

        try:
            pr.create_issue_comment(comment)
            self.logger.info(f"Posted review comment to PR #{pr.number}")
        except Exception as e:
            self.logger.error(f"Failed to post review comment: {e}")


# Example usage and CLI interface
async def main():
    """CLI interface for AI Code Review Agent"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="AI Code Review Agent - Autonomous PR Analysis"
    )
    parser.add_argument("--repo", required=True,
                        help="Repository name (owner/repo)")
    parser.add_argument("--pr", type=int, required=True,
                        help="Pull request number")
    parser.add_argument(
        "--github-token", help="GitHub token (or set GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--anthropic-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    anthropic_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY")

    if not github_token or not anthropic_key:
        print("❌ Error: GitHub token and Anthropic API key are required")
        return

    # Initialize AI Code Review Agent
    agent = AICodeReviewAgent(github_token, anthropic_key)

    print(f"🤖 Starting autonomous review of {args.repo} PR #{args.pr}")

    # Perform review
    result = await agent.review_pull_request(args.repo, args.pr)

    if "error" in result:
        print(f"❌ Review failed: {result['error']}")
        return

    print(f"\n✅ Review completed!")
    print(f"📊 Confidence: {result['merge_decision']['confidence']:.1%}")
    print(f"🎯 Decision: {result['merge_decision']['action'].upper()}")
    print(f"\n💡 Key factors:")
    for name, score in result["merge_decision"]["decision_factors"].items():
        print(f"   {name}: {score:.2f}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
