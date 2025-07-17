"""
AI Development Team Orchestrator - Coordinates all AI teammates for autonomous development

This orchestrator acts as the development team lead, coordinating:
- Code Review Agent for technical analysis
- Technical Lead Agent for strategic decisions
- Security Reviewer Agent for security validation
- Architecture Guardian Agent for design integrity
- Integration with business orchestrators for holistic decisions
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import anthropic
from github import Github

# Import business orchestrators for integration
from ...orchestrator.competitive_intelligence_orchestrator import (
    CompetitiveIntelligenceOrchestrator,
)
from ...orchestrator.tactical_advantage_orchestrator import (
    TacticalAdvantageOrchestrator,
)
from .architecture_guardian_agent import AIArchitectureGuardianAgent
from .code_review_agent import AICodeReviewAgent
from .security_reviewer_agent import AISecurityReviewerAgent
from .technical_lead_agent import AITechnicalLeadAgent


@dataclass
class TeamDecision:
    """Represents a coordinated team decision"""

    final_decision: str  # merge, hold, reject, escalate
    confidence: float
    team_consensus: bool
    primary_reasoning: str
    dissenting_opinions: List[str]
    business_alignment: str
    risk_assessment: Dict
    escalation_triggers: List[str]
    execution_plan: List[str]


@dataclass
class TeamAnalysis:
    """Complete team analysis results"""

    code_review_result: Dict
    technical_lead_result: Dict
    security_assessment: Dict
    architectural_assessment: Dict
    business_context: Dict
    team_decision: TeamDecision
    coordination_metrics: Dict


class AIDevelopmentTeamOrchestrator:
    """
    Coordinates all AI development teammates for autonomous development

    Capabilities:
    - Orchestrates comprehensive PR reviews by specialized AI teammates
    - Integrates technical and business intelligence for decisions
    - Manages team consensus and handles disagreements
    - Provides autonomous merge decisions with full context
    - Escalates complex decisions to human oversight when needed
    - Tracks team performance and coordination metrics
    """

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger(__name__)

        # Initialize AI teammates
        self.code_reviewer = AICodeReviewAgent(github_token, anthropic_api_key)
        self.technical_lead = AITechnicalLeadAgent(
            github_token, anthropic_api_key)
        self.security_reviewer = AISecurityReviewerAgent(
            github_token, anthropic_api_key
        )
        self.architecture_guardian = AIArchitectureGuardianAgent(
            github_token, anthropic_api_key
        )

        # Initialize business orchestrators
        self.competitive_intel = CompetitiveIntelligenceOrchestrator()
        self.tactical_advantage = TacticalAdvantageOrchestrator()

        # Team coordination parameters
        self.team_config = {
            "require_consensus": True,
            "escalation_threshold": 0.3,  # Escalate if confidence < 30%
            "security_veto_power": True,  # Security can veto any decision
            "architecture_veto_power": True,  # Architecture can veto structural changes
            "min_team_confidence": 0.75,  # Minimum confidence for autonomous decisions
            "parallel_analysis": True,  # Run analyses in parallel for speed
            "business_integration": True,  # Integrate with business orchestrators
        }

        # Decision weights for team members
        self.decision_weights = {
            "code_reviewer": 0.25,
            "technical_lead": 0.35,  # Highest weight as team lead
            "security_reviewer": 0.20,
            "architecture_guardian": 0.20,
        }

    async def orchestrate_team_review(
        self, repo_name: str, pr_number: int
    ) -> TeamAnalysis:
        """
        Orchestrate comprehensive team review of a PR

        Coordinates all AI teammates to provide:
        - Technical code analysis
        - Strategic business assessment
        - Security validation
        - Architectural review
        - Final team decision with consensus
        """
        self.logger.info(
            f"🚀 Starting AI Development Team review of PR #{pr_number}")

        try:
            # Get PR details for context
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Phase 1: Parallel technical analysis by all teammates
            self.logger.info(
                "Phase 1: Parallel technical analysis by AI teammates")

            if self.team_config["parallel_analysis"]:
                # Run all analyses in parallel for speed
                code_review_task = self.code_reviewer.review_pull_request(
                    repo_name, pr_number
                )
                security_review_task = self.security_reviewer.perform_security_review(
                    repo_name, pr_number
                )
                architecture_review_task = (
                    self.architecture_guardian.perform_architectural_review(
                        repo_name, pr_number
                    )
                )

                # Wait for all technical analyses to complete
                code_review_result, security_assessment, architectural_assessment = (
                    await asyncio.gather(
                        code_review_task,
                        security_review_task,
                        architecture_review_task,
                        return_exceptions=True,
                    )
                )

                # Handle any exceptions
                if isinstance(code_review_result, Exception):
                    self.logger.error(
                        f"Code review failed: {code_review_result}")
                    code_review_result = {"error": str(code_review_result)}

                if isinstance(security_assessment, Exception):
                    self.logger.error(
                        f"Security review failed: {security_assessment}")
                    security_assessment = {"error": str(security_assessment)}

                if isinstance(architectural_assessment, Exception):
                    self.logger.error(
                        f"Architecture review failed: {architectural_assessment}"
                    )
                    architectural_assessment = {
                        "error": str(architectural_assessment)}

            else:
                # Sequential analysis if parallel is disabled
                code_review_result = await self.code_reviewer.review_pull_request(
                    repo_name, pr_number
                )
                security_assessment = (
                    await self.security_reviewer.perform_security_review(
                        repo_name, pr_number
                    )
                )
                architectural_assessment = (
                    await self.architecture_guardian.perform_architectural_review(
                        repo_name, pr_number
                    )
                )

            # Phase 2: Business context integration
            self.logger.info("Phase 2: Business context integration")
            business_context = await self._gather_business_context(
                pr, code_review_result, security_assessment, architectural_assessment
            )

            # Phase 3: Technical Lead strategic analysis
            self.logger.info("Phase 3: Technical Lead strategic analysis")
            technical_lead_result = await self.technical_lead.make_strategic_decision(
                repo_name, pr_number, code_review_result
            )

            # Phase 4: Team coordination and consensus building
            self.logger.info(
                "Phase 4: Team coordination and consensus building")
            team_decision = await self._coordinate_team_decision(
                pr,
                code_review_result,
                technical_lead_result,
                security_assessment,
                architectural_assessment,
                business_context,
            )

            # Phase 5: Execution planning
            self.logger.info("Phase 5: Execution planning")
            execution_plan = await self._create_execution_plan(team_decision, pr)
            team_decision.execution_plan = execution_plan

            # Calculate coordination metrics
            coordination_metrics = self._calculate_coordination_metrics(
                code_review_result,
                technical_lead_result,
                security_assessment,
                architectural_assessment,
            )

            # Create comprehensive team analysis
            team_analysis = TeamAnalysis(
                code_review_result=code_review_result,
                technical_lead_result=technical_lead_result,
                security_assessment=security_assessment,
                architectural_assessment=architectural_assessment,
                business_context=business_context,
                team_decision=team_decision,
                coordination_metrics=coordination_metrics,
            )

            # Post final team decision
            await self._post_team_decision_comment(pr, team_analysis)

            # Execute decision if autonomous
            if (
                team_decision.final_decision == "merge"
                and team_decision.confidence >= self.team_config["min_team_confidence"]
            ):
                await self._execute_autonomous_merge(pr, team_decision)

            return team_analysis

        except Exception as e:
            self.logger.error(f"Team orchestration failed: {e}")
            return TeamAnalysis(
                code_review_result={"error": "Analysis failed"},
                technical_lead_result={"error": "Decision failed"},
                security_assessment={"error": "Security scan failed"},
                architectural_assessment={
                    "error": "Architecture review failed"},
                business_context={"error": "Business analysis failed"},
                team_decision=TeamDecision(
                    final_decision="escalate",
                    confidence=0.0,
                    team_consensus=False,
                    primary_reasoning="Team orchestration failure",
                    dissenting_opinions=[f"System error: {str(e)}"],
                    business_alignment="unknown",
                    risk_assessment={"system": "high"},
                    escalation_triggers=["orchestration_failure"],
                    execution_plan=["Manual review required"],
                ),
                coordination_metrics={"error": str(e)},
            )

    async def _gather_business_context(
        self, pr, code_review: Dict, security: Dict, architecture: Dict
    ) -> Dict:
        """Gather business context by integrating with business orchestrators"""

        business_context = {
            "competitive_implications": {},
            "tactical_advantages": {},
            "market_opportunities": [],
            "business_risks": [],
            "strategic_alignment": "unknown",
        }

        if self.team_config["business_integration"]:
            try:
                # Get competitive intelligence context
                files_changed = [f.filename for f in pr.get_files()]

                # Analyze competitive implications
                if any("automation" in f or "orchestrator" in f for f in files_changed):
                    business_context["competitive_implications"] = {
                        "affects_core_advantage": True,
                        "competitive_risk": "medium",
                        "market_positioning_impact": "significant",
                    }

                # Assess tactical advantages
                if code_review.get("merge_decision", {}).get("confidence", 0) > 0.8:
                    business_context["tactical_advantages"] = {
                        "technical_advancement": True,
                        "competitive_differentiation": "enhanced",
                        "market_readiness": "improved",
                    }

                # Business risk assessment
                if security.get("overall_risk") in ["critical", "high"]:
                    business_context["business_risks"].append(
                        "Security vulnerabilities threaten business operations"
                    )

                if architecture.get("overall_health") == "poor":
                    business_context["business_risks"].append(
                        "Architectural degradation affects scalability"
                    )

                # Strategic alignment
                if (
                    code_review.get("merge_decision", {}).get(
                        "confidence", 0) > 0.7
                    and security.get("overall_risk", "high") in ["low", "medium"]
                    and architecture.get("overall_health", "poor")
                    in ["good", "excellent"]
                ):
                    business_context["strategic_alignment"] = "strong"
                else:
                    business_context["strategic_alignment"] = "weak"

            except Exception as e:
                self.logger.warning(
                    f"Business context integration failed: {e}")
                business_context["error"] = str(e)

        return business_context

    async def _coordinate_team_decision(
        self,
        pr,
        code_review: Dict,
        technical_lead: Dict,
        security: Dict,
        architecture: Dict,
        business_context: Dict,
    ) -> TeamDecision:
        """Coordinate team decision with consensus building"""

        # Collect individual decisions and confidences
        individual_decisions = {
            "code_reviewer": {
                "decision": code_review.get("merge_decision", {}).get("action", "wait"),
                "confidence": code_review.get("merge_decision", {}).get(
                    "confidence", 0.5
                ),
            },
            "technical_lead": {
                "decision": (
                    technical_lead.decision
                    if hasattr(technical_lead, "decision")
                    else "wait"
                ),
                "confidence": (
                    technical_lead.confidence
                    if hasattr(technical_lead, "confidence")
                    else 0.5
                ),
            },
            "security_reviewer": {
                "decision": (
                    "merge"
                    if security.get("overall_risk", "high") in ["low", "medium"]
                    else "reject"
                ),
                "confidence": (
                    (security.get("security_score", 50) / 100)
                    if "security_score" in security
                    else 0.5
                ),
            },
            "architecture_guardian": {
                "decision": (
                    "merge"
                    if architecture.get("overall_health", "poor")
                    in ["good", "excellent"]
                    else "wait"
                ),
                "confidence": (
                    (architecture.get("pattern_consistency_score", 50) / 100)
                    if "pattern_consistency_score" in architecture
                    else 0.5
                ),
            },
        }

        # Check for security/architecture vetoes
        security_blocks = (
            security.get("overall_risk") == "critical"
            or len(security.get("blocking_issues", [])) > 0
        )
        architecture_blocks = (
            architecture.get("overall_health") == "poor"
            or len(
                [
                    v
                    for v in architecture.get("violations", [])
                    if v.severity == "critical"
                ]
            )
            > 0
        )

        if security_blocks and self.team_config["security_veto_power"]:
            return TeamDecision(
                final_decision="reject",
                confidence=0.95,
                team_consensus=False,
                primary_reasoning="Security veto: Critical security issues detected",
                dissenting_opinions=[],
                business_alignment="risk_mitigation",
                risk_assessment={"security": "critical"},
                escalation_triggers=["security_veto"],
                execution_plan=["Fix security issues before resubmission"],
            )

        if architecture_blocks and self.team_config["architecture_veto_power"]:
            return TeamDecision(
                final_decision="reject",
                confidence=0.90,
                team_consensus=False,
                primary_reasoning="Architecture veto: Critical architectural violations detected",
                dissenting_opinions=[],
                business_alignment="long_term_sustainability",
                risk_assessment={"architecture": "critical"},
                escalation_triggers=["architecture_veto"],
                execution_plan=[
                    "Address architectural violations before resubmission"],
            )

        # Calculate weighted decision
        weighted_decisions = {}
        for teammate, weight in self.decision_weights.items():
            decision_data = individual_decisions[teammate]
            weighted_decisions[teammate] = {
                "decision": decision_data["decision"],
                "weighted_confidence": decision_data["confidence"] * weight,
            }

        # Determine consensus
        decision_counts = {}
        total_weighted_confidence = 0

        for teammate_data in weighted_decisions.values():
            decision = teammate_data["decision"]
            confidence = teammate_data["weighted_confidence"]

            if decision not in decision_counts:
                decision_counts[decision] = {"count": 0, "confidence": 0}

            decision_counts[decision]["count"] += 1
            decision_counts[decision]["confidence"] += confidence
            total_weighted_confidence += confidence

        # Find consensus decision
        consensus_decision = max(
            decision_counts.items(), key=lambda x: x[1]["confidence"]
        )
        final_decision = consensus_decision[0]
        team_confidence = total_weighted_confidence

        # Check for consensus
        team_consensus = (
            decision_counts[final_decision]["count"] >= 3
        )  # Majority consensus

        # Collect dissenting opinions
        dissenting_opinions = []
        for teammate, data in weighted_decisions.items():
            if data["decision"] != final_decision:
                dissenting_opinions.append(
                    f"{teammate}: prefers {data['decision']}")

        # Determine business alignment
        business_alignment = self._assess_business_alignment(
            final_decision, business_context
        )

        # Risk assessment
        risk_assessment = {
            "technical": "low" if team_confidence > 0.8 else "medium",
            "business": business_context.get("strategic_alignment", "unknown"),
            "consensus": "low" if team_consensus else "high",
        }

        # Escalation triggers
        escalation_triggers = []
        if team_confidence < self.team_config["escalation_threshold"]:
            escalation_triggers.append("low_confidence")
        if not team_consensus and self.team_config["require_consensus"]:
            escalation_triggers.append("no_consensus")
        if len(business_context.get("business_risks", [])) > 2:
            escalation_triggers.append("high_business_risk")

        # Adjust decision based on escalation triggers
        if escalation_triggers and final_decision == "merge":
            final_decision = "escalate"

        return TeamDecision(
            final_decision=final_decision,
            confidence=team_confidence,
            team_consensus=team_consensus,
            primary_reasoning=self._generate_primary_reasoning(
                final_decision, weighted_decisions, business_context
            ),
            dissenting_opinions=dissenting_opinions,
            business_alignment=business_alignment,
            risk_assessment=risk_assessment,
            escalation_triggers=escalation_triggers,
            execution_plan=[],  # Will be filled later
        )

    def _assess_business_alignment(self, decision: str, business_context: Dict) -> str:
        """Assess how well the decision aligns with business objectives"""

        strategic_alignment = business_context.get(
            "strategic_alignment", "unknown")
        business_risks = len(business_context.get("business_risks", []))

        if decision == "merge":
            if strategic_alignment == "strong" and business_risks == 0:
                return "excellent"
            elif strategic_alignment == "strong" or business_risks <= 1:
                return "good"
            else:
                return "weak"
        elif decision == "reject":
            if business_risks > 1:
                return "risk_mitigation"
            else:
                return "conservative"
        else:  # wait, escalate
            return "cautious"

    def _generate_primary_reasoning(
        self, decision: str, weighted_decisions: Dict, business_context: Dict
    ) -> str:
        """Generate primary reasoning for the team decision"""

        # Find the highest confidence contributor
        top_contributor = max(
            weighted_decisions.items(), key=lambda x: x[1]["weighted_confidence"]
        )

        if decision == "merge":
            return f"Team consensus for merge based on {top_contributor[0]} analysis with strong technical confidence and {business_context.get('strategic_alignment', 'unknown')} business alignment"
        elif decision == "reject":
            return "Team consensus to reject based on critical issues identified by multiple teammates"
        elif decision == "escalate":
            return "Team escalation due to complexity requiring human oversight"
        else:
            return "Team decision to wait for additional information or fixes"

    async def _create_execution_plan(
        self, team_decision: TeamDecision, pr
    ) -> List[str]:
        """Create execution plan based on team decision"""

        execution_plan = []

        if team_decision.final_decision == "merge":
            execution_plan.extend(
                [
                    "Enable GitHub auto-merge",
                    "Monitor merge success",
                    "Validate post-merge CI/CD pipeline",
                    "Update team metrics",
                ]
            )

        elif team_decision.final_decision == "reject":
            execution_plan.extend(
                [
                    "Close PR with detailed feedback",
                    "Provide remediation guidance",
                    "Schedule follow-up review",
                    "Update rejection metrics",
                ]
            )

        elif team_decision.final_decision == "escalate":
            execution_plan.extend(
                [
                    "Notify human reviewers",
                    "Prepare escalation report",
                    "Schedule review meeting",
                    "Provide decision context",
                ]
            )

        else:  # wait
            execution_plan.extend(
                [
                    "Request additional information",
                    "Set review reminder",
                    "Monitor for updates",
                    "Re-evaluate when ready",
                ]
            )

        return execution_plan

    def _calculate_coordination_metrics(
        self,
        code_review: Dict,
        technical_lead: Dict,
        security: Dict,
        architecture: Dict,
    ) -> Dict:
        """Calculate team coordination metrics"""

        # Extract confidence scores
        confidences = []
        if (
            "merge_decision" in code_review
            and "confidence" in code_review["merge_decision"]
        ):
            confidences.append(code_review["merge_decision"]["confidence"])
        if hasattr(technical_lead, "confidence"):
            confidences.append(technical_lead.confidence)
        if "security_score" in security:
            confidences.append(security["security_score"] / 100)
        if "pattern_consistency_score" in architecture:
            confidences.append(architecture["pattern_consistency_score"] / 100)

        # Calculate metrics
        avg_confidence = sum(confidences) / \
            len(confidences) if confidences else 0
        confidence_variance = (
            sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
            if confidences
            else 0
        )

        return {
            "team_size": 4,
            "avg_confidence": avg_confidence,
            "confidence_variance": confidence_variance,
            "coordination_quality": (
                "high"
                if confidence_variance < 0.1
                else "medium" if confidence_variance < 0.25 else "low"
            ),
            "analysis_completeness": sum(
                1
                for result in [code_review, technical_lead, security, architecture]
                if "error" not in result
            ),
            "consensus_strength": 1.0 - confidence_variance,
        }

    async def _post_team_decision_comment(
        self, pr, team_analysis: TeamAnalysis
    ) -> None:
        """Post comprehensive team decision comment"""

        decision = team_analysis.team_decision

        # Decision emoji mapping
        decision_emoji = {"merge": "✅", "reject": "❌",
                          "escalate": "🚨", "wait": "⏳"}

        comment = f"""## 🚀 AI Development Team - Final Decision

