"""
Data Processing Module
Handles cleaning, analysis, and processing of collected airline data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
import json
import os

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes and analyzes airline booking data"""
    
    def __init__(self):
        self.processed_data_dir = 'data/processed'
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def process_data(self, raw_data: Dict) -> Dict:
        """Main method to process raw flight data"""
        
        logger.info("Processing flight data...")
        
        if not raw_data.get('flights'):
            return self._get_empty_processed_data()
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(raw_data['flights'])
        
        # Clean and standardize the data
        df_clean = self._clean_data(df)
        
        # Perform analysis
        analysis = {
            'summary': self._generate_summary(df_clean),
            'price_analysis': self._analyze_prices(df_clean),
            'route_analysis': self._analyze_routes(df_clean),
            'time_analysis': self._analyze_time_patterns(df_clean),
            'demand_analysis': self._analyze_demand(df_clean),
            'airline_analysis': self._analyze_airlines(df_clean)
        }
        
        # Combine with market data
        processed_data = {
            'search_params': raw_data.get('search_params', {}),
            'flights_data': df_clean.to_dict('records'),
            'analysis': analysis,
            'market_data': raw_data.get('market_data', {}),
            'processing_timestamp': datetime.now().isoformat(),
            'total_flights': len(df_clean)
        }
        
        # Save processed data
        self._save_processed_data(processed_data)
        
        return processed_data
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the flight data"""
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Ensure required columns exist
        required_columns = ['price', 'origin', 'destination', 'date']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Clean price data
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        df = df[df['price'] > 0]
        
        # Standardize airport codes
        df['origin'] = df['origin'].str.upper()
        df['destination'] = df['destination'].str.upper()
        
        # Parse dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Add derived columns
        df['day_of_week'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name()
        df['is_weekend'] = df['date'].dt.weekday >= 5
        
        # Add route column
        df['route'] = df['origin'] + '-' + df['destination']
        
        return df
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics"""
        
        return {
            'total_flights': len(df),
            'unique_routes': df['route'].nunique(),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'price_range': {
                'min': float(df['price'].min()),
                'max': float(df['price'].max()),
                'avg': float(df['price'].mean()),
                'median': float(df['price'].median())
            },
            'airlines': df['airline'].nunique() if 'airline' in df.columns else 0
        }
    
    def _analyze_prices(self, df: pd.DataFrame) -> Dict:
        """Analyze price patterns and trends"""
        
        price_analysis = {
            'statistics': {
                'mean': float(df['price'].mean()),
                'median': float(df['price'].median()),
                'std': float(df['price'].std()),
                'min': float(df['price'].min()),
                'max': float(df['price'].max())
            },
            'by_day_of_week': df.groupby('day_of_week')['price'].mean().to_dict(),
            'by_month': df.groupby('month')['price'].mean().to_dict(),
            'weekend_premium': {
                'weekend_avg': float(df[df['is_weekend']]['price'].mean()),
                'weekday_avg': float(df[~df['is_weekend']]['price'].mean())
            }
        }
        
        # Calculate weekend premium percentage
        weekend_avg = price_analysis['weekend_premium']['weekend_avg']
        weekday_avg = price_analysis['weekend_premium']['weekday_avg']
        if weekday_avg > 0:
            price_analysis['weekend_premium']['premium_percentage'] = \
                ((weekend_avg - weekday_avg) / weekday_avg) * 100
        
        return price_analysis
    
    def _analyze_routes(self, df: pd.DataFrame) -> Dict:
        """Analyze route popularity and characteristics"""

        # Check if 'direct' column exists
        agg_dict = {'price': ['count', 'mean', 'min', 'max']}
        if 'direct' in df.columns:
            agg_dict['direct'] = 'mean'

        route_stats = df.groupby('route').agg(agg_dict).round(2)
        
        # Set column names based on what columns we have
        if 'direct' in df.columns:
            route_stats.columns = ['flight_count', 'avg_price', 'min_price', 'max_price', 'direct_ratio']
        else:
            route_stats.columns = ['flight_count', 'avg_price', 'min_price', 'max_price']
        route_stats = route_stats.reset_index()
        
        # Sort by flight count (popularity)
        route_stats = route_stats.sort_values('flight_count', ascending=False)
        
        return {
            'popular_routes': route_stats.head(10).to_dict('records'),
            'total_routes': len(route_stats),
            'most_expensive_route': route_stats.loc[route_stats['avg_price'].idxmax()].to_dict(),
            'cheapest_route': route_stats.loc[route_stats['avg_price'].idxmin()].to_dict()
        }
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze time-based patterns"""
        
        # Daily flight counts
        daily_counts = df.groupby(df['date'].dt.date)['price'].count()
        
        # Weekly patterns
        weekly_pattern = df.groupby('day_of_week')['price'].count().to_dict()
        
        return {
            'daily_flight_counts': daily_counts.to_dict(),
            'weekly_pattern': weekly_pattern,
            'busiest_day': daily_counts.idxmax().strftime('%Y-%m-%d'),
            'quietest_day': daily_counts.idxmin().strftime('%Y-%m-%d'),
            'avg_flights_per_day': float(daily_counts.mean())
        }
    
    def _analyze_demand(self, df: pd.DataFrame) -> Dict:
        """Analyze demand patterns"""
        
        demand_analysis = {
            'high_demand_routes': [],
            'price_demand_correlation': 0,
            'peak_times': {}
        }
        
        # If demand_score is available
        if 'demand_score' in df.columns:
            # High demand routes (top 20% by demand score)
            route_demand = df.groupby('route')['demand_score'].mean().sort_values(ascending=False)
            high_demand_threshold = route_demand.quantile(0.8)
            demand_analysis['high_demand_routes'] = route_demand[route_demand >= high_demand_threshold].to_dict()
            
            # Correlation between price and demand
            demand_analysis['price_demand_correlation'] = float(df['price'].corr(df['demand_score']))
        
        # Peak times based on flight frequency
        if 'time' in df.columns:
            df['hour'] = pd.to_datetime(df['time'], format='%H:%M', errors='coerce').dt.hour
            hourly_counts = df.groupby('hour')['price'].count()
            demand_analysis['peak_times'] = {
                'busiest_hour': int(hourly_counts.idxmax()),
                'quietest_hour': int(hourly_counts.idxmin()),
                'hourly_distribution': hourly_counts.to_dict()
            }
        
        return demand_analysis
    
    def _analyze_airlines(self, df: pd.DataFrame) -> Dict:
        """Analyze airline-specific patterns"""
        
        if 'airline' not in df.columns:
            return {'message': 'No airline data available'}
        
        airline_stats = df.groupby('airline').agg({
            'price': ['count', 'mean', 'min', 'max'],
            'direct': 'mean'
        }).round(2)
        
        airline_stats.columns = ['flight_count', 'avg_price', 'min_price', 'max_price', 'direct_ratio']
        airline_stats = airline_stats.reset_index()
        airline_stats = airline_stats.sort_values('flight_count', ascending=False)
        
        return {
            'airline_rankings': airline_stats.to_dict('records'),
            'most_flights': airline_stats.iloc[0]['airline'],
            'cheapest_airline': airline_stats.loc[airline_stats['avg_price'].idxmin()]['airline'],
            'most_expensive_airline': airline_stats.loc[airline_stats['avg_price'].idxmax()]['airline']
        }
    
    def get_trending_routes(self) -> List[Dict]:
        """Get trending route information"""
        
        # Sample trending data
        trending_routes = [
            {'route': 'SYD-MEL', 'trend': 'up', 'change': '+12%', 'volume': 1250},
            {'route': 'MEL-SYD', 'trend': 'stable', 'change': '+2%', 'volume': 1180},
            {'route': 'SYD-BNE', 'trend': 'down', 'change': '-8%', 'volume': 890},
            {'route': 'BNE-SYD', 'trend': 'up', 'change': '+15%', 'volume': 845},
            {'route': 'MEL-BNE', 'trend': 'stable', 'change': '+1%', 'volume': 650}
        ]
        
        return trending_routes
    
    def get_price_trends(self) -> Dict:
        """Get price trend analysis"""
        
        return {
            'overall_trend': 'increasing',
            'monthly_change': '+5.2%',
            'seasonal_patterns': {
                'peak_season': 'December-January',
                'low_season': 'February-March',
                'price_difference': '25-30%'
            },
            'forecast': {
                'next_month': '+3%',
                'next_quarter': '+8%'
            }
        }
    
    def get_sample_data(self) -> Dict:
        """Get sample data for API endpoints"""
        
        return {
            'popular_routes': [
                {'route': 'SYD-MEL', 'flights': 45, 'avg_price': 165},
                {'route': 'MEL-SYD', 'flights': 42, 'avg_price': 158},
                {'route': 'SYD-BNE', 'flights': 28, 'avg_price': 220}
            ],
            'price_trends': {
                'this_week': 185,
                'last_week': 178,
                'change': '+3.9%'
            }
        }
    
    def _get_empty_processed_data(self) -> Dict:
        """Return empty processed data structure"""
        
        return {
            'search_params': {},
            'flights_data': [],
            'analysis': {
                'summary': {'total_flights': 0},
                'price_analysis': {},
                'route_analysis': {},
                'time_analysis': {},
                'demand_analysis': {},
                'airline_analysis': {}
            },
            'market_data': {},
            'processing_timestamp': datetime.now().isoformat(),
            'total_flights': 0
        }
    
    def _save_processed_data(self, data: Dict) -> None:
        """Save processed data to file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'processed_data_{timestamp}.json'
        filepath = os.path.join(self.processed_data_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Processed data saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save processed data: {str(e)}")
