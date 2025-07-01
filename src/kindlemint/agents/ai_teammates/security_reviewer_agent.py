"""
AI Security Reviewer Agent - Specialized security analysis and vulnerability detection

This agent acts as a security specialist teammate, providing:
- Advanced vulnerability scanning and detection
- Security best practices enforcement
- Threat modeling for changes
- Compliance validation (SOC2, GDPR, etc.)
- Security incident prevention
"""

import hashlib
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import anthropic
from github import Github


@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability finding"""

    severity: str  # critical, high, medium, low
    category: str  # injection, xss, secrets, crypto, auth, etc.
    description: str
    file_path: str
    line_number: Optional[int] = None
    vulnerable_code: Optional[str] = None
    remediation: str = ""
    cve_references: List[str] = None
    confidence: float = 0.95


@dataclass
class SecurityAssessment:
    """Complete security assessment of a PR"""

    overall_risk: str  # critical, high, medium, low
    vulnerabilities: List[SecurityVulnerability]
    compliance_issues: List[Dict]
    security_score: float  # 0-100
    threat_model: Dict
    recommendations: List[str]
    blocking_issues: List[str]


class AISecurityReviewerAgent:
    """
    Autonomous AI teammate specialized in security reviews

    Capabilities:
    - Advanced vulnerability pattern detection
    - Static application security testing (SAST)
    - Secrets and credentials scanning
    - Dependency vulnerability analysis
    - Security compliance validation
    - Threat modeling and risk assessment
    - Security best practices enforcement
    """

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger(__name__)

        # Load security patterns and rules
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.secrets_patterns = self._load_secrets_patterns()
        self.compliance_rules = self._load_compliance_rules()
        self.security_best_practices = self._load_security_best_practices()

        # Security thresholds
        self.security_thresholds = {
            "max_critical_vulns": 0,
            "max_high_vulns": 2,
            "max_medium_vulns": 5,
            "min_security_score": 85,
            "max_secrets_exposed": 0,
            "max_compliance_violations": 1,
        }

    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict]]:
        """Load vulnerability detection patterns"""
        return {
            "injection": [
                {
                    "pattern": r"exec\s*\([^)]*\)",
                    "description": "Code execution vulnerability",
                    "severity": "critical",
                },
                {
                    "pattern": r"eval\s*\([^)]*\)",
                    "description": "Code evaluation vulnerability",
                    "severity": "critical",
                },
                {
                    "pattern": r"subprocess\.(?:call|run|Popen).*shell\s*=\s*True",
                    "description": "Shell injection vulnerability",
                    "severity": "high",
                },
                {
                    "pattern": r"os\.system\s*\(",
                    "description": "OS command injection risk",
                    "severity": "high",
                },
            ],
            "deserialization": [
                {
                    "pattern": r"pickle\.loads?\s*\(",
                    "description": "Unsafe deserialization",
                    "severity": "critical",
                },
                {
                    "pattern": r"yaml\.load\s*\([^,)]*\)",
                    "description": "Unsafe YAML loading",
                    "severity": "high",
                },
                {
                    "pattern": r"json\.loads?\([^)]*user[^)]*\)",
                    "description": "Potential unsafe JSON deserialization",
                    "severity": "medium",
                },
            ],
            "crypto": [
                {
                    "pattern": r"hashlib\.md5\s*\(",
                    "description": "Weak MD5 hashing algorithm",
                    "severity": "medium",
                },
                {
                    "pattern": r"hashlib\.sha1\s*\(",
                    "description": "Weak SHA1 hashing algorithm",
                    "severity": "medium",
                },
                {
                    "pattern": r"random\.random\s*\(",
                    "description": "Cryptographically weak random number generation",
                    "severity": "low",
                },
            ],
            "auth": [
                {
                    "pattern": r"password\s*==?\s*['\"][^'\"]*['\"]",
                    "description": "Hardcoded password",
                    "severity": "critical",
                },
                {
                    "pattern": r"if\s+.*password.*==.*:",
                    "description": "Potential weak password comparison",
                    "severity": "medium",
                },
            ],
            "sql": [
                {
                    "pattern": r"['\"].*%s.*['\"].*%.*\(",
                    "description": "Potential SQL injection",
                    "severity": "high",
                },
                {
                    "pattern": r"\.format\([^)]*sql[^)]*\)",
                    "description": "SQL query formatting vulnerability",
                    "severity": "high",
                },
            ],
        }

    def _load_secrets_patterns(self) -> List[Dict]:
        """Load patterns for detecting secrets and credentials"""
        return [
            {
                "pattern": r"api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                "description": "API key exposure",
                "severity": "critical",
            },
            {
                "pattern": r"password\s*[:=]\s*['\"][^'\"]{6,}['\"]",
                "description": "Hardcoded password",
                "severity": "critical",
            },
            {
                "pattern": r"secret\s*[:=]\s*['\"][a-zA-Z0-9_-]{15,}['\"]",
                "description": "Secret key exposure",
                "severity": "critical",
            },
            {
                "pattern": r"token\s*[:=]\s*['\"][a-zA-Z0-9._-]{20,}['\"]",
                "description": "Authentication token exposure",
                "severity": "critical",
            },
            {
                "pattern": r"private[_-]?key\s*[:=]\s*['\"]-----BEGIN",
                "description": "Private key exposure",
                "severity": "critical",
            },
            {
                "pattern": r"aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*['\"][A-Z0-9]{20}['\"]",
                "description": "AWS access key exposure",
                "severity": "critical",
            },
            {
                "pattern": r"github[_-]?token\s*[:=]\s*['\"]ghp_[a-zA-Z0-9]{36}['\"]",
                "description": "GitHub token exposure",
                "severity": "critical",
            },
        ]

    def _load_compliance_rules(self) -> Dict[str, List[Dict]]:
        """Load compliance validation rules"""
        return {
            "gdpr": [
                {
                    "pattern": r"email\s*[:=].*@.*\..*",
                    "description": "Email collection requires GDPR consent",
                    "requirement": "data_consent",
                },
                {
                    "pattern": r"personal[_-]?data|user[_-]?info",
                    "description": "Personal data handling requires GDPR compliance",
                    "requirement": "data_protection",
                },
            ],
            "soc2": [
                {
                    "pattern": r"logging\.|log\.|logger\.",
                    "description": "Audit logging required for SOC2",
                    "requirement": "audit_trail",
                },
                {
                    "pattern": r"encrypt|decrypt|cipher",
                    "description": "Encryption controls for SOC2",
                    "requirement": "data_encryption",
                },
            ],
            "pci": [
                {
                    "pattern": r"credit[_-]?card|card[_-]?number|ccn",
                    "description": "Payment card data requires PCI compliance",
                    "requirement": "pci_dss",
                }
            ],
        }

    def _load_security_best_practices(self) -> Dict[str, List[str]]:
        """Load security best practices rules"""
        return {
            "input_validation": [
                "All user inputs must be validated",
                "Use parameterized queries for database access",
                "Implement proper input sanitization",
            ],
            "authentication": [
                "Use strong password policies",
                "Implement multi-factor authentication",
                "Secure session management",
            ],
            "authorization": [
                "Implement principle of least privilege",
                "Use role-based access control",
                "Validate permissions for all operations",
            ],
            "data_protection": [
                "Encrypt sensitive data at rest",
                "Use HTTPS for data in transit",
                "Implement proper key management",
            ],
            "error_handling": [
                "Don't expose sensitive information in errors",
                "Log security events appropriately",
                "Implement secure error responses",
            ],
        }

    async def perform_security_review(
        self, repo_name: str, pr_number: int
    ) -> SecurityAssessment:
        """
        Perform comprehensive security review of a PR

        Returns complete security assessment including:
        - Vulnerability detection and analysis
        - Secrets and credentials scanning
        - Compliance validation
        - Threat modeling
        - Security recommendations
        """
        self.logger.info(f"🔒 Starting security review of PR #{pr_number}")

        try:
            # Get PR details
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Scan for vulnerabilities
            vulnerabilities = await self._scan_vulnerabilities(pr)

            # Scan for secrets
            secrets_found = await self._scan_secrets(pr)
            vulnerabilities.extend(secrets_found)

            # Check compliance
            compliance_issues = await self._check_compliance(pr)

            # Perform threat modeling
            threat_model = await self._perform_threat_modeling(pr, vulnerabilities)

            # Generate AI-powered security insights
            ai_security_insights = await self._generate_security_insights(
                pr, vulnerabilities, compliance_issues, threat_model
            )

            # Calculate security score
            security_score = self._calculate_security_score(
                vulnerabilities, compliance_issues, len(list(pr.get_files()))
            )

            # Determine overall risk
            overall_risk = self._determine_overall_risk(
                vulnerabilities, compliance_issues
            )

            # Generate recommendations
            recommendations = self._generate_security_recommendations(
                vulnerabilities, compliance_issues, ai_security_insights
            )

            # Identify blocking issues
            blocking_issues = self._identify_blocking_issues(
                vulnerabilities, compliance_issues
            )

            assessment = SecurityAssessment(
                overall_risk=overall_risk,
                vulnerabilities=vulnerabilities,
                compliance_issues=compliance_issues,
                security_score=security_score,
                threat_model=threat_model,
                recommendations=recommendations,
                blocking_issues=blocking_issues,
            )

            # Post security review comment
            await self._post_security_comment(pr, assessment)

            return assessment

        except Exception as e:
            self.logger.error(f"Security review failed: {e}")
            return SecurityAssessment(
                overall_risk="unknown",
                vulnerabilities=[],
                compliance_issues=[],
                security_score=0,
                threat_model={"error": str(e)},
                recommendations=["Manual security review required"],
                blocking_issues=[f"Security scan failed: {str(e)}"],
            )

    async def _scan_vulnerabilities(self, pr) -> List[SecurityVulnerability]:
        """Scan for security vulnerabilities in code changes"""
        vulnerabilities = []

        for file in pr.get_files():
            if not file.patch:
                continue

            # Scan each vulnerability category
            for category, patterns in self.vulnerability_patterns.items():
                for pattern_def in patterns:
                    matches = re.finditer(
                        pattern_def["pattern"], file.patch, re.MULTILINE | re.IGNORECASE
                    )

                    for match in matches:
                        # Calculate line number in diff
                        line_num = self._get_line_number_from_patch(
                            file.patch, match.start()
                        )

                        vulnerability = SecurityVulnerability(
                            severity=pattern_def["severity"],
                            category=category,
                            description=pattern_def["description"],
                            file_path=file.filename,
                            line_number=line_num,
                            vulnerable_code=match.group(0),
                            remediation=self._get_remediation_advice(
                                category, pattern_def
                            ),
                            confidence=0.9,
                        )

                        vulnerabilities.append(vulnerability)

        return vulnerabilities

    async def _scan_secrets(self, pr) -> List[SecurityVulnerability]:
        """Scan for exposed secrets and credentials"""
        secrets_found = []

        for file in pr.get_files():
            if not file.patch:
                continue

            for secret_pattern in self.secrets_patterns:
                matches = re.finditer(
                    secret_pattern["pattern"], file.patch, re.MULTILINE
                )

                for match in matches:
                    line_num = self._get_line_number_from_patch(
                        file.patch, match.start()
                    )

                    # Extract and hash the potential secret for tracking
                    secret_value = match.group(0)
                    secret_hash = hashlib.sha256(
                        secret_value.encode()).hexdigest()[:16]

                    vulnerability = SecurityVulnerability(
                        severity=secret_pattern["severity"],
                        category="secrets",
                        description=f"{secret_pattern['description']} (hash: {secret_hash})",
                        file_path=file.filename,
                        line_number=line_num,
                        vulnerable_code="[REDACTED - SECRET DETECTED]",
                        remediation="Remove hardcoded secret and use environment variables or secure vaults",
                        confidence=0.95,
                    )

                    secrets_found.append(vulnerability)

        return secrets_found

    async def _check_compliance(self, pr) -> List[Dict]:
        """Check for compliance issues"""
        compliance_issues = []

        for file in pr.get_files():
            if not file.patch:
                continue

            for standard, rules in self.compliance_rules.items():
                for rule in rules:
                    matches = re.finditer(
                        rule["pattern"], file.patch, re.MULTILINE | re.IGNORECASE
                    )

                    for match in matches:
                        line_num = self._get_line_number_from_patch(
                            file.patch, match.start()
                        )

                        issue = {
                            "standard": standard.upper(),
                            "requirement": rule["requirement"],
                            "description": rule["description"],
                            "file_path": file.filename,
                            "line_number": line_num,
                            "severity": "medium",  # Default compliance severity
                        }

                        compliance_issues.append(issue)

        return compliance_issues

    async def _perform_threat_modeling(
        self, pr, vulnerabilities: List[SecurityVulnerability]
    ) -> Dict:
        """Perform threat modeling analysis"""

        files_changed = [f.filename for f in pr.get_files()]

        # Identify attack surfaces
        attack_surfaces = {
            "api_endpoints": any("api" in f or "endpoint" in f for f in files_changed),
            "data_processing": any(
                "data" in f or "process" in f for f in files_changed
            ),
            "authentication": any("auth" in f or "login" in f for f in files_changed),
            "file_operations": any("file" in f or "upload" in f for f in files_changed),
            "external_integrations": any(
                "integration" in f or "api" in f for f in files_changed
            ),
        }

        # Assess threat categories using STRIDE
        threats = {
            "spoofing": self._assess_spoofing_threats(files_changed, vulnerabilities),
            "tampering": self._assess_tampering_threats(files_changed, vulnerabilities),
            "repudiation": self._assess_repudiation_threats(
                files_changed, vulnerabilities
            ),
            "information_disclosure": self._assess_disclosure_threats(
                files_changed, vulnerabilities
            ),
            "denial_of_service": self._assess_dos_threats(
                files_changed, vulnerabilities
            ),
            "elevation_of_privilege": self._assess_privilege_threats(
                files_changed, vulnerabilities
            ),
        }

        # Calculate overall threat level
        threat_scores = [t["risk_level"] for t in threats.values()]
        if any(score == "high" for score in threat_scores):
            overall_threat = "high"
        elif any(score == "medium" for score in threat_scores):
            overall_threat = "medium"
        else:
            overall_threat = "low"

        return {
            "attack_surfaces": attack_surfaces,
            "stride_analysis": threats,
            "overall_threat_level": overall_threat,
            "mitigation_priority": self._prioritize_mitigations(threats),
        }

    def _assess_spoofing_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess spoofing threats"""
        auth_changes = any("auth" in f or "login" in f for f in files_changed)
        auth_vulns = [v for v in vulns if v.category == "auth"]

        if auth_changes and len(auth_vulns) > 0:
            risk_level = "high"
        elif auth_changes:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of identity spoofing",
            "affected_components": [f for f in files_changed if "auth" in f],
        }

    def _assess_tampering_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess tampering threats"""
        data_changes = any("data" in f or "input" in f for f in files_changed)
        injection_vulns = [v for v in vulns if v.category == "injection"]

        if data_changes and len(injection_vulns) > 0:
            risk_level = "high"
        elif data_changes:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of data tampering",
            "affected_components": [
                f for f in files_changed if "data" in f or "input" in f
            ],
        }

    def _assess_repudiation_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess repudiation threats"""
        logging_changes = any(
            "log" in f or "audit" in f for f in files_changed)

        risk_level = "medium" if logging_changes else "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of action repudiation",
            "affected_components": [
                f for f in files_changed if "log" in f or "audit" in f
            ],
        }

    def _assess_disclosure_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess information disclosure threats"""
        secrets_vulns = [v for v in vulns if v.category == "secrets"]

        if len(secrets_vulns) > 0:
            risk_level = "high"
        elif any("data" in f or "info" in f for f in files_changed):
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of information disclosure",
            "affected_components": [v.file_path for v in secrets_vulns],
        }

    def _assess_dos_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess denial of service threats"""
        api_changes = any("api" in f or "endpoint" in f for f in files_changed)

        risk_level = "medium" if api_changes else "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of denial of service",
            "affected_components": [
                f for f in files_changed if "api" in f or "endpoint" in f
            ],
        }

    def _assess_privilege_threats(
        self, files_changed: List[str], vulns: List[SecurityVulnerability]
    ) -> Dict:
        """Assess elevation of privilege threats"""
        auth_changes = any(
            "auth" in f or "permission" in f for f in files_changed)
        auth_vulns = [v for v in vulns if v.category == "auth"]

        if auth_changes and len(auth_vulns) > 0:
            risk_level = "high"
        elif auth_changes:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "description": "Risk of privilege escalation",
            "affected_components": [
                f for f in files_changed if "auth" in f or "permission" in f
            ],
        }

    def _prioritize_mitigations(self, threats: Dict) -> List[str]:
        """Prioritize threat mitigations"""
        mitigations = []

        for threat_type, threat_data in threats.items():
            if threat_data["risk_level"] == "high":
                mitigations.append(
                    f"HIGH PRIORITY: Address {threat_type} threats")
            elif threat_data["risk_level"] == "medium":
                mitigations.append(f"MEDIUM: Review {threat_type} controls")

        return mitigations

    def _get_line_number_from_patch(self, patch: str, match_start: int) -> int:
        """Get line number from patch position"""
        # Simple line counting - could be enhanced for more accuracy
        lines_before = patch[:match_start].count("\n")
        return lines_before + 1

    def _get_remediation_advice(self, category: str, pattern_def: Dict) -> str:
        """Get remediation advice for vulnerability category"""
        remediation_map = {
            "injection": "Use parameterized queries and input validation",
            "deserialization": "Use safe deserialization methods or avoid untrusted data",
            "crypto": "Use strong cryptographic algorithms (SHA-256 or better)",
            "auth": "Remove hardcoded credentials, use secure authentication",
            "sql": "Use parameterized queries and ORM frameworks",
        }

        return remediation_map.get(category, "Follow security best practices")

    def _calculate_security_score(
        self,
        vulnerabilities: List[SecurityVulnerability],
        compliance_issues: List[Dict],
        files_count: int,
    ) -> float:
        """Calculate overall security score"""
        base_score = 100.0

        # Deduct for vulnerabilities
        for vuln in vulnerabilities:
            if vuln.severity == "critical":
                base_score -= 25
            elif vuln.severity == "high":
                base_score -= 15
            elif vuln.severity == "medium":
                base_score -= 8
            elif vuln.severity == "low":
                base_score -= 3

        # Deduct for compliance issues
        base_score -= len(compliance_issues) * 5

        # Bonus for small, focused changes
        if files_count <= 3:
            base_score += 5

        return max(0, min(100, base_score))

    def _determine_overall_risk(
        self,
        vulnerabilities: List[SecurityVulnerability],
        compliance_issues: List[Dict],
    ) -> str:
        """Determine overall security risk level"""
        critical_vulns = [
            v for v in vulnerabilities if v.severity == "critical"]
        high_vulns = [v for v in vulnerabilities if v.severity == "high"]

        if len(critical_vulns) > 0:
            return "critical"
        elif len(high_vulns) > 2:
            return "high"
        elif len(high_vulns) > 0 or len(compliance_issues) > 2:
            return "medium"
        else:
            return "low"

    def _generate_security_recommendations(
        self,
        vulnerabilities: List[SecurityVulnerability],
        compliance_issues: List[Dict],
        ai_insights: Dict,
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        # Vulnerability-based recommendations
        critical_vulns = [
            v for v in vulnerabilities if v.severity == "critical"]
        if critical_vulns:
            recommendations.append(
                "URGENT: Fix all critical vulnerabilities before merge"
            )

        secrets_vulns = [v for v in vulnerabilities if v.category == "secrets"]
        if secrets_vulns:
            recommendations.append(
                "Remove all hardcoded secrets and use environment variables"
            )

        # Compliance-based recommendations
        if compliance_issues:
            recommendations.append(
                "Address compliance requirements before deployment")

        # Generic best practices
        recommendations.extend(
            [
                "Implement comprehensive input validation",
                "Add security unit tests for new functionality",
                "Document security considerations in PR description",
            ]
        )

        return recommendations[:10]  # Limit to top 10

    def _identify_blocking_issues(
        self,
        vulnerabilities: List[SecurityVulnerability],
        compliance_issues: List[Dict],
    ) -> List[str]:
        """Identify issues that should block the merge"""
        blocking = []

        # Critical vulnerabilities always block
        critical_vulns = [
            v for v in vulnerabilities if v.severity == "critical"]
        for vuln in critical_vulns:
            blocking.append(
                f"CRITICAL: {vuln.description} in {vuln.file_path}")

        # Secrets exposure always blocks
        secrets_vulns = [v for v in vulnerabilities if v.category == "secrets"]
        for secret in secrets_vulns:
            blocking.append(f"SECRET EXPOSURE: {secret.description}")

        # Too many high-severity issues
        high_vulns = [v for v in vulnerabilities if v.severity == "high"]
        if len(high_vulns) > self.security_thresholds["max_high_vulns"]:
            blocking.append(
                f"TOO MANY HIGH-SEVERITY ISSUES: {len(high_vulns)} found")

        return blocking

    async def _generate_security_insights(
        self,
        pr,
        vulnerabilities: List[SecurityVulnerability],
        compliance_issues: List[Dict],
        threat_model: Dict,
    ) -> Dict:
        """Generate AI-powered security insights"""

        context = f"""
        Security Review for PR: {pr.title}
        Files Changed: {len(list(pr.get_files()))}
        
        Vulnerabilities Found: {len(vulnerabilities)}
        - Critical: {len([v for v in vulnerabilities if v.severity == 'critical'])}
        - High: {len([v for v in vulnerabilities if v.severity == 'high'])}
        - Medium: {len([v for v in vulnerabilities if v.severity == 'medium'])}
        - Low: {len([v for v in vulnerabilities if v.severity == 'low'])}
        
        Compliance Issues: {len(compliance_issues)}
        Overall Threat Level: {threat_model.get('overall_threat_level', 'unknown')}
        """

        prompt = f"""
        As a security specialist reviewing this PR for an AI-KindleMint system:

        {context}

        Provide security insights focusing on:
        1. Risk assessment and business impact
        2. Attack vectors and potential exploits
        3. Security posture improvement recommendations
        4. Incident response considerations
        5. Specific next steps for security hardening

        Focus on actionable security guidance for the development team.
        """

        try:
            response = await self.anthropic.messages.acreate(
                model="claude-3-sonnet-20240229",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )

            insights = {
                "security_analysis": response.content[0].text,
                "confidence": 0.90,
                "key_risks": self._extract_key_risks(response.content[0].text),
                "mitigation_strategies": self._extract_mitigation_strategies(
                    response.content[0].text
                ),
            }

        except Exception as e:
            self.logger.warning(f"AI security insights failed: {e}")
            insights = {
                "security_analysis": "AI security analysis unavailable",
                "confidence": 0.5,
                "key_risks": ["Manual security review required"],
                "mitigation_strategies": ["Standard security review process"],
            }

        return insights

    def _extract_key_risks(self, ai_response: str) -> List[str]:
        """Extract key security risks from AI response"""
        risks = []
        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["risk", "threat", "vulnerability", "exploit"]
            ):
                risks.append(line.strip())
        return risks[:5]

    def _extract_mitigation_strategies(self, ai_response: str) -> List[str]:
        """Extract mitigation strategies from AI response"""
        strategies = []
        lines = ai_response.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["mitigate", "fix", "secure", "protect"]
            ):
                strategies.append(line.strip())
        return strategies[:5]

    async def _post_security_comment(self, pr, assessment: SecurityAssessment) -> None:
        """Post comprehensive security review comment"""

        # Risk level emoji mapping
        risk_emoji = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "✅"}

        comment = f"""## 🔒 AI Security Reviewer - Comprehensive Security Analysis

**Security Risk:** {risk_emoji.get(assessment.overall_risk, '❓')} {assessment.overall_risk.upper()} (Score: {assessment.security_score:.1f}/100)

### 🛡️ Vulnerability Summary
"""

        if assessment.vulnerabilities:
            # Group by severity
            vuln_by_severity = {}
            for vuln in assessment.vulnerabilities:
                if vuln.severity not in vuln_by_severity:
                    vuln_by_severity[vuln.severity] = []
                vuln_by_severity[vuln.severity].append(vuln)

            for severity in ["critical", "high", "medium", "low"]:
                if severity in vuln_by_severity:
                    vulns = vuln_by_severity[severity]
                    comment += f"**{severity.upper()}:** {len(vulns)} found\n"
                    for vuln in vulns[:3]:  # Show top 3 per severity
                        comment += f"- {vuln.description} in `{vuln.file_path}`\n"
                    if len(vulns) > 3:
                        comment += f"- ... and {len(vulns) - 3} more\n"
        else:
            comment += "✅ No vulnerabilities detected\n"

        comment += """
### 📋 Compliance Analysis
"""

        if assessment.compliance_issues:
            for issue in assessment.compliance_issues[:5]:
                comment += f"- **{issue['standard']}:** {issue['description']}\n"
        else:
            comment += "✅ No compliance issues detected\n"

        comment += f"""
### 🎯 Threat Model Analysis
**Overall Threat Level:** {assessment.threat_model.get('overall_threat_level', 'Unknown')}

**Attack Surfaces Identified:**
"""

        attack_surfaces = assessment.threat_model.get("attack_surfaces", {})
        for surface, affected in attack_surfaces.items():
            status = "⚠️ EXPOSED" if affected else "✅ Secure"
            comment += f"- {surface.replace('_', ' ').title()}: {status}\n"

        if assessment.blocking_issues:
            comment += f"""
### 🚨 BLOCKING SECURITY ISSUES
"""
            for issue in assessment.blocking_issues:
                comment += f"- {issue}\n"

        comment += f"""
### 💡 Security Recommendations
"""
        for rec in assessment.recommendations[:5]:
            comment += f"- {rec}\n"

        comment += f"""
### 🔍 Next Steps
"""

        if assessment.overall_risk in ["critical", "high"]:
            comment += (
                "❌ **MERGE BLOCKED** - Critical security issues must be resolved\n"
            )
        elif assessment.overall_risk == "medium":
            comment += "⚠️ **SECURITY REVIEW REQUIRED** - Address issues before merge\n"
        else:
            comment += "✅ **SECURITY APPROVED** - No blocking security issues\n"

        comment += f"""
---
*Security review by AI Security Reviewer at {datetime.now().isoformat()}*
*Vulnerability Scanning • Threat Modeling • Compliance Validation*
"""

        try:
            pr.create_issue_comment(comment)
            self.logger.info(f"Posted security review to PR #{pr.number}")
        except Exception as e:
            self.logger.error(f"Failed to post security comment: {e}")


# CLI interface
async def main():
    """CLI interface for AI Security Reviewer Agent"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="AI Security Reviewer Agent")
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

    # Initialize Security Reviewer Agent
    agent = AISecurityReviewerAgent(github_token, anthropic_key)

    print(f"🔒 Starting security review of {args.repo} PR #{args.pr}")

    # Perform security review
    assessment = await agent.perform_security_review(args.repo, args.pr)

    print(f"\n✅ Security review completed!")
    print(f"🛡️ Risk Level: {assessment.overall_risk.upper()}")
    print(f"📊 Security Score: {assessment.security_score:.1f}/100")
    print(f"🚨 Vulnerabilities: {len(assessment.vulnerabilities)}")

    if assessment.blocking_issues:
        print(f"🚫 BLOCKING ISSUES:")
        for issue in assessment.blocking_issues:
            print(f"   - {issue}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
