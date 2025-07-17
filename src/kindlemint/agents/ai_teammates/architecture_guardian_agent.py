"""
AI Architecture Guardian Agent - System design consistency and architectural integrity

This agent acts as a senior architect teammate, ensuring:
- Architectural pattern consistency across the codebase
- Design principle enforcement (SOLID, DRY, KISS)
- System boundary and interface integrity
- Technical debt monitoring and prevention
- Long-term maintainability and scalability
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import anthropic
from github import Github


@dataclass
class ArchitecturalViolation:
    """Represents an architectural design violation"""

    violation_type: (
        str  # pattern_inconsistency, boundary_violation, coupling_issue, etc.
    )
    severity: str  # critical, high, medium, low
    description: str
    file_path: str
    line_number: Optional[int] = None
    affected_components: List[str] = None
    suggested_fix: str = ""
    architectural_principle: str = ""
    impact_assessment: str = ""


@dataclass
class ArchitecturalAssessment:
    """Complete architectural assessment of changes"""

    overall_health: str  # excellent, good, needs_attention, poor
    violations: List[ArchitecturalViolation]
    pattern_consistency_score: float  # 0-100
    coupling_analysis: Dict
    cohesion_analysis: Dict
    design_debt_impact: str
    future_maintainability: str
    scalability_impact: str
    recommendations: List[str]


class AIArchitectureGuardianAgent:
    """
    Autonomous AI teammate specialized in architectural oversight

    Capabilities:
    - Architectural pattern detection and enforcement
    - SOLID principles validation
    - System boundary and interface analysis
    - Component coupling and cohesion assessment
    - Design debt identification and prevention
    - Scalability and maintainability evaluation
    - Architectural decision tracking and validation
    """

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger(__name__)

        # Load architectural patterns and rules
        self.architectural_patterns = self._load_architectural_patterns()
        self.design_principles = self._load_design_principles()
        self.component_boundaries = self._load_component_boundaries()
        self.interface_contracts = self._load_interface_contracts()

        # Architecture quality thresholds
        self.quality_thresholds = {
            "min_pattern_consistency": 85,
            "max_coupling_index": 0.3,
            "min_cohesion_score": 0.7,
            "max_design_debt_increase": 10,
            "max_cyclomatic_complexity": 10,
            "max_component_dependencies": 8,
        }

    def _load_architectural_patterns(self) -> Dict[str, Dict]:
        """Load known architectural patterns in the system"""
        return {
            "orchestrator_pattern": {
                "description": "Multi-agent orchestration with business intelligence",
                "components": [
                    "competitive_intelligence_orchestrator",
                    "tactical_advantage_orchestrator",
                    "professional_quality_orchestrator",
                    "tactical_seo_orchestrator",
                ],
                "principles": [
                    "Single responsibility for each orchestrator",
                    "Async communication between orchestrators",
                    "Centralized coordination through main orchestrator",
                    "Business intelligence integration required",
                ],
                "interfaces": [
                    "async def analyze_*",
                    "async def orchestrate_*",
                    "async def generate_insights",
                ],
            },
            "agent_communication": {
                "description": "Agent-to-agent messaging and coordination",
                "components": [
                    "message_protocol",
                    "health_monitoring",
                    "task_coordinator",
                ],
                "principles": [
                    "Message-based communication",
                    "Health monitoring for all agents",
                    "Standardized message formats",
                    "Async message handling",
                ],
                "interfaces": [
                    "send_message",
                    "receive_message",
                    "register_agent",
                    "health_check",
                ],
            },
            "automation_pipeline": {
                "description": "KDP automation with market intelligence",
                "components": [
                    "kdp_automation_engine",
                    "market_research",
                    "content_generation",
                ],
                "principles": [
                    "Pipeline-based processing",
                    "Error handling and recovery",
                    "Progress tracking",
                    "Configurable automation steps",
                ],
                "interfaces": [
                    "async def process_*",
                    "async def generate_*",
                    "async def analyze_*",
                ],
            },
            "ai_teammates": {
                "description": "AI development teammates coordination",
                "components": [
                    "code_review_agent",
                    "technical_lead_agent",
                    "security_reviewer_agent",
                    "architecture_guardian_agent",
                ],
                "principles": [
                    "Specialized expertise per agent",
                    "Coordinated decision making",
                    "GitHub integration",
                    "AI-powered analysis",
                ],
                "interfaces": [
                    "async def review_*",
                    "async def make_decision",
                    "async def assess_*",
                ],
            },
        }

    def _load_design_principles(self) -> Dict[str, Dict]:
        """Load design principles and their validation rules"""
        return {
            "single_responsibility": {
                "description": "Each class should have only one reason to change",
                "validation_rules": [
                    "Class should have < 10 public methods",
                    "Class should have < 500 lines",
                    "Class name should indicate single purpose",
                ],
            },
            "open_closed": {
                "description": "Open for extension, closed for modification",
                "validation_rules": [
                    "Use abstract base classes for extension points",
                    "Avoid modifying existing public interfaces",
                    "Prefer composition over inheritance",
                ],
            },
            "liskov_substitution": {
                "description": "Derived classes should be substitutable for base classes",
                "validation_rules": [
                    "Override methods should strengthen preconditions",
                    "Override methods should weaken postconditions",
                    "No exceptions thrown that base class doesn't throw",
                ],
            },
            "interface_segregation": {
                "description": "Clients shouldn't depend on interfaces they don't use",
                "validation_rules": [
                    "Interfaces should be focused and cohesive",
                    "Large interfaces should be split into smaller ones",
                    "Dependencies should be minimal",
                ],
            },
            "dependency_inversion": {
                "description": "Depend on abstractions, not concretions",
                "validation_rules": [
                    "High-level modules shouldn't depend on low-level modules",
                    "Use dependency injection",
                    "Program to interfaces, not implementations",
                ],
            },
            "dry": {
                "description": "Don't Repeat Yourself",
                "validation_rules": [
                    "No duplicate code blocks > 10 lines",
                    "Extract common functionality to utilities",
                    "Use inheritance or composition for common behavior",
                ],
            },
            "kiss": {
                "description": "Keep It Simple, Stupid",
                "validation_rules": [
                    "Avoid unnecessary complexity",
                    "Prefer simple solutions over clever ones",
                    "Code should be easily understandable",
                ],
            },
        }

    def _load_component_boundaries(self) -> Dict[str, Dict]:
        """Load component boundaries and their rules"""
        return {
            "orchestrator_layer": {
                "path_patterns": ["src/kindlemint/orchestrator/"],
                "allowed_dependencies": [
                    "src/kindlemint/agents/",
                    "src/kindlemint/automation/",
                    "anthropic",
                    "openai",
                ],
                "forbidden_dependencies": ["src/kindlemint/cli.py", "scripts/"],
                "principles": [
                    "Should not directly import CLI components",
                    "Should use agents for low-level operations",
                    "Should maintain business logic separation",
                ],
            },
            "agents_layer": {
                "path_patterns": ["src/kindlemint/agents/"],
                "allowed_dependencies": [
                    "src/kindlemint/context/",
                    "github",
                    "anthropic",
                ],
                "forbidden_dependencies": ["src/kindlemint/orchestrator/", "scripts/"],
                "principles": [
                    "Should not depend on orchestrators",
                    "Should be independently testable",
                    "Should use message protocol for communication",
                ],
            },
            "automation_layer": {
                "path_patterns": ["src/kindlemint/automation/"],
                "allowed_dependencies": [
                    "src/kindlemint/agents/",
                    "requests",
                    "aiohttp",
                ],
                "forbidden_dependencies": ["src/kindlemint/orchestrator/"],
                "principles": [
                    "Should focus on external integrations",
                    "Should handle errors gracefully",
                    "Should be configurable and testable",
                ],
            },
            "ai_teammates_layer": {
                "path_patterns": ["src/kindlemint/agents/ai_teammates/"],
                "allowed_dependencies": [
                    "src/kindlemint/orchestrator/",
                    "src/kindlemint/agents/",
                    "github",
                    "anthropic",
                ],
                "forbidden_dependencies": ["scripts/", "src/kindlemint/cli.py"],
                "principles": [
                    "Should integrate with business orchestrators",
                    "Should maintain GitHub integration",
                    "Should provide AI-powered analysis",
                ],
            },
        }

    def _load_interface_contracts(self) -> Dict[str, Dict]:
        """Load interface contracts and their requirements"""
        return {
            "orchestrator_interface": {
                "required_methods": [
                    "async def analyze",
                    "async def orchestrate",
                    "async def generate_insights",
                ],
                "required_attributes": ["anthropic", "logger"],
                "naming_conventions": [
                    "Class names end with 'Orchestrator'",
                    "Methods use async/await",
                    "Return types are Dict or specific dataclasses",
                ],
            },
            "agent_interface": {
                "required_methods": ["async def process", "register", "health_check"],
                "required_attributes": ["logger", "agent_id"],
                "naming_conventions": [
                    "Class names end with 'Agent'",
                    "Use message protocol for communication",
                    "Implement health monitoring",
                ],
            },
            "ai_teammate_interface": {
                "required_methods": [
                    "async def review_*",
                    "async def make_*_decision",
                    "async def assess_*",
                ],
                "required_attributes": ["github", "anthropic", "logger"],
                "naming_conventions": [
                    "Class names end with 'Agent'",
                    "GitHub integration required",
                    "AI analysis methods",
                ],
            },
        }

    async def perform_architectural_review(
        self, repo_name: str, pr_number: int
    ) -> ArchitecturalAssessment:
        """
        Perform comprehensive architectural review of PR changes

        Returns detailed assessment including:
        - Architectural pattern consistency
        - Design principle violations
        - Component boundary analysis
        - Coupling and cohesion metrics
        - Design debt impact
        - Long-term maintainability assessment
        """
        self.logger.info(
            f"🏗️ Starting architectural review of PR #{pr_number}")

        try:
            # Get PR details
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Analyze architectural patterns
            pattern_analysis = await self._analyze_pattern_consistency(pr)

            # Validate design principles
            principle_violations = await self._validate_design_principles(pr)

            # Check component boundaries
            boundary_analysis = await self._analyze_component_boundaries(pr)

            # Assess coupling and cohesion
            coupling_analysis = await self._analyze_coupling(pr)
            cohesion_analysis = await self._analyze_cohesion(pr)

            # Evaluate design debt impact
            design_debt_analysis = await self._evaluate_design_debt_impact(pr)

            # Generate AI-powered architectural insights
            ai_insights = await self._generate_architectural_insights(
                pr,
                pattern_analysis,
                principle_violations,
                boundary_analysis,
                coupling_analysis,
                cohesion_analysis,
                design_debt_analysis,
            )

            # Combine all violations
            all_violations = []
            all_violations.extend(principle_violations)
            all_violations.extend(boundary_analysis.get("violations", []))

            # Calculate overall health
            overall_health = self._calculate_architectural_health(
                pattern_analysis, all_violations, coupling_analysis, cohesion_analysis
            )

            # Generate recommendations
            recommendations = self._generate_architectural_recommendations(
                all_violations, coupling_analysis, cohesion_analysis, ai_insights
            )

            assessment = ArchitecturalAssessment(
                overall_health=overall_health,
                violations=all_violations,
                pattern_consistency_score=pattern_analysis["consistency_score"],
                coupling_analysis=coupling_analysis,
                cohesion_analysis=cohesion_analysis,
                design_debt_impact=design_debt_analysis["impact_level"],
                future_maintainability=design_debt_analysis["maintainability_trend"],
                scalability_impact=design_debt_analysis["scalability_impact"],
                recommendations=recommendations,
            )

            # Post architectural review comment
            await self._post_architectural_comment(pr, assessment)

            return assessment

        except Exception as e:
            self.logger.error(f"Architectural review failed: {e}")
            return ArchitecturalAssessment(
                overall_health="unknown",
                violations=[],
                pattern_consistency_score=0,
                coupling_analysis={"error": str(e)},
                cohesion_analysis={"error": str(e)},
                design_debt_impact="unknown",
                future_maintainability="unknown",
                scalability_impact="unknown",
                recommendations=["Manual architectural review required"],
            )

    async def _analyze_pattern_consistency(self, pr) -> Dict:
        """Analyze consistency with established architectural patterns"""

        files_changed = list(pr.get_files())
        pattern_scores = {}

        for pattern_name, pattern_def in self.architectural_patterns.items():
            # Check if changes affect this pattern
            affected_components = []
            for component in pattern_def["components"]:
                for file in files_changed:
                    if component in file.filename:
                        affected_components.append(file.filename)

            if affected_components:
                # Analyze pattern compliance
                compliance_score = await self._check_pattern_compliance(
                    affected_components, pattern_def, files_changed
                )
                pattern_scores[pattern_name] = {
                    "affected_components": affected_components,
                    "compliance_score": compliance_score,
                    "violations": await self._identify_pattern_violations(
                        affected_components, pattern_def, files_changed
                    ),
                }

        # Calculate overall consistency score
        if pattern_scores:
            total_score = sum(p["compliance_score"]
                              for p in pattern_scores.values())
            consistency_score = total_score / len(pattern_scores)
        else:
            consistency_score = 100  # No patterns affected

        return {
            "consistency_score": consistency_score,
            "pattern_analysis": pattern_scores,
            "affected_patterns": list(pattern_scores.keys()),
        }

    async def _check_pattern_compliance(
        self, affected_files: List[str], pattern_def: Dict, all_files: List
    ) -> float:
        """Check compliance with a specific architectural pattern"""

        compliance_score = 100.0

        # Check naming conventions
        for file_obj in all_files:
            if file_obj.filename in affected_files:
                # Check if interfaces are properly implemented
                if hasattr(file_obj, "patch") and file_obj.patch:
                    patch_content = file_obj.patch

                    # Check for required interface methods
                    interfaces = pattern_def.get("interfaces", [])
                    for interface in interfaces:
                        if (
                            "async def" in interface
                            and "async def" not in patch_content
                        ):
                            compliance_score -= 10

                    # Check for principle violations
                    principles = pattern_def.get("principles", [])
                    for principle in principles:
                        if (
                            "async" in principle.lower()
                            and "def " in patch_content
                            and "async def" not in patch_content
                        ):
                            compliance_score -= 15

        return max(0, compliance_score)

    async def _identify_pattern_violations(
        self, affected_files: List[str], pattern_def: Dict, all_files: List
    ) -> List[str]:
        """Identify specific pattern violations"""
        violations = []

        for file_obj in all_files:
            if (
                file_obj.filename in affected_files
                and hasattr(file_obj, "patch")
                and file_obj.patch
            ):
                patch_content = file_obj.patch

                # Check for synchronous methods where async is expected
                if pattern_def.get("description", "").lower().startswith("multi-agent"):
                    if re.search(r"^[+].*def\s+(?!__)", patch_content, re.MULTILINE):
                        async_methods = re.findall(
                            r"^[+].*async def\s+(\w+)", patch_content, re.MULTILINE
                        )
                        sync_methods = re.findall(
                            r"^[+].*def\s+(\w+)", patch_content, re.MULTILINE
                        )

                        if len(sync_methods) > len(async_methods):
                            violations.append(
                                f"Synchronous methods in async pattern: {file_obj.filename}"
                            )

        return violations

    async def _validate_design_principles(self, pr) -> List[ArchitecturalViolation]:
        """Validate adherence to design principles"""
        violations = []

        for file in pr.get_files():
            if (
                not file.filename.endswith(".py")
                or not hasattr(file, "patch")
                or not file.patch
            ):
                continue

            patch_content = file.patch

            # Check Single Responsibility Principle
            class_count = len(
                re.findall(r"^[+]class\s+\w+", patch_content, re.MULTILINE)
            )
            method_count = len(
                re.findall(r"^[+]\s+def\s+\w+", patch_content, re.MULTILINE)
            )

            if class_count > 0 and method_count > 15:  # Too many methods in a class
                violations.append(
                    ArchitecturalViolation(
                        violation_type="single_responsibility",
                        severity="medium",
                        description=f"Class may have too many responsibilities ({method_count} methods)",
                        file_path=file.filename,
                        architectural_principle="Single Responsibility Principle",
                        suggested_fix="Consider breaking class into smaller, focused classes",
                    )
                )

            # Check DRY principle - look for duplicated code patterns
            lines = patch_content.split("\n")
            added_lines = [
                line[1:] for line in lines if line.startswith("+") and len(line) > 10
            ]

            # Simple duplicate detection
            for i, line1 in enumerate(added_lines):
                for j, line2 in enumerate(added_lines[i + 1:], i + 1):
                    if line1.strip() == line2.strip() and len(line1.strip()) > 20:
                        violations.append(
                            ArchitecturalViolation(
                                violation_type="dry_violation",
                                severity="low",
                                description="Potential code duplication detected",
                                file_path=file.filename,
                                line_number=i + 1,
                                architectural_principle="Don't Repeat Yourself",
                                suggested_fix="Extract common code to a shared function or method",
                            )
                        )
                        break

            # Check for overly complex methods (KISS principle)
            complex_methods = re.findall(
                r"^[+]\s+def\s+(\w+).*?(?=^[+]\s+def|\Z)",
                patch_content,
                re.MULTILINE | re.DOTALL,
            )
            for method in complex_methods:
                if method.count("\n") > 30:  # Method too long
                    violations.append(
                        ArchitecturalViolation(
                            violation_type="kiss_violation",
                            severity="medium",
                            description="Method is too complex (> 30 lines)",
                            file_path=file.filename,
                            architectural_principle="Keep It Simple, Stupid",
                            suggested_fix="Break method into smaller, focused functions",
                        )
                    )

        return violations

    async def _analyze_component_boundaries(self, pr) -> Dict:
        """Analyze component boundary violations"""

        boundary_violations = []
        files_changed = list(pr.get_files())

        for file in files_changed:
            if not hasattr(file, "patch") or not file.patch:
                continue

            # Determine which layer this file belongs to
            file_layer = None
            for layer_name, layer_def in self.component_boundaries.items():
                if any(
                    pattern in file.filename for pattern in layer_def["path_patterns"]
                ):
                    file_layer = layer_name
                    break

            if not file_layer:
                continue

            layer_def = self.component_boundaries[file_layer]

            # Check imports in the patch for boundary violations
            import_lines = re.findall(
                r"^[+].*(?:import|from)\s+([^\s]+)", file.patch, re.MULTILINE
            )

            for import_line in import_lines:
                # Check against forbidden dependencies
                for forbidden in layer_def.get("forbidden_dependencies", []):
                    if forbidden in import_line:
                        boundary_violations.append(
                            ArchitecturalViolation(
                                violation_type="boundary_violation",
                                severity="high",
                                description=f"Forbidden dependency: {import_line}",
                                file_path=file.filename,
                                architectural_principle=f"{file_layer} boundary rules",
                                suggested_fix=f"Remove dependency on {forbidden} from {file_layer}",
                            )
                        )

        return {
            "violations": boundary_violations,
            "boundary_health": (
                "good" if len(boundary_violations) == 0 else "needs_attention"
            ),
        }

    async def _analyze_coupling(self, pr) -> Dict:
        """Analyze coupling between components"""

        coupling_metrics = {
            "afferent_coupling": {},  # Who depends on this
            "efferent_coupling": {},  # What this depends on
            "instability": {},  # Efferent / (Afferent + Efferent)
            "overall_coupling_index": 0.0,
        }

        files_changed = list(pr.get_files())

        for file in files_changed:
            if (
                not file.filename.endswith(".py")
                or not hasattr(file, "patch")
                or not file.patch
            ):
                continue

            # Count dependencies (efferent coupling)
            imports = re.findall(
                r"^[+].*(?:import|from)\s+([^\s]+)", file.patch, re.MULTILINE
            )
            local_imports = [
                imp
                for imp in imports
                if imp.startswith("src.kindlemint") or imp.startswith("kindlemint")
            ]

            coupling_metrics["efferent_coupling"][file.filename] = len(
                local_imports)

        # Calculate overall coupling index
        if coupling_metrics["efferent_coupling"]:
            avg_coupling = sum(coupling_metrics["efferent_coupling"].values()) / len(
                coupling_metrics["efferent_coupling"]
            )
            coupling_metrics["overall_coupling_index"] = (
                avg_coupling / 10.0
            )  # Normalize

        return coupling_metrics

    async def _analyze_cohesion(self, pr) -> Dict:
        """Analyze cohesion within components"""

        cohesion_metrics = {
            "class_cohesion": {},
            "module_cohesion": {},
            "overall_cohesion_score": 0.0,
        }

        files_changed = list(pr.get_files())

        for file in files_changed:
            if (
                not file.filename.endswith(".py")
                or not hasattr(file, "patch")
                or not file.patch
            ):
                continue

            # Simple cohesion analysis based on method relationships
            methods = re.findall(r"^[+]\s+def\s+(\w+)",
                                 file.patch, re.MULTILINE)
            classes = re.findall(r"^[+]class\s+(\w+)",
                                 file.patch, re.MULTILINE)

            if classes and methods:
                # Calculate methods per class ratio
                methods_per_class = len(methods) / len(classes)
                cohesion_score = min(
                    1.0, 1.0 / max(1, methods_per_class / 8)
                )  # Ideal ~8 methods per class
                cohesion_metrics["class_cohesion"][file.filename] = cohesion_score

        # Calculate overall cohesion
        if cohesion_metrics["class_cohesion"]:
            cohesion_metrics["overall_cohesion_score"] = sum(
                cohesion_metrics["class_cohesion"].values()
            ) / len(cohesion_metrics["class_cohesion"])
        else:
            # Default to good cohesion
            cohesion_metrics["overall_cohesion_score"] = 1.0

        return cohesion_metrics

    async def _evaluate_design_debt_impact(self, pr) -> Dict:
        """Evaluate the impact on technical/design debt"""

        files_changed = list(pr.get_files())
        debt_indicators = {
            "complexity_increase": 0,
            "coupling_increase": 0,
            "pattern_violations": 0,
            "maintainability_issues": 0,
        }

        for file in files_changed:
            if not hasattr(file, "patch") or not file.patch:
                continue

            # Count complexity indicators
            debt_indicators["complexity_increase"] += len(
                re.findall(r"^[+].*(?:if|for|while|try)",
                           file.patch, re.MULTILINE)
            )
            debt_indicators["coupling_increase"] += len(
                re.findall(r"^[+].*import", file.patch, re.MULTILINE)
            )

            # Look for TODO/FIXME/HACK comments
            debt_indicators["maintainability_issues"] += len(
                re.findall(r"^[+].*(?:TODO|FIXME|HACK|XXX)",
                           file.patch, re.MULTILINE)
            )

        # Calculate impact level
        total_debt_score = sum(debt_indicators.values())
        if total_debt_score > 20:
            impact_level = "high"
            maintainability_trend = "decreasing"
            scalability_impact = "negative"
        elif total_debt_score > 10:
            impact_level = "medium"
            maintainability_trend = "stable"
            scalability_impact = "neutral"
        else:
            impact_level = "low"
            maintainability_trend = "improving"
            scalability_impact = "positive"

        return {
            "impact_level": impact_level,
            "maintainability_trend": maintainability_trend,
            "scalability_impact": scalability_impact,
            "debt_indicators": debt_indicators,
        }

    async def _generate_architectural_insights(
        self,
        pr,
        pattern_analysis: Dict,
        violations: List,
        boundary_analysis: Dict,
        coupling_analysis: Dict,
        cohesion_analysis: Dict,
        design_debt_analysis: Dict,
    ) -> Dict:
        """Generate AI-powered architectural insights"""

        context = f"""
        Architectural Review for PR: {pr.title}
        Files Changed: {len(list(pr.get_files()))}
        
        Pattern Analysis:
        - Consistency Score: {pattern_analysis['consistency_score']:.1f}/100
        - Affected Patterns: {pattern_analysis['affected_patterns']}
        
        Design Violations: {len(violations)}
        Boundary Health: {boundary_analysis['boundary_health']}
        
        Coupling Analysis:
        - Overall Coupling Index: {coupling_analysis['overall_coupling_index']:.2f}
        
        Cohesion Analysis:
        - Overall Cohesion Score: {cohesion_analysis['overall_cohesion_score']:.2f}
        
        Design Debt:
        - Impact Level: {design_debt_analysis['impact_level']}
        - Maintainability Trend: {design_debt_analysis['maintainability_trend']}
        """

        prompt = f"""
        As a senior software architect reviewing this PR for an AI-KindleMint orchestration system:

        {context}

        Provide architectural insights focusing on:
        1. Long-term architectural health and sustainability
        2. Impact on system scalability and maintainability
        3. Alignment with established architectural patterns
        4. Design principle adherence and violations
        5. Strategic recommendations for architectural improvement

        Focus on the big picture and long-term implications.
        """

        try:
            response = await self.anthropic.messages.acreate(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            insights = {
                "architectural_analysis": response.content[0].text,
                "confidence": 0.88,
                "key_concerns": self._extract_architectural_concerns(
                    response.content[0].text
                ),
                "improvement_opportunities": self._extract_improvement_opportunities(
                    response.content[0].text
                ),
            }

        except Exception as e:
            self.logger.warning(f"AI architectural insights failed: {e}")
            insights = {
                "architectural_analysis": "AI architectural analysis unavailable",
                "confidence": 0.5,
                "key_concerns": ["Manual architectural review recommended"],
                "improvement_opportunities": ["Standard architecture review process"],
            }

        return insights

    def _extract_architectural_concerns(self, ai_response: str) -> List[str]:
        """Extract key architectural concerns from AI response"""
        concerns = []
        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["concern", "issue", "problem", "violation"]
            ):
                concerns.append(line.strip())
        return concerns[:5]

    def _extract_improvement_opportunities(self, ai_response: str) -> List[str]:
        """Extract improvement opportunities from AI response"""
        opportunities = []
        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["improve", "enhance", "optimize", "refactor"]
            ):
                opportunities.append(line.strip())
        return opportunities[:5]

    def _calculate_architectural_health(
        self,
        pattern_analysis: Dict,
        violations: List,
        coupling_analysis: Dict,
        cohesion_analysis: Dict,
    ) -> str:
        """Calculate overall architectural health"""

        # Weight different factors
        factors = {
            "pattern_consistency": pattern_analysis["consistency_score"] / 100,
            "violation_impact": max(0, 1 - (len(violations) / 10)),
            "coupling_health": max(0, 1 - coupling_analysis["overall_coupling_index"]),
            "cohesion_health": cohesion_analysis["overall_cohesion_score"],
        }

        # Calculate weighted score
        weights = {
            "pattern_consistency": 0.3,
            "violation_impact": 0.3,
            "coupling_health": 0.2,
            "cohesion_health": 0.2,
        }

        health_score = sum(factor * weights[name]
                           for name, factor in factors.items())

        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.75:
            return "good"
        elif health_score >= 0.6:
            return "needs_attention"
        else:
            return "poor"

    def _generate_architectural_recommendations(
        self,
        violations: List,
        coupling_analysis: Dict,
        cohesion_analysis: Dict,
        ai_insights: Dict,
    ) -> List[str]:
        """Generate architectural recommendations"""
        recommendations = []

        # Violation-based recommendations
        if violations:
            violation_types = set(v.violation_type for v in violations)
            for v_type in violation_types:
                if v_type == "single_responsibility":
                    recommendations.append(
                        "Refactor classes to have single, focused responsibilities"
                    )
                elif v_type == "dry_violation":
                    recommendations.append(
                        "Extract common code to reduce duplication")
                elif v_type == "boundary_violation":
                    recommendations.append(
                        "Respect component boundaries and layer separation"
                    )

        # Coupling-based recommendations
        if coupling_analysis["overall_coupling_index"] > 0.3:
            recommendations.append(
                "Reduce coupling by introducing abstractions and interfaces"
            )

        # Cohesion-based recommendations
        if cohesion_analysis["overall_cohesion_score"] < 0.7:
            recommendations.append(
                "Improve cohesion by grouping related functionality")

        # AI-based recommendations
        recommendations.extend(ai_insights.get(
            "improvement_opportunities", [])[:3])

        return recommendations[:8]  # Limit to top 8 recommendations

    async def _post_architectural_comment(
        self, pr, assessment: ArchitecturalAssessment
    ) -> None:
        """Post comprehensive architectural review comment"""

        # Health emoji mapping
        health_emoji = {
            "excellent": "🌟",
            "good": "✅",
            "needs_attention": "⚠️",
            "poor": "🚨",
        }

        comment = f"""## 🏗️ AI Architecture Guardian - Architectural Review