**Team Decision:** {decision_emoji.get(decision.final_decision, '❓')} **{decision.final_decision.upper()}** (Confidence: {decision.confidence:.1%})

### 👥 Team Analysis Summary
**Code Review:** {team_analysis.code_review_result.get('merge_decision', {}).get('action', 'N/A').title()}  
**Technical Lead:** {team_analysis.technical_lead_result.decision if hasattr(team_analysis.technical_lead_result, 'decision') else 'N/A'}  
**Security Review:** {'✅ Clear' if team_analysis.security_assessment.get('overall_risk', 'high') in ['low', 'medium'] else '⚠️ Issues'}  
**Architecture:** {team_analysis.architectural_assessment.get('overall_health', 'Unknown').title()}

### 🎯 Decision Factors
**Team Consensus:** {'Yes' if decision.team_consensus else 'No'}  
**Business Alignment:** {decision.business_alignment.replace('_', ' ').title()}  
**Primary Reasoning:** {decision.primary_reasoning}

### 📊 Team Coordination Metrics
**Average Confidence:** {team_analysis.coordination_metrics.get('avg_confidence', 0):.1%}  
**Coordination Quality:** {team_analysis.coordination_metrics.get('coordination_quality', 'Unknown').title()}  
**Consensus Strength:** {team_analysis.coordination_metrics.get('consensus_strength', 0):.1%}

