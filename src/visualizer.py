"""
Data Visualization Module
Creates charts and graphs for airline booking data visualization
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import pandas as pd
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataVisualizer:
    """Creates interactive visualizations for airline booking data"""
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_charts(self, processed_data: Dict) -> Dict:
        """Create all visualization charts from processed data"""
        
        logger.info("Creating visualization charts...")
        
        charts = {}
        
        try:
            # Price trend chart
            charts['price_trends'] = self._create_price_trend_chart(processed_data)
            
            # Route popularity chart
            charts['route_popularity'] = self._create_route_popularity_chart(processed_data)
            
            # Weekly pattern chart
            charts['weekly_patterns'] = self._create_weekly_pattern_chart(processed_data)
            
            # Price distribution chart
            charts['price_distribution'] = self._create_price_distribution_chart(processed_data)
            
            # Airline comparison chart
            charts['airline_comparison'] = self._create_airline_comparison_chart(processed_data)
            
            # Daily flight volume chart
            charts['daily_volume'] = self._create_daily_volume_chart(processed_data)
            
            logger.info(f"Created {len(charts)} visualization charts")
            
        except Exception as e:
            logger.error(f"Error creating charts: {str(e)}")
            charts['error'] = str(e)
        
        return charts
    
    def _create_price_trend_chart(self, data: Dict) -> str:
        """Create price trend over time chart"""
        
        flights_data = data.get('flights_data', [])
        if not flights_data:
            return self._create_empty_chart("No data available for price trends")
        
        # Convert to DataFrame
        df = pd.DataFrame(flights_data)
        
        # Group by date and calculate average price
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            daily_prices = df.groupby(df['date'].dt.date)['price'].mean().reset_index()
            daily_prices.columns = ['date', 'avg_price']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_prices['date'],
                y=daily_prices['avg_price'],
                mode='lines+markers',
                name='Average Price',
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title='Price Trends Over Time',
                xaxis_title='Date',
                yaxis_title='Average Price ($)',
                hovermode='x unified',
                template='plotly_white'
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return self._create_empty_chart("Date information not available")
    
    def _create_route_popularity_chart(self, data: Dict) -> str:
        """Create route popularity bar chart"""
        
        analysis = data.get('analysis', {})
        route_analysis = analysis.get('route_analysis', {})
        popular_routes = route_analysis.get('popular_routes', [])
        
        if not popular_routes:
            return self._create_empty_chart("No route data available")
        
        # Take top 10 routes
        top_routes = popular_routes[:10]
        routes = [route['route'] for route in top_routes]
        flight_counts = [route['flight_count'] for route in top_routes]
        avg_prices = [route['avg_price'] for route in top_routes]
        
        fig = go.Figure()
        
        # Flight count bars
        fig.add_trace(go.Bar(
            x=routes,
            y=flight_counts,
            name='Flight Count',
            marker_color=self.color_palette[0],
            yaxis='y'
        ))
        
        # Average price line
        fig.add_trace(go.Scatter(
            x=routes,
            y=avg_prices,
            mode='lines+markers',
            name='Average Price',
            line=dict(color=self.color_palette[1], width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Route Popularity and Pricing',
            xaxis_title='Routes',
            yaxis=dict(title='Flight Count', side='left'),
            yaxis2=dict(title='Average Price ($)', side='right', overlaying='y'),
            hovermode='x unified',
            template='plotly_white',
            legend=dict(x=0.7, y=1)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _create_weekly_pattern_chart(self, data: Dict) -> str:
        """Create weekly flight pattern chart"""
        
        analysis = data.get('analysis', {})
        price_analysis = analysis.get('price_analysis', {})
        by_day = price_analysis.get('by_day_of_week', {})
        
        if not by_day:
            return self._create_empty_chart("No weekly pattern data available")
        
        # Order days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days = [day for day in day_order if day in by_day]
        prices = [by_day[day] for day in days]
        
        # Color weekends differently
        colors = [self.color_palette[1] if day in ['Saturday', 'Sunday'] else self.color_palette[0] for day in days]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=prices,
            marker_color=colors,
            name='Average Price by Day'
        ))
        
        fig.update_layout(
            title='Weekly Price Patterns',
            xaxis_title='Day of Week',
            yaxis_title='Average Price ($)',
            template='plotly_white',
            showlegend=False
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _create_price_distribution_chart(self, data: Dict) -> str:
        """Create price distribution histogram"""
        
        flights_data = data.get('flights_data', [])
        if not flights_data:
            return self._create_empty_chart("No data available for price distribution")
        
        prices = [flight['price'] for flight in flights_data if 'price' in flight]
        
        if not prices:
            return self._create_empty_chart("No price data available")
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=prices,
            nbinsx=20,
            marker_color=self.color_palette[2],
            opacity=0.7,
            name='Price Distribution'
        ))
        
        fig.update_layout(
            title='Price Distribution',
            xaxis_title='Price ($)',
            yaxis_title='Number of Flights',
            template='plotly_white',
            showlegend=False
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _create_airline_comparison_chart(self, data: Dict) -> str:
        """Create airline comparison chart"""
        
        analysis = data.get('analysis', {})
        airline_analysis = analysis.get('airline_analysis', {})
        airline_rankings = airline_analysis.get('airline_rankings', [])
        
        if not airline_rankings:
            return self._create_empty_chart("No airline data available")
        
        airlines = [airline['airline'] for airline in airline_rankings]
        flight_counts = [airline['flight_count'] for airline in airline_rankings]
        avg_prices = [airline['avg_price'] for airline in airline_rankings]
        
        fig = go.Figure()
        
        # Flight count bars
        fig.add_trace(go.Bar(
            x=airlines,
            y=flight_counts,
            name='Flight Count',
            marker_color=self.color_palette[3],
            yaxis='y'
        ))
        
        # Average price line
        fig.add_trace(go.Scatter(
            x=airlines,
            y=avg_prices,
            mode='lines+markers',
            name='Average Price',
            line=dict(color=self.color_palette[4], width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Airline Comparison: Flight Volume vs Pricing',
            xaxis_title='Airlines',
            yaxis=dict(title='Flight Count', side='left'),
            yaxis2=dict(title='Average Price ($)', side='right', overlaying='y'),
            hovermode='x unified',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _create_daily_volume_chart(self, data: Dict) -> str:
        """Create daily flight volume chart"""
        
        analysis = data.get('analysis', {})
        time_analysis = analysis.get('time_analysis', {})
        daily_counts = time_analysis.get('daily_flight_counts', {})
        
        if not daily_counts:
            return self._create_empty_chart("No daily volume data available")
        
        # Convert to lists for plotting
        dates = list(daily_counts.keys())
        counts = list(daily_counts.values())
        
        # Convert string dates to datetime if needed
        try:
            dates = [pd.to_datetime(date) for date in dates]
        except:
            pass
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='Daily Flight Count',
            line=dict(color=self.color_palette[5], width=2),
            marker=dict(size=4),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title='Daily Flight Volume',
            xaxis_title='Date',
            yaxis_title='Number of Flights',
            template='plotly_white',
            showlegend=False
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _create_empty_chart(self, message: str) -> str:
        """Create an empty chart with a message"""
        
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        
        fig.update_layout(
            title='No Data Available',
            template='plotly_white',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_summary_metrics(self, data: Dict) -> Dict:
        """Create summary metrics for dashboard"""
        
        analysis = data.get('analysis', {})
        summary = analysis.get('summary', {})
        
        metrics = {
            'total_flights': summary.get('total_flights', 0),
            'unique_routes': summary.get('unique_routes', 0),
            'avg_price': summary.get('price_range', {}).get('avg', 0),
            'price_range': {
                'min': summary.get('price_range', {}).get('min', 0),
                'max': summary.get('price_range', {}).get('max', 0)
            },
            'date_range': summary.get('date_range', {}),
            'airlines': summary.get('airlines', 0)
        }
        
        return metrics
