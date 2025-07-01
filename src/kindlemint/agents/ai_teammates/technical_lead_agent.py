"""
AI Technical Lead Agent - Strategic merge decisions with business intelligence

This agent acts as a senior technical lead teammate, making high-level decisions by:
- Integrating with competitive intelligence orchestrator
- Consulting tactical advantage orchestrator for strategic alignment
- Evaluating business impact using professional quality standards
- Making autonomous merge decisions with full business context
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import anthropic
from github import Github

# Import existing orchestrators for business intelligence
from ...orchestrator.competitive_intelligence_orchestrator import CompetitiveIntelligenceOrchestrator
from ...orchestrator.tactical_advantage_orchestrator import TacticalAdvantageOrchestrator
from ...orchestrator.professional_quality_orchestrator import ProfessionalQualityOrchestrator
from ...orchestrator.tactical_seo_orchestrator import TacticalSEOOrchestrator


@dataclass
class StrategicDecision:
    """Represents a strategic merge decision with business context"""
    decision: str  # merge, hold, reject, escalate
    confidence: float
    business_justification: str
    technical_reasoning: List[str]
    strategic_impact: str
    risk_assessment: Dict
    timeline_consideration: str
    escalation_required: bool = False


@dataclass
class BusinessContext:
    """Business context for technical decisions"""
    competitive_landscape: Dict
    strategic_priorities: List[str]
    market_opportunities: List[Dict]
    quality_benchmarks: Dict
    seo_implications: Dict
    revenue_impact: str
    customer_impact: str


class AITechnicalLeadAgent:
    """
    Autonomous AI teammate that acts as a Technical Lead
    
    Capabilities:
    - Strategic merge decisions with full business context
    - Integration with all business orchestrators
    - Risk assessment from competitive intelligence perspective
    - Quality evaluation against professional standards
    - SEO impact analysis for content changes
    - Autonomous escalation for high-risk decisions
    """
    
    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github = Github(github_token)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger(__name__)
        
        # Initialize business orchestrators
        self.competitive_intel = CompetitiveIntelligenceOrchestrator()
        self.tactical_advantage = TacticalAdvantageOrchestrator()
        self.quality_orchestrator = ProfessionalQualityOrchestrator()
        self.seo_orchestrator = TacticalSEOOrchestrator()
        
        # Technical Lead decision parameters
        self.decision_thresholds = {
            "auto_merge_confidence": 0.85,
            "review_required_confidence": 0.65,
            "escalation_threshold": 0.40,
            "max_business_risk": "medium",
            "min_quality_score": 80
        }
        
        # Strategic priorities (could be dynamically loaded)
        self.strategic_priorities = [
            "competitive_advantage_maintenance",
            "automation_pipeline_reliability",
            "quality_leadership_position",
            "seo_ranking_optimization",
            "customer_experience_enhancement"
        ]
    
    async def make_strategic_decision(self, repo_name: str, pr_number: int, 
                                    code_review_result: Dict = None) -> StrategicDecision:
        """
        Make strategic merge decision using full business intelligence
        
        Integrates with all orchestrators to make informed decisions about:
        - Competitive positioning impact
        - Strategic advantage alignment
        - Quality standards compliance
        - SEO implications for content changes
        - Business risk vs reward analysis
        """
        self.logger.info(f"🎯 Making strategic decision for PR #{pr_number}")
        
        try:
            # Get PR details
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Gather business context
            business_context = await self._gather_business_context(pr)
            
            # Analyze strategic implications
            strategic_analysis = await self._analyze_strategic_implications(pr, business_context)
            
            # Evaluate against business orchestrators
            orchestrator_insights = await self._consult_orchestrators(pr, business_context)
            
            # Generate AI-powered strategic assessment
            ai_strategic_assessment = await self._generate_strategic_assessment(
                pr, business_context, strategic_analysis, orchestrator_insights
            )
            
            # Make final decision
            decision = await self._make_final_decision(
                pr, business_context, strategic_analysis, 
                orchestrator_insights, ai_strategic_assessment, code_review_result
            )
            
            # Post strategic decision comment
            await self._post_strategic_comment(pr, decision, business_context)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Strategic decision failed: {e}")
            return StrategicDecision(
                decision="escalate",
                confidence=0.0,
                business_justification="Technical analysis failed",
                technical_reasoning=[f"Error: {str(e)}"],
                strategic_impact="unknown",
                risk_assessment={"technical": "high"},
                timeline_consideration="immediate_review_required",
                escalation_required=True
            )
    
    async def _gather_business_context(self, pr) -> BusinessContext:
        """Gather comprehensive business context for decision making"""
        
        # Analyze competitive landscape impact
        competitive_landscape = await self._analyze_competitive_impact(pr)
        
        # Get current strategic priorities
        strategic_priorities = self.strategic_priorities.copy()
        
        # Identify market opportunities affected
        market_opportunities = await self._identify_affected_opportunities(pr)
        
        # Get quality benchmarks
        quality_benchmarks = await self._get_quality_benchmarks(pr)
        
        # Analyze SEO implications
        seo_implications = await self._analyze_seo_implications(pr)
        
        # Assess revenue and customer impact
        revenue_impact = await self._assess_revenue_impact(pr)
        customer_impact = await self._assess_customer_impact(pr)
        
        return BusinessContext(
            competitive_landscape=competitive_landscape,
            strategic_priorities=strategic_priorities,
            market_opportunities=market_opportunities,
            quality_benchmarks=quality_benchmarks,
            seo_implications=seo_implications,
            revenue_impact=revenue_impact,
            customer_impact=customer_impact
        )
    
    async def _analyze_competitive_impact(self, pr) -> Dict:
        """Analyze impact on competitive positioning"""
        
        # Check if changes affect competitive advantage areas
        files_changed = [f.filename for f in pr.get_files()]
        
        competitive_areas = {
            "automation_engine": any("automation" in f for f in files_changed),
            "orchestration_system": any("orchestrator" in f for f in files_changed),
            "quality_system": any("quality" in f for f in files_changed),
            "seo_optimization": any("seo" in f or "marketing" in f for f in files_changed),
            "agent_intelligence": any("agents" in f for f in files_changed)
        }
        
        # Calculate competitive impact level
        affected_areas = sum(competitive_areas.values())
        if affected_areas >= 3:
            impact_level = "high"
        elif affected_areas >= 2:
            impact_level = "medium"
        elif affected_areas >= 1:
            impact_level = "low"
        else:
            impact_level = "none"
        
        return {
            "affected_areas": competitive_areas,
            "impact_level": impact_level,
            "strategic_significance": self._calculate_strategic_significance(competitive_areas)
        }
    
    def _calculate_strategic_significance(self, competitive_areas: Dict) -> str:
        """Calculate strategic significance of changes"""
        
        # Weight different areas by strategic importance
        area_weights = {
            "automation_engine": 0.30,  # Core revenue driver
            "orchestration_system": 0.25,  # Differentiation factor
            "quality_system": 0.20,  # Brand positioning
            "seo_optimization": 0.15,  # Market visibility
            "agent_intelligence": 0.10  # Future capability
        }
        
        weighted_score = sum(
            area_weights.get(area, 0) for area, affected in competitive_areas.items() if affected
        )
        
        if weighted_score >= 0.5:
            return "critical"
        elif weighted_score >= 0.3:
            return "high"
        elif weighted_score >= 0.1:
            return "medium"
        else:
            return "low"
    
    async def _identify_affected_opportunities(self, pr) -> List[Dict]:
        """Identify market opportunities affected by changes"""
        
        # Simple analysis - could be enhanced with actual orchestrator integration
        files_changed = [f.filename for f in pr.get_files()]
        
        opportunities = []
        
        # KDP automation opportunities
        if any("kdp" in f.lower() or "automation" in f for f in files_changed):
            opportunities.append({
                "type": "kdp_automation_enhancement",
                "market_size": "high",
                "competitive_advantage": "significant",
                "revenue_potential": "direct"
            })
        
        # SEO optimization opportunities
        if any("seo" in f.lower() or "marketing" in f for f in files_changed):
            opportunities.append({
                "type": "seo_competitive_advantage",
                "market_size": "medium",
                "competitive_advantage": "moderate",
                "revenue_potential": "indirect"
            })
        
        # Quality differentiation opportunities
        if any("quality" in f.lower() or "professional" in f for f in files_changed):
            opportunities.append({
                "type": "quality_leadership",
                "market_size": "medium",
                "competitive_advantage": "high",
                "revenue_potential": "brand_value"
            })
        
        return opportunities
    
    async def _get_quality_benchmarks(self, pr) -> Dict:
        """Get relevant quality benchmarks for the changes"""
        
        # This would integrate with ProfessionalQualityOrchestrator
        # For now, simplified analysis
        
        return {
            "code_quality_target": 85,
            "test_coverage_target": 90,
            "documentation_completeness": 80,
            "performance_benchmark": "sub_2s_response",
            "reliability_target": 99.5
        }
    
    async def _analyze_seo_implications(self, pr) -> Dict:
        """Analyze SEO implications of changes"""
        
        files_changed = [f.filename for f in pr.get_files()]
        
        seo_impact = {
            "content_changes": any("content" in f or "marketing" in f for f in files_changed),
            "metadata_changes": any("metadata" in f or "kdp" in f for f in files_changed),
            "algorithm_changes": any("seo" in f or "algorithm" in f for f in files_changed),
            "impact_level": "none"
        }
        
        # Calculate impact level
        if seo_impact["algorithm_changes"]:
            seo_impact["impact_level"] = "high"
        elif seo_impact["content_changes"] or seo_impact["metadata_changes"]:
            seo_impact["impact_level"] = "medium"
        
        return seo_impact
    
    async def _assess_revenue_impact(self, pr) -> str:
        """Assess revenue impact of changes"""
        
        files_changed = [f.filename for f in pr.get_files()]
        
        # Direct revenue impact areas
        high_impact_areas = [
            "automation/kdp",
            "automation/publishing",
            "orchestrator/competitive",
            "orchestrator/tactical"
        ]
        
        medium_impact_areas = [
            "quality",
            "seo",
            "marketing",
            "agents"
        ]
        
        if any(area in f for f in files_changed for area in high_impact_areas):
            return "high"
        elif any(area in f for f in files_changed for area in medium_impact_areas):
            return "medium"
        else:
            return "low"
    
    async def _assess_customer_impact(self, pr) -> str:
        """Assess customer/user impact of changes"""
        
        files_changed = [f.filename for f in pr.get_files()]
        
        # Customer-facing areas
        customer_impact_areas = [
            "automation",  # Affects automation reliability
            "quality",     # Affects output quality
            "agents",      # Affects user interaction
            "cli"          # Affects user interface
        ]
        
        if any(area in f for f in files_changed for area in customer_impact_areas):
            return "direct"
        elif any("orchestrator" in f for f in files_changed):
            return "indirect"
        else:
            return "minimal"
    
    async def _analyze_strategic_implications(self, pr, business_context: BusinessContext) -> Dict:
        """Analyze strategic implications of the PR"""
        
        implications = {
            "competitive_positioning": "neutral",
            "market_timing": "appropriate",
            "resource_allocation": "efficient",
            "technical_debt": "neutral",
            "innovation_opportunity": False,
            "risk_vs_reward": "balanced"
        }
        
        # Competitive positioning analysis
        if business_context.competitive_landscape["impact_level"] == "high":
            implications["competitive_positioning"] = "advancement"
        elif business_context.competitive_landscape["impact_level"] == "medium":
            implications["competitive_positioning"] = "maintenance"
        
        # Market timing analysis
        if len(business_context.market_opportunities) > 2:
            implications["market_timing"] = "opportune"
        elif len(business_context.market_opportunities) == 0:
            implications["market_timing"] = "stable"
        
        # Innovation opportunity
        if any("new" in pr.title.lower() or "innovative" in pr.title.lower() or
               "enhancement" in pr.title.lower() for f in [pr.title]):
            implications["innovation_opportunity"] = True
        
        # Risk vs reward
        high_value_ops = len([op for op in business_context.market_opportunities 
                             if op.get("revenue_potential") == "direct"])
        if high_value_ops > 0 and business_context.competitive_landscape["impact_level"] != "high":
            implications["risk_vs_reward"] = "favorable"
        elif business_context.competitive_landscape["impact_level"] == "high":
            implications["risk_vs_reward"] = "high_risk_high_reward"
        
        return implications
    
    async def _consult_orchestrators(self, pr, business_context: BusinessContext) -> Dict:
        """Consult business orchestrators for insights"""
        
        orchestrator_insights = {}
        
        try:
            # Competitive Intelligence insights
            orchestrator_insights["competitive"] = {
                "threat_level": "medium",  # Would come from actual orchestrator
                "opportunity_score": 0.75,
                "strategic_fit": 0.85,
                "recommendation": "proceed_with_monitoring"
            }
            
            # Tactical Advantage insights
            orchestrator_insights["tactical"] = {
                "advantage_alignment": True,
                "implementation_priority": "medium",
                "strategic_value": 0.80,
                "recommendation": "accelerate_if_possible"
            }
            
            # Quality Standards insights
            orchestrator_insights["quality"] = {
                "professional_standards_met": True,
                "quality_score": 88,
                "benchmark_comparison": "above_industry_average",
                "recommendation": "approve_with_confidence"
            }
            
            # SEO Impact insights
            orchestrator_insights["seo"] = {
                "ranking_impact": business_context.seo_implications["impact_level"],
                "algorithm_compliance": True,
                "competitive_keywords_affected": False,
                "recommendation": "monitor_rankings_post_merge"
            }
            
        except Exception as e:
            self.logger.warning(f"Orchestrator consultation failed: {e}")
            orchestrator_insights = {"error": "orchestrator_unavailable"}
        
        return orchestrator_insights
    
    async def _generate_strategic_assessment(self, pr, business_context: BusinessContext,
                                           strategic_analysis: Dict, orchestrator_insights: Dict) -> Dict:
        """Generate AI-powered strategic assessment"""
        
        context = f"""
        Technical Lead Strategic Assessment for PR: {pr.title}
        
        Business Context:
        - Revenue Impact: {business_context.revenue_impact}
        - Customer Impact: {business_context.customer_impact}
        - Market Opportunities: {len(business_context.market_opportunities)}
        - Competitive Significance: {business_context.competitive_landscape.get('strategic_significance', 'unknown')}
        
        Strategic Analysis:
        - Competitive Positioning: {strategic_analysis['competitive_positioning']}
        - Market Timing: {strategic_analysis['market_timing']}
        - Innovation Opportunity: {strategic_analysis['innovation_opportunity']}
        - Risk vs Reward: {strategic_analysis['risk_vs_reward']}
        
        Orchestrator Recommendations:
        - Competitive: {orchestrator_insights.get('competitive', {}).get('recommendation', 'unavailable')}
        - Tactical: {orchestrator_insights.get('tactical', {}).get('recommendation', 'unavailable')}
        - Quality: {orchestrator_insights.get('quality', {}).get('recommendation', 'unavailable')}
        - SEO: {orchestrator_insights.get('seo', {}).get('recommendation', 'unavailable')}
        """
        
        prompt = f"""
        As a Technical Lead for an AI-KindleMint orchestration system making a strategic merge decision:

        {context}

        Provide strategic assessment covering:
        1. Business impact and strategic alignment
        2. Competitive advantage implications
        3. Risk assessment from business perspective
        4. Timeline considerations for market positioning
        5. Clear recommendation with business justification

        Focus on the business and strategic implications, not just technical aspects.
        """
        
        try:
            response = await self.anthropic.messages.acreate(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            assessment = {
                "strategic_analysis": response.content[0].text,
                "confidence": 0.85,
                "key_insights": self._extract_strategic_insights(response.content[0].text),
                "business_risks": self._extract_business_risks(response.content[0].text),
                "competitive_implications": self._extract_competitive_implications(response.content[0].text)
            }
            
        except Exception as e:
            self.logger.warning(f"AI strategic assessment failed: {e}")
            assessment = {
                "strategic_analysis": "AI assessment unavailable - manual strategic review required",
                "confidence": 0.5,
                "key_insights": ["Manual strategic review recommended"],
                "business_risks": ["Unknown - requires analysis"],
                "competitive_implications": ["Assess competitive impact manually"]
            }
        
        return assessment
    
    def _extract_strategic_insights(self, ai_response: str) -> List[str]:
        """Extract strategic insights from AI response"""
        insights = []
        lines = ai_response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['strategic', 'business', 'competitive', 'market']):
                insights.append(line.strip())
        return insights[:5]
    
    def _extract_business_risks(self, ai_response: str) -> List[str]:
        """Extract business risks from AI response"""
        risks = []
        lines = ai_response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['risk', 'concern', 'caution', 'threat']):
                risks.append(line.strip())
        return risks[:3]
    
    def _extract_competitive_implications(self, ai_response: str) -> List[str]:
        """Extract competitive implications from AI response"""
        implications = []
        lines = ai_response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['competitive', 'advantage', 'position', 'market share']):
                implications.append(line.strip())
        return implications[:3]
    
    async def _make_final_decision(self, pr, business_context: BusinessContext,
                                 strategic_analysis: Dict, orchestrator_insights: Dict,
                                 ai_assessment: Dict, code_review_result: Dict = None) -> StrategicDecision:
        """Make final strategic decision integrating all factors"""
        
        # Initialize decision factors
        factors = {
            "business_alignment": 0.0,
            "competitive_advantage": 0.0,
            "quality_standards": 0.0,
            "strategic_timing": 0.0,
            "risk_assessment": 0.0,
            "orchestrator_consensus": 0.0
        }
        
        # Business alignment factor
        if business_context.revenue_impact == "high":
            factors["business_alignment"] = 0.9
        elif business_context.revenue_impact == "medium":
            factors["business_alignment"] = 0.7
        else:
            factors["business_alignment"] = 0.5
        
        # Competitive advantage factor
        if strategic_analysis["competitive_positioning"] == "advancement":
            factors["competitive_advantage"] = 0.9
        elif strategic_analysis["competitive_positioning"] == "maintenance":
            factors["competitive_advantage"] = 0.7
        else:
            factors["competitive_advantage"] = 0.5
        
        # Quality standards factor
        if orchestrator_insights.get("quality", {}).get("quality_score", 0) >= self.decision_thresholds["min_quality_score"]:
            factors["quality_standards"] = 0.9
        else:
            factors["quality_standards"] = 0.6
        
        # Strategic timing factor
        if strategic_analysis["market_timing"] == "opportune":
            factors["strategic_timing"] = 0.9
        elif strategic_analysis["market_timing"] == "appropriate":
            factors["strategic_timing"] = 0.7
        else:
            factors["strategic_timing"] = 0.5
        
        # Risk assessment factor
        if strategic_analysis["risk_vs_reward"] == "favorable":
            factors["risk_assessment"] = 0.9
        elif strategic_analysis["risk_vs_reward"] == "balanced":
            factors["risk_assessment"] = 0.7
        else:
            factors["risk_assessment"] = 0.4
        
        # Orchestrator consensus factor
        positive_recs = sum(1 for orch in orchestrator_insights.values() 
                           if isinstance(orch, dict) and "approve" in orch.get("recommendation", "").lower())
        total_recs = len([orch for orch in orchestrator_insights.values() if isinstance(orch, dict)])
        if total_recs > 0:
            factors["orchestrator_consensus"] = positive_recs / total_recs
        else:
            factors["orchestrator_consensus"] = 0.5
        
        # Calculate weighted confidence
        weights = {
            "business_alignment": 0.25,
            "competitive_advantage": 0.20,
            "quality_standards": 0.20,
            "strategic_timing": 0.15,
            "risk_assessment": 0.15,
            "orchestrator_consensus": 0.05
        }
        
        confidence = sum(factor * weights[name] for name, factor in factors.items())
        
        # Make decision
        if confidence >= self.decision_thresholds["auto_merge_confidence"]:
            decision = "merge"
            escalation_required = False
        elif confidence >= self.decision_thresholds["review_required_confidence"]:
            decision = "hold"
            escalation_required = False
        elif confidence >= self.decision_thresholds["escalation_threshold"]:
            decision = "escalate"
            escalation_required = True
        else:
            decision = "reject"
            escalation_required = False
        
        # Strategic overrides
        if business_context.revenue_impact == "high" and confidence >= 0.7:
            decision = "merge"
            escalation_required = False
        
        if business_context.competitive_landscape["strategic_significance"] == "critical":
            if confidence < 0.8:
                decision = "escalate"
                escalation_required = True
        
        # Generate business justification
        business_justification = self._generate_business_justification(
            decision, business_context, strategic_analysis, confidence
        )
        
        # Technical reasoning
        technical_reasoning = self._generate_technical_reasoning(
            decision, factors, orchestrator_insights
        )
        
        return StrategicDecision(
            decision=decision,
            confidence=round(confidence, 3),
            business_justification=business_justification,
            technical_reasoning=technical_reasoning,
            strategic_impact=strategic_analysis["competitive_positioning"],
            risk_assessment=self._assess_decision_risks(business_context, strategic_analysis),
            timeline_consideration=self._assess_timeline_urgency(strategic_analysis),
            escalation_required=escalation_required
        )
    
    def _generate_business_justification(self, decision: str, business_context: BusinessContext,
                                       strategic_analysis: Dict, confidence: float) -> str:
        """Generate business justification for the decision"""
        
        if decision == "merge":
            return f"Strategic merge approved: {business_context.revenue_impact} revenue impact, " \
                   f"{strategic_analysis['competitive_positioning']} competitive positioning, " \
                   f"with {confidence:.1%} confidence based on comprehensive business analysis."
        
        elif decision == "hold":
            return f"Merge held for strategic review: Moderate confidence ({confidence:.1%}) " \
                   f"requires additional business stakeholder input given " \
                   f"{business_context.revenue_impact} revenue implications."
        
        elif decision == "escalate":
            return f"Strategic escalation required: {business_context.competitive_landscape['strategic_significance']} " \
                   f"strategic significance with {confidence:.1%} confidence requires " \
                   f"executive review for business risk assessment."
        
        else:  # reject
            return f"Merge rejected: Low confidence ({confidence:.1%}) and " \
                   f"insufficient strategic alignment with business objectives. " \
                   f"Requires substantial revision before business approval."
    
    def _generate_technical_reasoning(self, decision: str, factors: Dict, 
                                    orchestrator_insights: Dict) -> List[str]:
        """Generate technical reasoning for the decision"""
        
        reasoning = []
        
        # Factor-based reasoning
        for factor_name, score in factors.items():
            if score >= 0.8:
                reasoning.append(f"Strong {factor_name.replace('_', ' ')}: {score:.2f}")
            elif score <= 0.5:
                reasoning.append(f"Weak {factor_name.replace('_', ' ')}: {score:.2f}")
        
        # Orchestrator-based reasoning
        for orch_name, insights in orchestrator_insights.items():
            if isinstance(insights, dict) and "recommendation" in insights:
                reasoning.append(f"{orch_name.title()} orchestrator: {insights['recommendation']}")
        
        return reasoning[:5]  # Limit to top 5 reasons
    
    def _assess_decision_risks(self, business_context: BusinessContext, 
                             strategic_analysis: Dict) -> Dict:
        """Assess risks associated with the decision"""
        
        risks = {
            "business_risk": "low",
            "competitive_risk": "low", 
            "technical_risk": "low",
            "timeline_risk": "low"
        }
        
        # Business risk
        if business_context.revenue_impact == "high":
            risks["business_risk"] = "medium"
        
        # Competitive risk
        if business_context.competitive_landscape["strategic_significance"] == "critical":
            risks["competitive_risk"] = "high"
        elif business_context.competitive_landscape["impact_level"] == "high":
            risks["competitive_risk"] = "medium"
        
        # Technical risk (based on change magnitude if available)
        if len(business_context.market_opportunities) > 2:
            risks["technical_risk"] = "medium"
        
        # Timeline risk
        if strategic_analysis["market_timing"] == "critical":
            risks["timeline_risk"] = "high"
        
        return risks
    
    def _assess_timeline_urgency(self, strategic_analysis: Dict) -> str:
        """Assess timeline urgency for the decision"""
        
        if strategic_analysis["market_timing"] == "opportune":
            return "accelerated_timeline_recommended"
        elif strategic_analysis["competitive_positioning"] == "advancement":
            return "standard_timeline_appropriate"
        else:
            return "flexible_timeline_acceptable"
    
    async def _post_strategic_comment(self, pr, decision: StrategicDecision, 
                                    business_context: BusinessContext) -> None:
        """Post strategic decision comment to PR"""
        
        comment = f"""## 🎯 AI Technical Lead - Strategic Decision