### ⚖️ Risk Assessment
"""

        for risk_type, level in decision.risk_assessment.items():
            comment += f"- **{risk_type.title()}:** {level.upper()}\n"

        if decision.dissenting_opinions:
            comment += """
### 🗣️ Dissenting Opinions
"""
            for opinion in decision.dissenting_opinions:
                comment += f"- {opinion}\n"

        if decision.escalation_triggers:
            comment += """
### 🚨 Escalation Triggers
"""
            for trigger in decision.escalation_triggers:
                comment += f"- {trigger.replace('_', ' ').title()}\n"

        comment += """
### 📋 Execution Plan
"""
        for step in decision.execution_plan:
            comment += f"- {step}\n"

        comment += f"""
### 🔍 Individual Team Member Reports
- 🔎 **Code Review Agent:** [See detailed analysis above]
- 🎯 **Technical Lead Agent:** [See strategic decision above]  
- 🔒 **Security Reviewer Agent:** [See security analysis above]
- 🏗️ **Architecture Guardian Agent:** [See architectural review above]

---
*Coordinated decision by AI Development Team at {datetime.now().isoformat()}*
*Team Lead: Technical Lead Agent • Coordination: Development Team Orchestrator*
"""

        try:
            pr.create_issue_comment(comment)
            self.logger.info(f"Posted team decision to PR #{pr.number}")
        except Exception as e:
            self.logger.error(f"Failed to post team decision: {e}")

    async def _execute_autonomous_merge(self, pr, team_decision: TeamDecision) -> None:
        """Execute autonomous merge with team coordination"""

        try:
            self.logger.info(f"Executing autonomous merge for PR #{pr.number}")

            # Enable auto-merge
            pr.enable_automerge(merge_method="merge")

            # Post execution confirmation
            execution_comment = f"""## 🤖 Autonomous Merge Executed

