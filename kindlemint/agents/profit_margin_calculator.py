#!/usr/bin/env python3
"""
ProfitMarginCalculator - Calculate true net profit for every book and series
Uses data from CostTracker and SalesDataIngestion to provide accurate profitability analysis
"""
import os
import json
import boto3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP

# Import our other agents
try:
    from .cost_tracker import CostTracker, BookProductionCost
    from .sales_data_ingestion import SalesDataIngestion, KDPSalesRecord
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("⚠️ Cost and Sales agents not available")

# Sentry integration
try:
    from ..utils.sentry_config import capture_business_event, SentryPerformanceTracker
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

@dataclass
class BookProfitAnalysis:
    """Complete profit analysis for a single book."""
    book_id: str
    asin: str
    title: str
    series_name: str
    volume_number: int
    analysis_date: str
    
    # Production costs
    total_production_cost: Decimal
    api_costs: Decimal
    aws_costs: Decimal
    cost_per_unit: Decimal
    
    # Sales data
    units_sold: int
    units_refunded: int
    net_units_sold: int
    gross_revenue: Decimal
    royalty_earned: Decimal
    average_royalty_rate: float
    
    # Profit calculations
    net_profit: Decimal
    profit_margin_percent: float
    roi_percent: float
    break_even_units: int
    
    # Performance metrics
    days_since_publication: int
    daily_average_sales: float
    monthly_projected_revenue: Decimal
    monthly_projected_profit: Decimal
    
    # Market position
    estimated_market_share: float
    competitive_position: str

@dataclass
class SeriesProfitAnalysis:
    """Complete profit analysis for an entire series."""
    series_name: str
    analysis_date: str
    
    # Series overview
    total_volumes: int
    published_volumes: int
    volumes_with_sales: int
    
    # Aggregated costs
    total_production_costs: Decimal
    average_cost_per_volume: Decimal
    total_api_costs: Decimal
    total_aws_costs: Decimal
    
    # Aggregated sales
    total_units_sold: int
    total_net_units_sold: int
    total_gross_revenue: Decimal
    total_royalty_earned: Decimal
    average_royalty_rate: float
    
    # Series profitability
    total_net_profit: Decimal
    series_profit_margin_percent: float
    series_roi_percent: float
    
    # Performance trends
    monthly_growth_rate: float
    best_performing_volume: Dict[str, Any]
    worst_performing_volume: Dict[str, Any]
    
    # Projections
    projected_annual_revenue: Decimal
    projected_annual_profit: Decimal
    break_even_timeline_months: int
    
    # Individual book analyses
    book_analyses: List[BookProfitAnalysis]