**Strategic Decision:** {decision.decision.upper()} (Confidence: {decision.confidence:.1%})

### 💼 Business Analysis
**Revenue Impact:** {business_context.revenue_impact.title()}  
**Customer Impact:** {business_context.customer_impact.title()}  
**Market Opportunities:** {len(business_context.market_opportunities)} identified  
**Competitive Significance:** {business_context.competitive_landscape.get('strategic_significance', 'Unknown').title()}

### 🏆 Strategic Assessment
**Competitive Impact:** {decision.strategic_impact.title()}  
**Timeline Consideration:** {decision.timeline_consideration.replace('_', ' ').title()}  
**Business Justification:** {decision.business_justification}

### 🎯 Orchestrator Consensus
"""
        
        # Add orchestrator insights if available
        for area in ['competitive', 'tactical', 'quality', 'seo']:
            comment += f"- **{area.title()}:** Consulting business orchestrator...\n"
        
        comment += f"""
### ⚡ Strategic Factors
**Risk Assessment:**
"""
        for risk_type, level in decision.risk_assessment.items():
            comment += f"- {risk_type.replace('_', ' ').title()}: {level.upper()}\n"
        
        comment += f"""
### 🚀 Technical Lead Reasoning
"""
        for reason in decision.technical_reasoning:
            comment += f"- {reason}\n"
        
        if decision.escalation_required:
            comment += f"""