**Architectural Health:** {health_emoji.get(assessment.overall_health, '❓')} {assessment.overall_health.upper()} (Pattern Consistency: {assessment.pattern_consistency_score:.1f}/100)

### 📐 Design Analysis
**Pattern Consistency:** {assessment.pattern_consistency_score:.1f}/100  
**Coupling Index:** {assessment.coupling_analysis.get('overall_coupling_index', 0):.2f} (lower is better)  
**Cohesion Score:** {assessment.cohesion_analysis.get('overall_cohesion_score', 0):.2f}/1.0  
**Design Debt Impact:** {assessment.design_debt_impact.title()}

### 🎯 Architectural Violations
"""

        if assessment.violations:
            # Group by severity
            violations_by_severity = {}
            for violation in assessment.violations:
                if violation.severity not in violations_by_severity:
                    violations_by_severity[violation.severity] = []
                violations_by_severity[violation.severity].append(violation)

            for severity in ["critical", "high", "medium", "low"]:
                if severity in violations_by_severity:
                    viols = violations_by_severity[severity]
                    comment += f"**{severity.upper()}:** {len(viols)} found\n"
                    for violation in viols[:3]:  # Show top 3 per severity
                        comment += (
                            f"- {violation.description} in `{violation.file_path}`\n"
                        )
                    if len(viols) > 3:
                        comment += f"- ... and {len(viols) - 3} more\n"
        else:
            comment += "✅ No architectural violations detected\n"

        comment += f"""