class ProfitMarginCalculator:
    """Calculates precise profit margins using cost and sales data."""
    
    def __init__(self):
        self.analysis_dir = Path("output/profit_analysis")
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize our data sources
        if AGENTS_AVAILABLE:
            self.cost_tracker = CostTracker()
            self.sales_ingestion = SalesDataIngestion()
        else:
            print("⚠️ Agent dependencies not available")
            
        # DynamoDB connection
        self.dynamodb = boto3.resource('dynamodb')
        
        # Market data for competitive analysis
        self.market_data = {
            'large_print_crosswords': {
                'estimated_monthly_searches': 12000,
                'average_competing_books': 150,
                'average_price': 7.99,
                'top_performer_units_monthly': 500
            }
        }
    
    def analyze_book_profit(self, book_id: str, asin: str = None) -> Optional[BookProfitAnalysis]:
        """Analyze profit for a single book."""
        try:
            print(f"📊 Analyzing profit for book: {book_id}")
            
            # Get cost data
            cost_data = self._load_book_cost_data(book_id)
            if not cost_data:
                print(f"⚠️ No cost data found for {book_id}")
                return None
            
            # Get sales data
            sales_data = self._load_book_sales_data(book_id, asin)
            if not sales_data:
                print(f"⚠️ No sales data found for {book_id}")
                # Create analysis with cost data only
                return self._create_cost_only_analysis(book_id, cost_data)
            
            # Calculate profit metrics
            analysis = self._calculate_book_profit(book_id, cost_data, sales_data)
            
            # Save analysis
            self._save_book_analysis(analysis)
            
            if SENTRY_AVAILABLE:
                capture_business_event("book_profit_analyzed",
                                     f"Book {book_id}: ${analysis.net_profit:.2f} profit ({analysis.profit_margin_percent:.1f}%)",
                                     extra_data={
                                         "book_id": book_id,
                                         "net_profit": float(analysis.net_profit),
                                         "profit_margin": analysis.profit_margin_percent
                                     })
            
            return analysis
            
        except Exception as e:
            print(f"❌ Book profit analysis failed for {book_id}: {e}")
            return None
    
    def analyze_series_profit(self, series_name: str) -> Optional[SeriesProfitAnalysis]:
        """Analyze profit for an entire series."""
        try:
            print(f"📈 Analyzing series profit: {series_name}")
            
            with SentryPerformanceTracker("series_profit_analysis") if SENTRY_AVAILABLE else None:
                # Get all books in series
                book_analyses = self._get_series_book_analyses(series_name)
                
                if not book_analyses:
                    print(f"⚠️ No book data found for series: {series_name}")
                    return None
                
                # Calculate series metrics
                analysis = self._calculate_series_profit(series_name, book_analyses)
                
                # Save analysis
                self._save_series_analysis(analysis)
                
                if SENTRY_AVAILABLE:
                    capture_business_event("series_profit_analyzed",
                                         f"Series {series_name}: ${analysis.total_net_profit:.2f} profit ({analysis.series_profit_margin_percent:.1f}%)",
                                         extra_data={
                                             "series_name": series_name,
                                             "total_profit": float(analysis.total_net_profit),
                                             "profit_margin": analysis.series_profit_margin_percent,
                                             "volumes": analysis.total_volumes
                                         })
                
                return analysis
                
        except Exception as e:
            print(f"❌ Series profit analysis failed for {series_name}: {e}")
            return None
    
    def _load_book_cost_data(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Load cost data for a book."""
        if not AGENTS_AVAILABLE:
            # Try to load from file directly
            cost_file = Path("output/cost_tracking") / f"{book_id}_cost_breakdown.json"
            if cost_file.exists():
                with open(cost_file, 'r') as f:
                    return json.load(f)
            return None
        
        # Use cost tracker
        cost_files = Path("output/cost_tracking").glob(f"*{book_id}*_cost_breakdown.json")
        for cost_file in cost_files:
            try:
                with open(cost_file, 'r') as f:
                    return json.load(f)
            except:
                continue
        return None
    
    def _load_book_sales_data(self, book_id: str, asin: str = None) -> Optional[List[Dict[str, Any]]]:
        """Load sales data for a book."""
        if not AGENTS_AVAILABLE:
            return None
            
        try:
            sales_table = self.dynamodb.Table('KindleMint-SalesData')
            
            if asin:
                # Query by ASIN
                response = sales_table.query(
                    KeyConditionExpression='asin = :asin',
                    ExpressionAttributeValues={':asin': asin}
                )
            else:
                # Scan for book_id
                response = sales_table.scan(
                    FilterExpression='book_id = :book_id',
                    ExpressionAttributeValues={':book_id': book_id}
                )
            
            return response['Items']
            
        except Exception as e:
            print(f"⚠️ Failed to load sales data: {e}")
            return None
    
    def _get_series_book_analyses(self, series_name: str) -> List[BookProfitAnalysis]:
        """Get all book analyses for a series."""
        analyses = []
        
        # Load existing analyses
        for analysis_file in self.analysis_dir.glob(f"*{series_name}*_book_analysis.json"):
            try:
                with open(analysis_file, 'r') as f:
                    data = json.load(f)
                    # Convert back to dataclass
                    analysis = BookProfitAnalysis(**data)
                    analyses.append(analysis)
            except Exception as e:
                print(f"⚠️ Failed to load analysis from {analysis_file}: {e}")
        
        # Generate analyses for books that don't have them
        cost_files = Path("output/cost_tracking").glob("*_cost_breakdown.json")
        for cost_file in cost_files:
            try:
                with open(cost_file, 'r') as f:
                    cost_data = json.load(f)
                
                if cost_data.get('series_name') == series_name:
                    book_id = cost_data.get('book_id')
                    
                    # Check if we already have analysis
                    if any(a.book_id == book_id for a in analyses):
                        continue
                    
                    # Generate new analysis
                    analysis = self.analyze_book_profit(book_id)
                    if analysis:
                        analyses.append(analysis)
                        
            except Exception as e:
                print(f"⚠️ Failed to process cost file {cost_file}: {e}")
        
        return analyses
    
    def _calculate_book_profit(self, book_id: str, cost_data: Dict[str, Any], sales_data: List[Dict[str, Any]]) -> BookProfitAnalysis:
        """Calculate detailed profit analysis for a book."""
        # Extract cost information
        total_production_cost = Decimal(str(cost_data.get('total_production_cost', 0)))
        api_costs = Decimal(str(cost_data.get('total_api_cost', 0)))
        aws_costs = Decimal(str(cost_data.get('total_aws_cost', 0)))
        
        # Aggregate sales data
        total_units_sold = sum(int(record.get('units_sold', 0)) for record in sales_data)
        total_units_refunded = sum(int(record.get('units_refunded', 0)) for record in sales_data)
        net_units_sold = sum(int(record.get('net_units_sold', 0)) for record in sales_data)
        total_royalty = sum(Decimal(str(record.get('royalty_earned', 0))) for record in sales_data)
        
        # Calculate metrics
        cost_per_unit = total_production_cost / net_units_sold if net_units_sold > 0 else total_production_cost
        net_profit = total_royalty - total_production_cost
        profit_margin = (net_profit / total_royalty * 100) if total_royalty > 0 else 0
        roi = (net_profit / total_production_cost * 100) if total_production_cost > 0 else 0
        
        # Calculate break-even
        avg_royalty_per_unit = total_royalty / net_units_sold if net_units_sold > 0 else Decimal('0')
        break_even_units = int(total_production_cost / avg_royalty_per_unit) if avg_royalty_per_unit > 0 else 0
        
        # Performance metrics
        publication_date = cost_data.get('production_date', datetime.now().isoformat())
        days_since_pub = (datetime.now() - datetime.fromisoformat(publication_date.replace('Z', '+00:00').replace('+00:00', ''))).days
        daily_avg_sales = net_units_sold / max(days_since_pub, 1)
        monthly_proj_revenue = Decimal(str(daily_avg_sales * 30)) * avg_royalty_per_unit
        monthly_proj_profit = monthly_proj_revenue - (total_production_cost / max(days_since_pub / 30, 1))
        
        # Market position estimation
        market_info = self.market_data.get('large_print_crosswords', {})
        estimated_market_share = (net_units_sold / market_info.get('top_performer_units_monthly', 100)) * 100
        
        competitive_position = "Unknown"
        if profit_margin > 50:
            competitive_position = "Excellent"
        elif profit_margin > 25:
            competitive_position = "Good"
        elif profit_margin > 10:
            competitive_position = "Average"
        elif profit_margin > 0:
            competitive_position = "Poor"
        else:
            competitive_position = "Loss-making"
        
        # Get basic book info
        sample_record = sales_data[0] if sales_data else {}
        
        return BookProfitAnalysis(
            book_id=book_id,
            asin=sample_record.get('asin', ''),
            title=sample_record.get('title', cost_data.get('title', 'Unknown')),
            series_name=cost_data.get('series_name', ''),
            volume_number=cost_data.get('volume_number', 0),
            analysis_date=datetime.now().isoformat(),
            
            # Costs
            total_production_cost=total_production_cost,
            api_costs=api_costs,
            aws_costs=aws_costs,
            cost_per_unit=cost_per_unit,
            
            # Sales
            units_sold=total_units_sold,
            units_refunded=total_units_refunded,
            net_units_sold=net_units_sold,
            gross_revenue=total_royalty,  # For KDP, royalty is our revenue
            royalty_earned=total_royalty,
            average_royalty_rate=float(total_royalty / total_units_sold) if total_units_sold > 0 else 0,
            
            # Profit
            net_profit=net_profit,
            profit_margin_percent=float(profit_margin),
            roi_percent=float(roi),
            break_even_units=break_even_units,
            
            # Performance
            days_since_publication=days_since_pub,
            daily_average_sales=daily_avg_sales,
            monthly_projected_revenue=monthly_proj_revenue,
            monthly_projected_profit=monthly_proj_profit,
            
            # Market
            estimated_market_share=estimated_market_share,
            competitive_position=competitive_position
        )
    
    def _create_cost_only_analysis(self, book_id: str, cost_data: Dict[str, Any]) -> BookProfitAnalysis:
        """Create analysis when only cost data is available."""
        total_production_cost = Decimal(str(cost_data.get('total_production_cost', 0)))
        
        return BookProfitAnalysis(
            book_id=book_id,
            asin='',
            title=cost_data.get('title', 'Unknown'),
            series_name=cost_data.get('series_name', ''),
            volume_number=cost_data.get('volume_number', 0),
            analysis_date=datetime.now().isoformat(),
            
            # Costs
            total_production_cost=total_production_cost,
            api_costs=Decimal(str(cost_data.get('total_api_cost', 0))),
            aws_costs=Decimal(str(cost_data.get('total_aws_cost', 0))),
            cost_per_unit=total_production_cost,
            
            # Sales (all zeros - no sales data)
            units_sold=0,
            units_refunded=0,
            net_units_sold=0,
            gross_revenue=Decimal('0'),
            royalty_earned=Decimal('0'),
            average_royalty_rate=0.0,
            
            # Profit (all losses since no revenue)
            net_profit=-total_production_cost,
            profit_margin_percent=-100.0,
            roi_percent=-100.0,
            break_even_units=0,
            
            # Performance
            days_since_publication=0,
            daily_average_sales=0.0,
            monthly_projected_revenue=Decimal('0'),
            monthly_projected_profit=Decimal('0'),
            
            # Market
            estimated_market_share=0.0,
            competitive_position="No Sales Data"
        )
    
    def _calculate_series_profit(self, series_name: str, book_analyses: List[BookProfitAnalysis]) -> SeriesProfitAnalysis:
        """Calculate profit analysis for entire series."""
        # Aggregate metrics
        total_production_costs = sum(a.total_production_cost for a in book_analyses)
        total_api_costs = sum(a.api_costs for a in book_analyses)
        total_aws_costs = sum(a.aws_costs for a in book_analyses)
        
        total_units_sold = sum(a.units_sold for a in book_analyses)
        total_net_units_sold = sum(a.net_units_sold for a in book_analyses)
        total_royalty_earned = sum(a.royalty_earned for a in book_analyses)
        
        total_net_profit = sum(a.net_profit for a in book_analyses)
        
        # Calculate averages and percentages
        volumes_with_sales = len([a for a in book_analyses if a.net_units_sold > 0])
        avg_cost_per_volume = total_production_costs / len(book_analyses) if book_analyses else Decimal('0')
        series_profit_margin = (total_net_profit / total_royalty_earned * 100) if total_royalty_earned > 0 else -100
        series_roi = (total_net_profit / total_production_costs * 100) if total_production_costs > 0 else -100
        avg_royalty_rate = float(total_royalty_earned / total_units_sold) if total_units_sold > 0 else 0
        
        # Performance trends (simplified)
        monthly_growth_rate = 0.0  # Would need time-series data for accurate calculation
        
        # Best and worst performers
        profitable_books = [a for a in book_analyses if a.net_profit > 0]
        loss_making_books = [a for a in book_analyses if a.net_profit <= 0]
        
        best_performer = max(book_analyses, key=lambda x: x.net_profit) if book_analyses else None
        worst_performer = min(book_analyses, key=lambda x: x.net_profit) if book_analyses else None
        
        # Projections
        avg_monthly_profit_per_book = sum(a.monthly_projected_profit for a in book_analyses) / len(book_analyses) if book_analyses else Decimal('0')
        projected_annual_profit = avg_monthly_profit_per_book * 12 * len(book_analyses)
        projected_annual_revenue = sum(a.monthly_projected_revenue for a in book_analyses) * 12
        
        # Break-even timeline
        monthly_net_cash_flow = projected_annual_profit / 12
        break_even_months = int(abs(total_production_costs / monthly_net_cash_flow)) if monthly_net_cash_flow > 0 else 999
        
        return SeriesProfitAnalysis(
            series_name=series_name,
            analysis_date=datetime.now().isoformat(),
            
            # Overview
            total_volumes=len(book_analyses),
            published_volumes=len(book_analyses),  # All analyzed books are published
            volumes_with_sales=volumes_with_sales,
            
            # Costs
            total_production_costs=total_production_costs,
            average_cost_per_volume=avg_cost_per_volume,
            total_api_costs=total_api_costs,
            total_aws_costs=total_aws_costs,
            
            # Sales
            total_units_sold=total_units_sold,
            total_net_units_sold=total_net_units_sold,
            total_gross_revenue=total_royalty_earned,
            total_royalty_earned=total_royalty_earned,
            average_royalty_rate=avg_royalty_rate,
            
            # Profitability
            total_net_profit=total_net_profit,
            series_profit_margin_percent=float(series_profit_margin),
            series_roi_percent=float(series_roi),
            
            # Trends
            monthly_growth_rate=monthly_growth_rate,
            best_performing_volume={
                "volume": best_performer.volume_number if best_performer else 0,
                "profit": float(best_performer.net_profit) if best_performer else 0
            },
            worst_performing_volume={
                "volume": worst_performer.volume_number if worst_performer else 0,
                "profit": float(worst_performer.net_profit) if worst_performer else 0
            },
            
            # Projections
            projected_annual_revenue=projected_annual_revenue,
            projected_annual_profit=projected_annual_profit,
            break_even_timeline_months=break_even_months,
            
            # Details
            book_analyses=book_analyses
        )
    
    def _save_book_analysis(self, analysis: BookProfitAnalysis):
        """Save book analysis to file."""
        filename = f"{analysis.book_id}_{analysis.series_name}_book_analysis.json"
        filepath = self.analysis_dir / filename
        
        # Convert to JSON-serializable format
        data = asdict(analysis)
        
        # Convert Decimal values to strings
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 Book analysis saved: {filename}")
    
    def _save_series_analysis(self, analysis: SeriesProfitAnalysis):
        """Save series analysis to file."""
        filename = f"{analysis.series_name}_series_analysis.json"
        filepath = self.analysis_dir / filename
        
        # Convert to JSON-serializable format
        data = asdict(analysis)
        
        # Convert Decimal values and nested objects
        def convert_decimals(obj):
            if isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif isinstance(obj, Decimal):
                return str(obj)
            else:
                return obj
        
        data = convert_decimals(data)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 Series analysis saved: {filename}")
    
    def generate_profit_report(self, series_name: str = None) -> Dict[str, Any]:
        """Generate comprehensive profit report."""
        try:
            print(f"📋 Generating profit report for {series_name or 'all series'}")
            
            if series_name:
                # Single series report
                series_analysis = self.analyze_series_profit(series_name)
                if not series_analysis:
                    return {"error": f"No data found for series: {series_name}"}
                
                report = {
                    "report_type": "series",
                    "series_name": series_name,
                    "generated_at": datetime.now().isoformat(),
                    "summary": {
                        "total_volumes": series_analysis.total_volumes,
                        "total_profit": str(series_analysis.total_net_profit),
                        "profit_margin": series_analysis.series_profit_margin_percent,
                        "roi": series_analysis.series_roi_percent
                    },
                    "analysis": asdict(series_analysis)
                }
            else:
                # All series report
                all_analyses = []
                series_dirs = set()
                
                # Find all series
                for analysis_file in self.analysis_dir.glob("*_series_analysis.json"):
                    series_name = analysis_file.stem.replace('_series_analysis', '')
                    series_dirs.add(series_name)
                
                for series in series_dirs:
                    analysis = self.analyze_series_profit(series)
                    if analysis:
                        all_analyses.append(analysis)
                
                # Calculate portfolio metrics
                total_profit = sum(a.total_net_profit for a in all_analyses)
                total_revenue = sum(a.total_royalty_earned for a in all_analyses)
                total_costs = sum(a.total_production_costs for a in all_analyses)
                
                report = {
                    "report_type": "portfolio",
                    "generated_at": datetime.now().isoformat(),
                    "summary": {
                        "total_series": len(all_analyses),
                        "total_profit": str(total_profit),
                        "total_revenue": str(total_revenue),
                        "total_costs": str(total_costs),
                        "portfolio_margin": float(total_profit / total_revenue * 100) if total_revenue > 0 else 0
                    },
                    "series_analyses": [asdict(a) for a in all_analyses]
                }
            
            # Save report
            report_filename = f"profit_report_{series_name or 'portfolio'}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(self.analysis_dir / report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            return report
            
        except Exception as e:
            print(f"❌ Profit report generation failed: {e}")
            return {"error": str(e)}

# Global profit calculator instance
profit_calculator = ProfitMarginCalculator()

# Convenience functions
def analyze_book(book_id: str, asin: str = None):
    """Analyze profit for a single book."""
    return profit_calculator.analyze_book_profit(book_id, asin)

def analyze_series(series_name: str):
    """Analyze profit for a series."""
    return profit_calculator.analyze_series_profit(series_name)

def generate_report(series_name: str = None):
    """Generate profit report."""
    return profit_calculator.generate_profit_report(series_name)

def get_portfolio_summary():
    """Get portfolio profit summary."""
    return profit_calculator.generate_profit_report()