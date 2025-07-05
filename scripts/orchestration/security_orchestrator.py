#!/usr/bin/env python3
"""
Security Orchestrator - Prevents security issues in autonomous workflows

This module integrates security scanning into the orchestration system to catch
issues like hardcoded secrets, vulnerable dependencies, and security misconfigurations
before they reach production.
"""

import os
import re
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecuritySeverity(Enum):
    """Security issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityCheckType(Enum):
    """Types of security checks"""
    SECRET_DETECTION = "secret_detection"
    DEPENDENCY_SCAN = "dependency_scan"
    CODE_QUALITY = "code_quality"
    CONFIGURATION = "configuration"
    PERMISSIONS = "permissions"
    ENCRYPTION = "encryption"
    API_SECURITY = "api_security"


@dataclass
class SecurityIssue:
    """Represents a security issue found during scanning"""
    check_type: SecurityCheckType
    severity: SecuritySeverity
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    cwe_id: Optional[str] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "check_type": self.check_type.value,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "description": self.description,
            "recommendation": self.recommendation,
            "cwe_id": self.cwe_id,
            "confidence": self.confidence
        }


class SecurityOrchestrator:
    """
    Orchestrates security scanning across the development workflow.
    Integrates with worktree system and CI/CD to prevent security issues.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config = self._load_security_config()
        self.secret_patterns = self._load_secret_patterns()
        self.issues: List[SecurityIssue] = []
        
    def _load_security_config(self) -> Dict:
        """Load security scanning configuration"""
        config_path = self.project_root / "scripts/orchestration/security_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        
        return {
            "enabled_checks": [
                "secret_detection",
                "dependency_scan", 
                "code_quality",
                "configuration"
            ],
            "severity_threshold": "medium",
            "fail_on_critical": True,
            "exclude_patterns": [
                "*.pyc",
                "__pycache__/*",
                ".git/*",
                "node_modules/*",
                "venv/*",
                ".env.example"
            ],
            "secret_detection": {
                "entropy_threshold": 4.5,
                "check_git_history": False,
                "whitelist_files": [".env.example", "docs/*"]
            }
        }
    
    def _load_secret_patterns(self) -> List[Dict]:
        """Load patterns for detecting secrets"""
        return [
            {
                "name": "Generic Password",
                "pattern": r'(?i)(password|pwd|pass)\s*[=:]\s*["\']?([a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{8,})["\']?',
                "severity": SecuritySeverity.CRITICAL,
                "confidence": 0.8
            },
            {
                "name": "API Key",
                "pattern": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                "severity": SecuritySeverity.CRITICAL,
                "confidence": 0.9
            },
            {
                "name": "Secret Key",
                "pattern": r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9]{16,})["\']?',
                "severity": SecuritySeverity.CRITICAL,
                "confidence": 0.9
            },
            {
                "name": "Database URL",
                "pattern": r'(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*["\']?(mongodb://|mysql://|postgresql://|sqlite://)[^\s"\']+["\']?',
                "severity": SecuritySeverity.HIGH,
                "confidence": 0.95
            },
            {
                "name": "JWT Token",
                "pattern": r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
                "severity": SecuritySeverity.HIGH,
                "confidence": 0.95
            },
            {
                "name": "Private Key",
                "pattern": r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----',
                "severity": SecuritySeverity.CRITICAL,
                "confidence": 1.0
            },
            {
                "name": "AWS Access Key",
                "pattern": r'AKIA[0-9A-Z]{16}',
                "severity": SecuritySeverity.CRITICAL,
                "confidence": 1.0
            },
            {
                "name": "Generic Token",
                "pattern": r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9]{32,})["\']?',
                "severity": SecuritySeverity.HIGH,
                "confidence": 0.7
            }
        ]
    
    async def scan_for_security_issues(self, target_path: Optional[str] = None) -> List[SecurityIssue]:
        """
        Comprehensive security scan of the codebase
        
        Args:
            target_path: Specific path to scan, defaults to project root
            
        Returns:
            List of security issues found
        """
        scan_path = Path(target_path) if target_path else self.project_root
        self.issues = []
        
        logger.info(f"🔍 Starting security scan of {scan_path}")
        
        # Run all enabled security checks
        checks = []
        
        if "secret_detection" in self.config["enabled_checks"]:
            checks.append(self._scan_for_secrets(scan_path))
        
        if "dependency_scan" in self.config["enabled_checks"]:
            checks.append(self._scan_dependencies(scan_path))
        
        if "code_quality" in self.config["enabled_checks"]:
            checks.append(self._scan_code_quality(scan_path))
        
        if "configuration" in self.config["enabled_checks"]:
            checks.append(self._scan_configuration(scan_path))
        
        # Run all checks concurrently
        await asyncio.gather(*checks)
        
        # Sort by severity
        severity_order = {
            SecuritySeverity.CRITICAL: 0,
            SecuritySeverity.HIGH: 1,
            SecuritySeverity.MEDIUM: 2,
            SecuritySeverity.LOW: 3,
            SecuritySeverity.INFO: 4
        }
        
        self.issues.sort(key=lambda x: severity_order[x.severity])
        
        logger.info(f"🔍 Security scan complete. Found {len(self.issues)} issues")
        return self.issues
    
    async def _scan_for_secrets(self, scan_path: Path):
        """Scan for hardcoded secrets and credentials"""
        logger.info("🔐 Scanning for hardcoded secrets...")
        
        for file_path in self._get_scannable_files(scan_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check against secret patterns
                for pattern_def in self.secret_patterns:
                    matches = re.finditer(pattern_def["pattern"], content, re.MULTILINE)
                    
                    for match in matches:
                        # Calculate line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Skip if in whitelist
                        rel_path = str(file_path.relative_to(self.project_root))
                        if self._is_whitelisted(rel_path):
                            continue
                        
                        # Check entropy for generic patterns
                        suspected_secret = match.group(2) if len(match.groups()) >= 2 else match.group(0)
                        if self._calculate_entropy(suspected_secret) < self.config["secret_detection"]["entropy_threshold"]:
                            continue
                        
                        self.issues.append(SecurityIssue(
                            check_type=SecurityCheckType.SECRET_DETECTION,
                            severity=pattern_def["severity"],
                            file_path=rel_path,
                            line_number=line_num,
                            description=f"Potential {pattern_def['name']} found: {suspected_secret[:20]}...",
                            recommendation=f"Move {pattern_def['name'].lower()} to environment variable",
                            confidence=pattern_def["confidence"]
                        ))
                        
            except Exception as e:
                logger.warning(f"Error scanning {file_path}: {e}")
    
    async def _scan_dependencies(self, scan_path: Path):
        """Scan for vulnerable dependencies"""
        logger.info("📦 Scanning dependencies for vulnerabilities...")
        
        # Check requirements.txt
        req_file = scan_path / "requirements.txt"
        if req_file.exists():
            try:
                # Use safety to check for known vulnerabilities
                result = subprocess.run(
                    ["safety", "check", "-r", str(req_file), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Parse safety output
                    try:
                        vulnerabilities = json.loads(result.stdout)
                        for vuln in vulnerabilities:
                            self.issues.append(SecurityIssue(
                                check_type=SecurityCheckType.DEPENDENCY_SCAN,
                                severity=self._map_cve_severity(vuln.get("vulnerability_id", "")),
                                file_path="requirements.txt",
                                line_number=None,
                                description=f"Vulnerable dependency: {vuln.get('package_name')} {vuln.get('installed_version')}",
                                recommendation=f"Update to version {vuln.get('safe_versions', ['latest'])[0]}",
                                cwe_id=vuln.get("cve")
                            ))
                    except json.JSONDecodeError:
                        pass
                        
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("Safety tool not available or timed out")
    
    async def _scan_code_quality(self, scan_path: Path):
        """Scan for code quality security issues"""
        logger.info("🔧 Scanning code quality...")
        
        # Check for common security anti-patterns
        security_patterns = [
            {
                "pattern": r'eval\s*\(',
                "description": "Use of eval() function - potential code injection",
                "severity": SecuritySeverity.HIGH,
                "recommendation": "Use ast.literal_eval() or avoid dynamic code execution"
            },
            {
                "pattern": r'exec\s*\(',
                "description": "Use of exec() function - potential code injection", 
                "severity": SecuritySeverity.HIGH,
                "recommendation": "Avoid dynamic code execution"
            },
            {
                "pattern": r'shell=True',
                "description": "subprocess with shell=True - potential command injection",
                "severity": SecuritySeverity.MEDIUM,
                "recommendation": "Use shell=False and pass command as list"
            },
            {
                "pattern": r'pickle\.loads?\(',
                "description": "Use of pickle - potential deserialization attack",
                "severity": SecuritySeverity.MEDIUM,
                "recommendation": "Use JSON or other safe serialization formats"
            }
        ]
        
        for file_path in self._get_python_files(scan_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern_def in security_patterns:
                    matches = re.finditer(pattern_def["pattern"], content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        self.issues.append(SecurityIssue(
                            check_type=SecurityCheckType.CODE_QUALITY,
                            severity=pattern_def["severity"],
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            description=pattern_def["description"],
                            recommendation=pattern_def["recommendation"]
                        ))
                        
            except Exception as e:
                logger.warning(f"Error scanning {file_path}: {e}")
    
    async def _scan_configuration(self, scan_path: Path):
        """Scan for configuration security issues"""
        logger.info("⚙️ Scanning configuration...")
        
        # Check for insecure configurations
        config_checks = [
            {
                "file": ".env",
                "exists": True,
                "description": ".env file should not be committed",
                "severity": SecuritySeverity.HIGH,
                "recommendation": "Add .env to .gitignore"
            },
            {
                "file": ".env.example",
                "exists": False,
                "description": "Missing .env.example template",
                "severity": SecuritySeverity.LOW,
                "recommendation": "Create .env.example with template values"
            }
        ]
        
        for check in config_checks:
            file_path = scan_path / check["file"]
            file_exists = file_path.exists()
            
            if check["exists"] == file_exists and check["exists"]:
                # File exists and shouldn't
                self.issues.append(SecurityIssue(
                    check_type=SecurityCheckType.CONFIGURATION,
                    severity=check["severity"],
                    file_path=check["file"],
                    line_number=None,
                    description=check["description"],
                    recommendation=check["recommendation"]
                ))
            elif not check["exists"] and not file_exists:
                # File doesn't exist and should
                self.issues.append(SecurityIssue(
                    check_type=SecurityCheckType.CONFIGURATION,
                    severity=check["severity"],
                    file_path=check["file"],
                    line_number=None,
                    description=check["description"],
                    recommendation=check["recommendation"]
                ))
    
    def validate_commit(self, commit_files: List[str]) -> Tuple[bool, List[SecurityIssue]]:
        """
        Validate a commit for security issues
        
        Args:
            commit_files: List of files in the commit
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        logger.info(f"🔍 Validating commit with {len(commit_files)} files")
        
        commit_issues = []
        critical_found = False
        
        for file_path in commit_files:
            if not Path(file_path).exists():
                continue
                
            # Run secret detection on this file
            asyncio.run(self._scan_file_for_secrets(file_path, commit_issues))
        
        # Check for critical issues
        for issue in commit_issues:
            if issue.severity == SecuritySeverity.CRITICAL:
                critical_found = True
                
        is_safe = not critical_found if self.config["fail_on_critical"] else True
        
        return is_safe, commit_issues
    
    async def _scan_file_for_secrets(self, file_path: str, issues_list: List[SecurityIssue]):
        """Scan a single file for secrets"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for pattern_def in self.secret_patterns:
                matches = re.finditer(pattern_def["pattern"], content, re.MULTILINE)
                
                for match in matches:
                    if self._is_whitelisted(file_path):
                        continue
                        
                    line_num = content[:match.start()].count('\n') + 1
                    suspected_secret = match.group(2) if len(match.groups()) >= 2 else match.group(0)
                    
                    if self._calculate_entropy(suspected_secret) < self.config["secret_detection"]["entropy_threshold"]:
                        continue
                    
                    issues_list.append(SecurityIssue(
                        check_type=SecurityCheckType.SECRET_DETECTION,
                        severity=pattern_def["severity"],
                        file_path=file_path,
                        line_number=line_num,
                        description=f"Potential {pattern_def['name']} found",
                        recommendation=f"Move {pattern_def['name'].lower()} to environment variable",
                        confidence=pattern_def["confidence"]
                    ))
                    
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
    
    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        report = {
            "scan_timestamp": str(asyncio.get_event_loop().time()),
            "total_issues": len(self.issues),
            "issues_by_severity": {},
            "issues_by_type": {},
            "critical_files": [],
            "recommendations": [],
            "issues": [issue.to_dict() for issue in self.issues]
        }
        
        # Count by severity
        for severity in SecuritySeverity:
            count = sum(1 for issue in self.issues if issue.severity == severity)
            report["issues_by_severity"][severity.value] = count
        
        # Count by type
        for check_type in SecurityCheckType:
            count = sum(1 for issue in self.issues if issue.check_type == check_type)
            report["issues_by_type"][check_type.value] = count
        
        # Identify critical files
        file_issue_counts = {}
        for issue in self.issues:
            file_issue_counts[issue.file_path] = file_issue_counts.get(issue.file_path, 0) + 1
        
        critical_files = sorted(file_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        report["critical_files"] = [{"file": f, "issues": c} for f, c in critical_files]
        
        # Generate recommendations
        if report["issues_by_severity"].get("critical", 0) > 0:
            report["recommendations"].append("CRITICAL: Address all critical security issues immediately")
        
        if report["issues_by_type"].get("secret_detection", 0) > 0:
            report["recommendations"].append("Move hardcoded secrets to environment variables")
        
        if report["issues_by_type"].get("dependency_scan", 0) > 0:
            report["recommendations"].append("Update vulnerable dependencies")
        
        return report
    
    def _get_scannable_files(self, scan_path: Path) -> List[Path]:
        """Get list of files to scan"""
        scannable_files = []
        
        for ext in ['.py', '.js', '.ts', '.json', '.yml', '.yaml', '.env*', '.conf', '.config']:
            pattern = f"**/*{ext}" if ext != '.env*' else "**/.env*"
            scannable_files.extend(scan_path.glob(pattern))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in scannable_files:
            rel_path = str(file_path.relative_to(scan_path))
            if not any(re.match(pattern.replace('*', '.*'), rel_path) for pattern in self.config["exclude_patterns"]):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _get_python_files(self, scan_path: Path) -> List[Path]:
        """Get list of Python files to scan"""
        return list(scan_path.glob("**/*.py"))
    
    def _is_whitelisted(self, file_path: str) -> bool:
        """Check if file is whitelisted from secret detection"""
        whitelist = self.config["secret_detection"]["whitelist_files"]
        return any(re.match(pattern.replace('*', '.*'), file_path) for pattern in whitelist)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0
        
        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        import math
        entropy = 0
        text_len = len(text)
        for count in freq.values():
            p = count / text_len
            entropy -= p * math.log2(p)
        
        return entropy
    
    def _map_cve_severity(self, cve_id: str) -> SecuritySeverity:
        """Map CVE severity to our severity levels"""
        # This would typically query CVE database
        # For now, default to HIGH
        return SecuritySeverity.HIGH


async def main():
    """Run security orchestrator"""
    orchestrator = SecurityOrchestrator()
    
    # Scan for issues
    issues = await orchestrator.scan_for_security_issues()
    
    # Generate report
    report = orchestrator.generate_security_report()
    
    # Save report
    report_path = Path("reports/security")
    report_path.mkdir(parents=True, exist_ok=True)
    
    with open(report_path / f"security_report_{int(asyncio.get_event_loop().time())}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"🔍 Security scan complete:")
    print(f"  Total issues: {report['total_issues']}")
    print(f"  Critical: {report['issues_by_severity'].get('critical', 0)}")
    print(f"  High: {report['issues_by_severity'].get('high', 0)}")
    print(f"  Medium: {report['issues_by_severity'].get('medium', 0)}")
    
    if report['issues_by_severity'].get('critical', 0) > 0:
        print("⚠️  CRITICAL ISSUES FOUND - Review immediately!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())