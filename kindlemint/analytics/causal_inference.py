"""
Alembic Causal Analytics Engine for KindleMint

This module implements causal inference models inspired by NVIDIA's approach to AI,
focusing on understanding the causal relationships between marketing actions and book sales.
The Alembic strategy involves distilling complex causal relationships into actionable insights.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class CausalRelationship:
    """Represents a causal relationship between variables"""
    cause: str
    effect: str
    strength: float
    confidence: float
    lag_time: Optional[timedelta] = None
    mechanism: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class InterventionResult:
    """Results from a causal intervention"""
    intervention: str
    target: str
    predicted_effect: float
    confidence_interval: Tuple[float, float]
    recommendation: str
    expected_roi: float


class CausalAnalyticsEngine:
    """
    Main engine for causal analytics in KindleMint publishing strategy.
    
    Implements the Alembic approach: distilling complex market dynamics into
    clear causal relationships that drive publishing decisions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the causal analytics engine"""
        self.config = config or self._default_config()
        self.causal_graph = nx.DiGraph()
        self.intervention_history = []
        self.model_cache = {}
        self._initialize_causal_structure()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the engine"""
        return {
            "min_sample_size": 100,
            "confidence_threshold": 0.95,
            "max_lag_days": 30,
            "parallel_workers": 4,
            "cache_ttl_hours": 24,
            "intervention_cooldown_hours": 48,
            "causal_discovery_methods": ["pc", "ges", "lingam"],
            "effect_size_threshold": 0.1
        }
    
    def _initialize_causal_structure(self):
        """Initialize the base causal structure for book publishing"""
        # Core causal relationships in book publishing
        base_relationships = [
            ("cover_quality", "click_through_rate", 0.7),
            ("price_point", "conversion_rate", -0.5),
            ("keywords_relevance", "search_visibility", 0.8),
            ("search_visibility", "impressions", 0.9),
            ("impressions", "clicks", 0.3),
            ("clicks", "conversions", 0.15),
            ("review_score", "conversion_rate", 0.6),
            ("review_count", "trust_signal", 0.7),
            ("trust_signal", "conversion_rate", 0.4),
            ("seasonal_trend", "demand", 0.5),
            ("marketing_spend", "impressions", 0.6),
            ("content_quality", "review_score", 0.8),
            ("series_momentum", "repeat_purchases", 0.7),
            ("email_campaign", "direct_traffic", 0.4),
            ("social_proof", "conversion_rate", 0.3)
        ]
        
        for cause, effect, strength in base_relationships:
            self.causal_graph.add_edge(cause, effect, weight=strength)
    
    def discover_causal_relationships(self, 
                                    data: pd.DataFrame,
                                    target_variable: str,
                                    method: str = "ensemble") -> List[CausalRelationship]:
        """
        Discover causal relationships from observational data
        
        Args:
            data: DataFrame with time series data
            target_variable: The outcome variable to analyze
            method: Discovery method to use
            
        Returns:
            List of discovered causal relationships
        """
        logger.info(f"Discovering causal relationships for {target_variable}")
        
        relationships = []
        
        # Ensemble approach combining multiple methods
        if method == "ensemble":
            methods_results = []
            with ThreadPoolExecutor(max_workers=self.config["parallel_workers"]) as executor:
                futures = []
                for method_name in self.config["causal_discovery_methods"]:
                    future = executor.submit(
                        self._run_causal_discovery_method,
                        data, target_variable, method_name
                    )
                    futures.append(future)
                
                for future in futures:
                    try:
                        result = future.result(timeout=60)
                        methods_results.append(result)
                    except Exception as e:
                        logger.error(f"Causal discovery failed: {e}")
            
            # Aggregate results from multiple methods
            relationships = self._aggregate_causal_discoveries(methods_results)
        else:
            relationships = self._run_causal_discovery_method(data, target_variable, method)
        
        # Update causal graph
        self._update_causal_graph(relationships)
        
        return relationships
    
    def _run_causal_discovery_method(self, 
                                   data: pd.DataFrame,
                                   target: str,
                                   method: str) -> List[CausalRelationship]:
        """Run a specific causal discovery method"""
        relationships = []
        
        if method == "pc":
            # Peter-Clark algorithm simulation
            relationships.extend(self._pc_algorithm(data, target))
        elif method == "ges":
            # Greedy Equivalence Search simulation
            relationships.extend(self._ges_algorithm(data, target))
        elif method == "lingam":
            # Linear Non-Gaussian Acyclic Model simulation
            relationships.extend(self._lingam_algorithm(data, target))
        
        return relationships
    
    def _pc_algorithm(self, data: pd.DataFrame, target: str) -> List[CausalRelationship]:
        """Simplified PC algorithm for causal discovery"""
        relationships = []
        
        # Compute conditional independence tests
        for col in data.columns:
            if col != target:
                # Partial correlation as proxy for conditional independence
                corr, p_value = stats.pearsonr(data[col], data[target])
                
                if p_value < 0.05 and abs(corr) > self.config["effect_size_threshold"]:
                    # Test for direct causation using temporal precedence
                    lag_corr = self._compute_lagged_correlation(data, col, target)
                    
                    if lag_corr["max_correlation"] > abs(corr):
                        relationships.append(CausalRelationship(
                            cause=col,
                            effect=target,
                            strength=lag_corr["max_correlation"],
                            confidence=1 - p_value,
                            lag_time=timedelta(days=lag_corr["optimal_lag"]),
                            mechanism="temporal_precedence"
                        ))
        
        return relationships
    
    def _ges_algorithm(self, data: pd.DataFrame, target: str) -> List[CausalRelationship]:
        """Simplified GES algorithm for causal discovery"""
        relationships = []
        
        # Build initial graph using correlation strength
        correlation_matrix = data.corr()
        
        for col in data.columns:
            if col != target:
                corr_value = correlation_matrix.loc[col, target]
                
                if abs(corr_value) > self.config["effect_size_threshold"]:
                    # Use information gain to determine direction
                    info_gain = self._compute_information_gain(data, col, target)
                    
                    if info_gain > 0:
                        relationships.append(CausalRelationship(
                            cause=col,
                            effect=target,
                            strength=abs(corr_value),
                            confidence=min(0.99, info_gain),
                            mechanism="information_flow"
                        ))
        
        return relationships
    
    def _lingam_algorithm(self, data: pd.DataFrame, target: str) -> List[CausalRelationship]:
        """Simplified LiNGAM algorithm for causal discovery"""
        relationships = []
        
        # Use independent component analysis approach
        for col in data.columns:
            if col != target:
                # Test for non-Gaussian noise
                _, normality_p = stats.normaltest(data[col])
                
                if normality_p < 0.05:  # Non-Gaussian
                    # Compute mutual information
                    mi_score = self._compute_mutual_information(data[col], data[target])
                    
                    if mi_score > 0.1:
                        relationships.append(CausalRelationship(
                            cause=col,
                            effect=target,
                            strength=mi_score,
                            confidence=0.8,
                            mechanism="non_gaussian_causation"
                        ))
        
        return relationships
    
    def _compute_lagged_correlation(self, 
                                  data: pd.DataFrame,
                                  cause: str,
                                  effect: str) -> Dict[str, Any]:
        """Compute correlation at different time lags"""
        max_corr = 0
        optimal_lag = 0
        
        for lag in range(1, min(self.config["max_lag_days"], len(data) // 4)):
            if lag < len(data):
                lagged_cause = data[cause].shift(lag)
                valid_idx = ~lagged_cause.isna()
                
                if valid_idx.sum() > self.config["min_sample_size"]:
                    corr, _ = stats.pearsonr(
                        lagged_cause[valid_idx],
                        data[effect][valid_idx]
                    )
                    
                    if abs(corr) > abs(max_corr):
                        max_corr = corr
                        optimal_lag = lag
        
        return {
            "max_correlation": max_corr,
            "optimal_lag": optimal_lag
        }
    
    def _compute_information_gain(self, 
                                data: pd.DataFrame,
                                feature: str,
                                target: str) -> float:
        """Compute information gain between feature and target"""
        # Discretize continuous variables
        feature_bins = pd.qcut(data[feature], q=5, duplicates='drop')
        target_bins = pd.qcut(data[target], q=5, duplicates='drop')
        
        # Compute mutual information
        contingency = pd.crosstab(feature_bins, target_bins)
        chi2, _, _, _ = stats.chi2_contingency(contingency)
        
        n = contingency.sum().sum()
        return chi2 / (2 * n)
    
    def _compute_mutual_information(self, x: pd.Series, y: pd.Series) -> float:
        """Compute mutual information between two variables"""
        # Simple binning approach
        x_bins = pd.qcut(x, q=10, duplicates='drop')
        y_bins = pd.qcut(y, q=10, duplicates='drop')
        
        # Joint and marginal probabilities
        joint_prob = pd.crosstab(x_bins, y_bins, normalize=True)
        x_prob = joint_prob.sum(axis=1)
        y_prob = joint_prob.sum(axis=0)
        
        # Mutual information
        mi = 0
        for i in range(len(x_prob)):
            for j in range(len(y_prob)):
                if joint_prob.iloc[i, j] > 0:
                    mi += joint_prob.iloc[i, j] * np.log(
                        joint_prob.iloc[i, j] / (x_prob.iloc[i] * y_prob.iloc[j])
                    )
        
        return mi
    
    def _aggregate_causal_discoveries(self, 
                                    results: List[List[CausalRelationship]]) -> List[CausalRelationship]:
        """Aggregate results from multiple causal discovery methods"""
        # Count occurrences of each relationship
        relationship_counts = defaultdict(list)
        
        for method_results in results:
            for rel in method_results:
                key = (rel.cause, rel.effect)
                relationship_counts[key].append(rel)
        
        # Aggregate relationships that appear in multiple methods
        aggregated = []
        for (cause, effect), rels in relationship_counts.items():
            if len(rels) >= 2:  # Relationship found by at least 2 methods
                avg_strength = np.mean([r.strength for r in rels])
                avg_confidence = np.mean([r.confidence for r in rels])
                
                aggregated.append(CausalRelationship(
                    cause=cause,
                    effect=effect,
                    strength=avg_strength,
                    confidence=avg_confidence,
                    mechanism="ensemble_consensus",
                    metadata={
                        "methods_count": len(rels),
                        "methods": [r.mechanism for r in rels]
                    }
                ))
        
        return aggregated
    
    def _update_causal_graph(self, relationships: List[CausalRelationship]):
        """Update the causal graph with new relationships"""
        for rel in relationships:
            if self.causal_graph.has_edge(rel.cause, rel.effect):
                # Update existing edge
                current_weight = self.causal_graph[rel.cause][rel.effect]["weight"]
                new_weight = (current_weight + rel.strength) / 2
                self.causal_graph[rel.cause][rel.effect]["weight"] = new_weight
            else:
                # Add new edge
                self.causal_graph.add_edge(
                    rel.cause, 
                    rel.effect,
                    weight=rel.strength,
                    confidence=rel.confidence
                )
    
    def estimate_intervention_effect(self,
                                   intervention: str,
                                   target: str,
                                   intervention_value: float,
                                   data: Optional[pd.DataFrame] = None) -> InterventionResult:
        """
        Estimate the causal effect of an intervention
        
        Args:
            intervention: Variable to intervene on
            target: Target outcome variable
            intervention_value: Value to set for intervention
            data: Historical data for estimation
            
        Returns:
            InterventionResult with predicted effects
        """
        logger.info(f"Estimating effect of {intervention} -> {target}")
        
        # Check cache
        cache_key = self._get_cache_key(intervention, target, intervention_value)
        if cache_key in self.model_cache:
            cached_result, timestamp = self.model_cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=self.config["cache_ttl_hours"]):
                logger.info("Returning cached intervention result")
                return cached_result
        
        # Find causal paths
        paths = list(nx.all_simple_paths(self.causal_graph, intervention, target))
        
        if not paths:
            return InterventionResult(
                intervention=intervention,
                target=target,
                predicted_effect=0,
                confidence_interval=(0, 0),
                recommendation="No causal path found",
                expected_roi=0
            )
        
        # Estimate effect through each path
        path_effects = []
        for path in paths:
            effect = intervention_value
            for i in range(len(path) - 1):
                edge_weight = self.causal_graph[path[i]][path[i+1]].get("weight", 0)
                effect *= edge_weight
            path_effects.append(effect)
        
        # Aggregate effects
        total_effect = sum(path_effects)
        
        # Estimate confidence interval
        if data is not None and len(data) > self.config["min_sample_size"]:
            ci_lower, ci_upper = self._bootstrap_confidence_interval(
                data, intervention, target, intervention_value
            )
        else:
            # Heuristic confidence interval
            std_dev = abs(total_effect) * 0.2
            ci_lower = total_effect - 1.96 * std_dev
            ci_upper = total_effect + 1.96 * std_dev
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            intervention, target, total_effect, ci_lower, ci_upper
        )
        
        # Estimate ROI
        expected_roi = self._estimate_roi(intervention, intervention_value, total_effect)
        
        result = InterventionResult(
            intervention=intervention,
            target=target,
            predicted_effect=total_effect,
            confidence_interval=(ci_lower, ci_upper),
            recommendation=recommendation,
            expected_roi=expected_roi
        )
        
        # Cache result
        self.model_cache[cache_key] = (result, datetime.now())
        
        # Record intervention
        self.intervention_history.append({
            "timestamp": datetime.now(),
            "intervention": intervention,
            "target": target,
            "value": intervention_value,
            "predicted_effect": total_effect
        })
        
        return result
    
    def _get_cache_key(self, intervention: str, target: str, value: float) -> str:
        """Generate cache key for intervention results"""
        key_string = f"{intervention}_{target}_{value}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _bootstrap_confidence_interval(self,
                                     data: pd.DataFrame,
                                     intervention: str,
                                     target: str,
                                     intervention_value: float,
                                     n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Estimate confidence interval using bootstrap"""
        effects = []
        
        for _ in range(n_bootstrap):
            # Resample data
            sample = data.sample(n=len(data), replace=True)
            
            # Fit simple model
            if intervention in sample.columns and target in sample.columns:
                X = sample[[intervention]]
                y = sample[target]
                
                model = RandomForestRegressor(n_estimators=10, random_state=42)
                model.fit(X, y)
                
                # Predict effect
                effect = model.predict([[intervention_value]])[0]
                effects.append(effect)
        
        if effects:
            return np.percentile(effects, 2.5), np.percentile(effects, 97.5)
        else:
            return 0, 0
    
    def _generate_recommendation(self,
                               intervention: str,
                               target: str,
                               effect: float,
                               ci_lower: float,
                               ci_upper: float) -> str:
        """Generate actionable recommendation based on causal analysis"""
        
        # Check if effect is significant
        if ci_lower > 0 and ci_upper > 0:
            direction = "positive"
            confidence = "high" if (ci_upper - ci_lower) / abs(effect) < 0.5 else "moderate"
        elif ci_lower < 0 and ci_upper < 0:
            direction = "negative"
            confidence = "high" if (ci_upper - ci_lower) / abs(effect) < 0.5 else "moderate"
        else:
            direction = "uncertain"
            confidence = "low"
        
        # Generate specific recommendations
        recommendations = {
            ("cover_quality", "conversions", "positive"): 
                f"Invest in professional cover design. Expected {effect:.1%} increase in conversions.",
            ("price_point", "conversions", "negative"):
                f"Consider price reduction. Current price may be reducing conversions by {abs(effect):.1%}.",
            ("keywords_relevance", "impressions", "positive"):
                f"Optimize keywords further. Can increase impressions by {effect:.1%}.",
            ("marketing_spend", "impressions", "positive"):
                f"Increase marketing budget. Each $1 spent expected to generate {effect:.0f} impressions.",
            ("review_score", "conversions", "positive"):
                f"Focus on review generation. Higher ratings can boost conversions by {effect:.1%}."
        }
        
        key = (intervention, target, direction)
        if key in recommendations:
            return recommendations[key]
        else:
            if direction == "positive":
                return f"Increasing {intervention} will likely improve {target} by {effect:.1%} ({confidence} confidence)"
            elif direction == "negative":
                return f"Reducing {intervention} may improve {target} by {abs(effect):.1%} ({confidence} confidence)"
            else:
                return f"Effect of {intervention} on {target} is uncertain. Consider A/B testing."
    
    def _estimate_roi(self, intervention: str, cost: float, effect: float) -> float:
        """Estimate return on investment for an intervention"""
        # Define value multipliers for different outcomes
        outcome_values = {
            "conversions": 15.0,  # Average book profit
            "impressions": 0.001,  # Value per impression
            "clicks": 0.01,  # Value per click
            "review_score": 50.0,  # Long-term value of rating improvement
            "repeat_purchases": 30.0  # Value of customer retention
        }
        
        # Find all affected outcomes
        affected_outcomes = nx.descendants(self.causal_graph, intervention)
        
        total_value = 0
        for outcome in affected_outcomes:
            if outcome in outcome_values:
                # Trace effect to this outcome
                paths = list(nx.all_simple_paths(self.causal_graph, intervention, outcome))
                outcome_effect = 0
                
                for path in paths:
                    path_effect = effect
                    for i in range(1, len(path) - 1):
                        edge_weight = self.causal_graph[path[i]][path[i+1]].get("weight", 0)
                        path_effect *= edge_weight
                    outcome_effect += path_effect
                
                total_value += outcome_effect * outcome_values[outcome]
        
        # Calculate ROI
        if cost > 0:
            roi = (total_value - cost) / cost
        else:
            roi = float('inf') if total_value > 0 else 0
        
        return roi
    
    def identify_confounders(self,
                           cause: str,
                           effect: str,
                           data: pd.DataFrame) -> List[str]:
        """Identify potential confounding variables"""
        confounders = []
        
        # Find common causes (confounders)
        cause_parents = list(self.causal_graph.predecessors(cause))
        effect_parents = list(self.causal_graph.predecessors(effect))
        
        common_parents = set(cause_parents) & set(effect_parents)
        confounders.extend(common_parents)
        
        # Statistical test for confounding
        for variable in data.columns:
            if variable not in [cause, effect] and variable not in confounders:
                # Check if variable is associated with both cause and effect
                cause_corr, cause_p = stats.pearsonr(data[variable], data[cause])
                effect_corr, effect_p = stats.pearsonr(data[variable], data[effect])
                
                if cause_p < 0.05 and effect_p < 0.05:
                    if abs(cause_corr) > 0.3 and abs(effect_corr) > 0.3:
                        confounders.append(variable)
        
        return list(set(confounders))
    
    def run_counterfactual_analysis(self,
                                  scenario: Dict[str, float],
                                  outcomes: List[str],
                                  data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run counterfactual analysis for "what-if" scenarios
        
        Args:
            scenario: Dictionary of interventions to apply
            outcomes: List of outcome variables to track
            data: Historical data for baseline
            
        Returns:
            Dictionary with counterfactual predictions
        """
        logger.info(f"Running counterfactual analysis for scenario: {scenario}")
        
        results = {
            "scenario": scenario,
            "baseline": {},
            "counterfactual": {},
            "changes": {},
            "confidence": {}
        }
        
        # Compute baseline values
        for outcome in outcomes:
            if outcome in data.columns:
                results["baseline"][outcome] = data[outcome].mean()
        
        # Estimate counterfactual outcomes
        for outcome in outcomes:
            total_effect = 0
            confidence_intervals = []
            
            for intervention, value in scenario.items():
                # Find all paths from intervention to outcome
                if nx.has_path(self.causal_graph, intervention, outcome):
                    intervention_result = self.estimate_intervention_effect(
                        intervention, outcome, value, data
                    )
                    total_effect += intervention_result.predicted_effect
                    confidence_intervals.append(intervention_result.confidence_interval)
            
            # Aggregate effects
            baseline = results["baseline"].get(outcome, 0)
            counterfactual = baseline + total_effect
            
            results["counterfactual"][outcome] = counterfactual
            results["changes"][outcome] = total_effect
            
            # Aggregate confidence
            if confidence_intervals:
                ci_lower = sum(ci[0] for ci in confidence_intervals)
                ci_upper = sum(ci[1] for ci in confidence_intervals)
                results["confidence"][outcome] = (ci_lower, ci_upper)
        
        return results
    
    def optimize_interventions(self,
                             budget: float,
                             target_outcome: str,
                             constraints: Optional[Dict[str, Tuple[float, float]]] = None) -> Dict[str, Any]:
        """
        Optimize interventions to maximize target outcome within budget
        
        Args:
            budget: Total budget available
            target_outcome: Outcome to maximize
            constraints: Min/max constraints for each intervention
            
        Returns:
            Optimal intervention plan
        """
        logger.info(f"Optimizing interventions for {target_outcome} with budget ${budget}")
        
        # Get all possible interventions
        interventions = [node for node in self.causal_graph.nodes() 
                        if self.causal_graph.out_degree(node) > 0]
        
        # Filter to those affecting target
        relevant_interventions = []
        for intervention in interventions:
            if nx.has_path(self.causal_graph, intervention, target_outcome):
                relevant_interventions.append(intervention)
        
        # Define intervention costs (simplified)
        intervention_costs = {
            "marketing_spend": 1.0,
            "price_point": 0.0,  # No cost to change price
            "cover_quality": 500.0,  # One-time cost
            "keywords_relevance": 100.0,  # SEO optimization
            "email_campaign": 200.0,  # Campaign cost
            "content_quality": 1000.0  # Editorial improvement
        }
        
        # Greedy optimization
        remaining_budget = budget
        optimal_plan = {}
        expected_effect = 0
        
        while remaining_budget > 0 and relevant_interventions:
            best_intervention = None
            best_roi = -float('inf')
            best_value = 0
            
            for intervention in relevant_interventions:
                cost = intervention_costs.get(intervention, 100)
                
                if cost <= remaining_budget:
                    # Try different intervention values
                    test_values = [0.1, 0.5, 1.0, 2.0] if constraints is None else [
                        constraints.get(intervention, (0, 1))[1]
                    ]
                    
                    for value in test_values:
                        if constraints and intervention in constraints:
                            min_val, max_val = constraints[intervention]
                            if value < min_val or value > max_val:
                                continue
                        
                        # Estimate effect
                        result = self.estimate_intervention_effect(
                            intervention, target_outcome, value
                        )
                        
                        roi = result.expected_roi
                        
                        if roi > best_roi:
                            best_roi = roi
                            best_intervention = intervention
                            best_value = value
            
            if best_intervention:
                # Add to plan
                optimal_plan[best_intervention] = best_value
                cost = intervention_costs.get(best_intervention, 100)
                remaining_budget -= cost
                relevant_interventions.remove(best_intervention)
                
                # Update expected effect
                result = self.estimate_intervention_effect(
                    best_intervention, target_outcome, best_value
                )
                expected_effect += result.predicted_effect
            else:
                break
        
        return {
            "optimal_plan": optimal_plan,
            "total_cost": budget - remaining_budget,
            "expected_effect": expected_effect,
            "expected_outcome_increase": f"{expected_effect:.1%}",
            "interventions": [
                {
                    "action": k,
                    "value": v,
                    "cost": intervention_costs.get(k, 100)
                }
                for k, v in optimal_plan.items()
            ]
        }
    
    def analyze_series_momentum(self,
                              series_data: pd.DataFrame,
                              book_id: str) -> Dict[str, Any]:
        """
        Analyze causal factors driving series momentum
        
        Args:
            series_data: DataFrame with series performance data
            book_id: Identifier for the book/series
            
        Returns:
            Analysis of series momentum factors
        """
        logger.info(f"Analyzing series momentum for {book_id}")
        
        # Key metrics for series momentum
        momentum_factors = [
            "reader_retention",
            "cross_sell_rate",
            "review_velocity",
            "pre_order_rate",
            "social_mentions",
            "readthrough_rate"
        ]
        
        analysis = {
            "book_id": book_id,
            "momentum_score": 0,
            "growth_trajectory": "stable",
            "key_drivers": [],
            "recommendations": []
        }
        
        # Calculate momentum score
        if all(factor in series_data.columns for factor in momentum_factors):
            # Discover causal relationships
            relationships = self.discover_causal_relationships(
                series_data, "sales_velocity", "ensemble"
            )
            
            # Identify strongest drivers
            strong_drivers = [
                rel for rel in relationships 
                if rel.strength > 0.5 and rel.confidence > 0.8
            ]
            
            analysis["key_drivers"] = [
                {
                    "factor": rel.cause,
                    "impact": rel.strength,
                    "confidence": rel.confidence
                }
                for rel in strong_drivers[:3]
            ]
            
            # Calculate momentum score
            momentum_score = np.mean([
                series_data[factor].iloc[-1] / series_data[factor].mean()
                for factor in momentum_factors
                if factor in series_data.columns
            ])
            analysis["momentum_score"] = momentum_score
            
            # Determine trajectory
            if momentum_score > 1.2:
                analysis["growth_trajectory"] = "accelerating"
            elif momentum_score < 0.8:
                analysis["growth_trajectory"] = "declining"
            
            # Generate recommendations
            for driver in analysis["key_drivers"]:
                if driver["factor"] == "reader_retention":
                    analysis["recommendations"].append(
                        "Focus on cliffhangers and series arc to improve retention"
                    )
                elif driver["factor"] == "review_velocity":
                    analysis["recommendations"].append(
                        "Implement review request automation in book backmatter"
                    )
                elif driver["factor"] == "readthrough_rate":
                    analysis["recommendations"].append(
                        "Optimize book endings to drive next book purchases"
                    )
        
        return analysis
    
    def export_causal_model(self) -> Dict[str, Any]:
        """Export the causal model for persistence"""
        return {
            "graph": nx.node_link_data(self.causal_graph),
            "intervention_history": self.intervention_history,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def import_causal_model(self, model_data: Dict[str, Any]):
        """Import a previously exported causal model"""
        self.causal_graph = nx.node_link_graph(model_data["graph"])
        self.intervention_history = model_data.get("intervention_history", [])
        self.config.update(model_data.get("config", {}))
        logger.info(f"Imported causal model from {model_data.get('timestamp', 'unknown')}")