### 📊 Architectural Metrics
**Coupling Analysis:**
- Overall Coupling Index: {assessment.coupling_analysis.get('overall_coupling_index', 0):.2f}
- Files with High Coupling: {len([f for f, c in assessment.coupling_analysis.get('efferent_coupling', {}).items() if c > 5])}

**Cohesion Analysis:**
- Overall Cohesion Score: {assessment.cohesion_analysis.get('overall_cohesion_score', 0):.2f}/1.0
- Well-Cohesive Modules: {len([f for f, c in assessment.cohesion_analysis.get('class_cohesion', {}).items() if c > 0.8])}

### 🔮 Future Impact Assessment
**Maintainability:** {assessment.future_maintainability.title()}  
**Scalability:** {assessment.scalability_impact.title()}  
**Long-term Health:** Trending {'📈' if assessment.future_maintainability == 'improving' else '📉' if assessment.future_maintainability == 'decreasing' else '➡️'}

### 💡 Architectural Recommendations
"""

        for rec in assessment.recommendations[:6]:
            comment += f"- {rec}\n"

        comment += """
### 🎯 Next Steps
"""

        if assessment.overall_health in ["excellent", "good"]:
            comment += "✅ **ARCHITECTURE APPROVED** - Changes align with architectural standards\n"
        elif assessment.overall_health == "needs_attention":
            comment += "⚠️ **ARCHITECTURAL REVIEW RECOMMENDED** - Address violations before merge\n"
        else:
            comment += "🚨 **ARCHITECTURAL CONCERNS** - Significant issues require resolution\n"

        comment += f"""
---
*Architectural review by AI Architecture Guardian at {datetime.now().isoformat()}*
*Pattern Analysis • Design Principles • Component Boundaries • Technical Debt*
"""

        try:
            pr.create_issue_comment(comment)
            self.logger.info(f"Posted architectural review to PR #{pr.number}")
        except Exception as e:
            self.logger.error(f"Failed to post architectural comment: {e}")


# CLI interface
async def main():
    """CLI interface for AI Architecture Guardian Agent"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="AI Architecture Guardian Agent")
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

    # Initialize Architecture Guardian Agent
    agent = AIArchitectureGuardianAgent(github_token, anthropic_key)

    print(f"🏗️ Starting architectural review of {args.repo} PR #{args.pr}")

    # Perform architectural review
    assessment = await agent.perform_architectural_review(args.repo, args.pr)

    print("\n✅ Architectural review completed!")
    print(f"🏗️ Health: {assessment.overall_health.upper()}")
    print(
        f"📐 Pattern Consistency: {assessment.pattern_consistency_score:.1f}/100")
    print(f"⚠️ Violations: {len(assessment.violations)}")

    if assessment.violations:
        print("🚨 Key Issues:")
        for violation in assessment.violations[:3]:
            print(f"   - {violation.description}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