The AI Development Team has **automatically enabled merge** for this PR based on:

✅ **High Team Confidence:** {team_decision.confidence:.1%}  
✅ **Team Consensus:** {'Achieved' if team_decision.team_consensus else 'Majority'}  
✅ **Business Alignment:** {team_decision.business_alignment.replace('_', ' ').title()}  
✅ **Risk Assessment:** All risks within acceptable thresholds

**Merge will complete automatically** once all required status checks pass.

---
*Autonomous execution by AI Development Team • Human oversight available via PR comments*
"""

            pr.create_issue_comment(execution_comment)
            self.logger.info(f"Autonomous merge enabled for PR #{pr.number}")

        except Exception as e:
            self.logger.error(f"Autonomous merge execution failed: {e}")

            # Post failure notification
            failure_comment = f"""## ⚠️ Autonomous Merge Failed

The AI Development Team attempted to enable auto-merge but encountered an error:
```
{str(e)}
```

**Manual intervention required.** The team decision remains: **{team_decision.final_decision.upper()}**

Please enable merge manually or contact repository administrators.
"""

            try:
                pr.create_issue_comment(failure_comment)
            except:
                pass  # Don't fail on comment failure


# CLI interface
async def main():
    """CLI interface for AI Development Team Orchestrator"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="AI Development Team Orchestrator")
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
    parser.add_argument(
        "--config", help="Path to team configuration JSON file")

    args = parser.parse_args()

    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    anthropic_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY")

    if not github_token or not anthropic_key:
        print("❌ Error: GitHub token and Anthropic API key are required")
        return

    # Initialize AI Development Team Orchestrator
    orchestrator = AIDevelopmentTeamOrchestrator(github_token, anthropic_key)

    # Load custom configuration if provided
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config = json.load(f)
            orchestrator.team_config.update(config)

    print(
        f"🚀 Starting AI Development Team review of {args.repo} PR #{args.pr}")
    print(
        "👥 Team: Code Reviewer, Technical Lead, Security Reviewer, Architecture Guardian"
    )

    # Orchestrate team review
    team_analysis = await orchestrator.orchestrate_team_review(args.repo, args.pr)

    print("\n✅ Team review completed!")
    print(
        f"🎯 Final Decision: {team_analysis.team_decision.final_decision.upper()}")
    print(f"👥 Team Confidence: {team_analysis.team_decision.confidence:.1%}")
    print(
        f"🤝 Consensus: {'Yes' if team_analysis.team_decision.team_consensus else 'No'}"
    )

    if team_analysis.team_decision.escalation_triggers:
        print(
            f"🚨 Escalation Required: {', '.join(team_analysis.team_decision.escalation_triggers)}"
        )

    print("\n📊 Coordination Metrics:")
    print(
        f"   Quality: {team_analysis.coordination_metrics.get('coordination_quality', 'Unknown')}"
    )
    print(
        f"   Avg Confidence: {team_analysis.coordination_metrics.get('avg_confidence', 0):.1%}"
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