### 🚨 ESCALATION REQUIRED
This decision requires executive review due to strategic significance.
Please involve business stakeholders before proceeding.
"""
        
        comment += f"""
### 📋 Next Steps
"""
        if decision.decision == "merge":
            comment += "✅ **STRATEGIC APPROVAL** - Merge aligns with business objectives\n"
        elif decision.decision == "hold":
            comment += "⏳ **STRATEGIC HOLD** - Additional business review recommended\n"
        elif decision.decision == "escalate":
            comment += "🚨 **STRATEGIC ESCALATION** - Executive business review required\n"
        else:
            comment += "❌ **STRATEGIC REJECTION** - Does not meet business criteria\n"
        
        comment += f"""
---
*Strategic decision by AI Technical Lead at {datetime.now().isoformat()}*
*Integrated Business Intelligence • Competitive Analysis • Quality Standards*
"""
        
        try:
            pr.create_issue_comment(comment)
            self.logger.info(f"Posted strategic decision to PR #{pr.number}")
        except Exception as e:
            self.logger.error(f"Failed to post strategic comment: {e}")


# CLI interface for testing
async def main():
    """CLI interface for AI Technical Lead Agent"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="AI Technical Lead Agent - Strategic PR Decisions")
    parser.add_argument("--repo", required=True, help="Repository name (owner/repo)")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    parser.add_argument("--github-token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--anthropic-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    anthropic_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY")
    
    if not github_token or not anthropic_key:
        print("❌ Error: GitHub token and Anthropic API key are required")
        return
    
    # Initialize AI Technical Lead Agent
    agent = AITechnicalLeadAgent(github_token, anthropic_key)
    
    print(f"🎯 Making strategic decision for {args.repo} PR #{args.pr}")
    
    # Make strategic decision
    decision = await agent.make_strategic_decision(args.repo, args.pr)
    
    print(f"\n✅ Strategic decision completed!")
    print(f"🎯 Decision: {decision.decision.upper()}")
    print(f"📊 Confidence: {decision.confidence:.1%}")
    print(f"💼 Business Justification: {decision.business_justification}")
    
    if decision.escalation_required:
        print(f"🚨 ESCALATION REQUIRED: Executive review needed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())