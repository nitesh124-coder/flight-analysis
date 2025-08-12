"""
Data Collection Module
Handles scraping and API integration for airline booking data
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from bs4 import BeautifulSoup
import pandas as pd
import random

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects airline booking data from various sources"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.amadeus_client_id = os.getenv('AMADEUS_CLIENT_ID')
        self.amadeus_client_secret = os.getenv('AMADEUS_CLIENT_SECRET')
        self.cache_dir = 'data/cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def collect_flight_data(self, origin: str, destination: str, 
                          date_from: str, date_to: str) -> Dict:
        """Main method to collect flight data from multiple sources"""
        
        logger.info(f"Collecting flight data: {origin} -> {destination}, {date_from} to {date_to}")
        
        # Try multiple data sources
        data = {
            'search_params': {
                'origin': origin,
                'destination': destination,
                'date_from': date_from,
                'date_to': date_to
            },
            'flights': [],
            'market_data': {},
            'collection_timestamp': datetime.now().isoformat()
        }
        
        # Source 1: RapidAPI Skyscanner (if API key available)
        if self.rapidapi_key:
            try:
                rapidapi_data = self._collect_from_rapidapi(origin, destination, date_from)
                data['flights'].extend(rapidapi_data)
                logger.info(f"Collected {len(rapidapi_data)} flights from RapidAPI")
            except Exception as e:
                logger.warning(f"RapidAPI collection failed: {str(e)}")
        
        # Source 2: Generate sample data for demonstration
        sample_data = self._generate_sample_data(origin, destination, date_from, date_to)
        data['flights'].extend(sample_data)
        
        # Source 3: Collect market trends data
        data['market_data'] = self._collect_market_trends()
        
        # Cache the results
        self._cache_data(data)
        
        return data
    
    def _collect_from_rapidapi(self, origin: str, destination: str, date: str) -> List[Dict]:
        """Collect data from RapidAPI Skyscanner"""
        
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/{}/{}/{}".format(
            origin, destination, date
        )
        
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            flights = []
            
            # Process the response data
            if 'Quotes' in data:
                for quote in data['Quotes']:
                    flight = {
                        'price': quote.get('MinPrice', 0),
                        'origin': origin,
                        'destination': destination,
                        'date': date,
                        'direct': quote.get('Direct', False),
                        'source': 'rapidapi_skyscanner'
                    }
                    flights.append(flight)
            
            return flights
            
        except Exception as e:
            logger.error(f"RapidAPI request failed: {str(e)}")
            return []
    
    def _generate_sample_data(self, origin: str, destination: str, 
                            date_from: str, date_to: str) -> List[Dict]:
        """Generate realistic sample flight data for demonstration"""
        
        flights = []
        
        # Popular routes with base prices
        route_prices = {
            ('SYD', 'MEL'): 150,
            ('MEL', 'SYD'): 150,
            ('SYD', 'BNE'): 200,
            ('BNE', 'SYD'): 200,
            ('MEL', 'BNE'): 250,
            ('BNE', 'MEL'): 250,
            ('SYD', 'PER'): 400,
            ('PER', 'SYD'): 400,
            ('MEL', 'ADL'): 180,
            ('ADL', 'MEL'): 180,
        }
        
        # Get base price for route
        route_key = (origin.upper(), destination.upper())
        base_price = route_prices.get(route_key, 300)
        
        # Generate flights for date range
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d') if date_from else datetime.now()
            end_date = datetime.strptime(date_to, '%Y-%m-%d') if date_to else start_date + timedelta(days=7)
        except:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=7)
        
        current_date = start_date
        while current_date <= end_date:
            # Generate 3-8 flights per day
            num_flights = random.randint(3, 8)
            
            for i in range(num_flights):
                # Price variation based on time and demand
                price_multiplier = random.uniform(0.7, 1.8)
                
                # Weekend premium
                if current_date.weekday() >= 5:
                    price_multiplier *= 1.2
                
                # Peak hours premium
                hour = random.randint(6, 22)
                if hour in [7, 8, 17, 18, 19]:
                    price_multiplier *= 1.15
                
                flight = {
                    'price': round(base_price * price_multiplier),
                    'origin': origin.upper(),
                    'destination': destination.upper(),
                    'date': current_date.strftime('%Y-%m-%d'),
                    'time': f"{hour:02d}:{random.randint(0, 59):02d}",
                    'airline': random.choice(['Jetstar', 'Virgin Australia', 'Qantas', 'Tiger Airways']),
                    'direct': random.choice([True, True, False]),  # 2/3 chance of direct
                    'duration': random.randint(90, 300),  # minutes
                    'source': 'sample_data',
                    'demand_score': random.uniform(0.3, 1.0)
                }
                flights.append(flight)
            
            current_date += timedelta(days=1)
        
        return flights
    
    def _collect_market_trends(self) -> Dict:
        """Collect general market trend data and enrich with public scrape if available"""

        # Base sample market data (fallback)
        popular_routes = [
            {'route': 'SYD-MEL', 'volume': 1250, 'avg_price': 165, 'trend': 'up'},
            {'route': 'MEL-SYD', 'volume': 1180, 'avg_price': 158, 'trend': 'stable'},
            {'route': 'SYD-BNE', 'volume': 890, 'avg_price': 220, 'trend': 'down'},
            {'route': 'BNE-SYD', 'volume': 845, 'avg_price': 215, 'trend': 'up'},
            {'route': 'MEL-BNE', 'volume': 650, 'avg_price': 275, 'trend': 'stable'},
        ]

        # Try to enrich with a lightweight public scrape (non-blocking on failure)
        try:
            scraped = self._scrape_wikipedia_routes()
            # Merge mapped scraped routes if any (prepend to highlight "real" data)
            if scraped:
                # Avoid duplicates by route key
                existing = {r['route'] for r in popular_routes}
                enriched = [r for r in scraped if r['route'] not in existing]
                popular_routes = enriched + popular_routes
        except Exception as e:
            logger.warning(f"Scrape enrichment failed: {e}")

        seasonal_trends = {
            'peak_months': ['December', 'January', 'July'],
            'low_months': ['February', 'March', 'August'],
            'price_variation': '15-30%',
            'booking_lead_time': '21-45 days'
        }

        return {
            'popular_routes': popular_routes,
            'seasonal_trends': seasonal_trends,
            'last_updated': datetime.now().isoformat()
        }

    def _scrape_wikipedia_routes(self) -> List[Dict]:
        """Scrape Wikipedia for busiest Australian domestic air routes and map to IATA codes.
        Returns a list like: [{'route': 'SYD-MEL', 'volume': 900, 'trend': 'up'}]
        """
        url_candidates = [
            'https://en.wikipedia.org/wiki/List_of_busiest_air_routes_in_Australia',
            'https://en.wikipedia.org/wiki/List_of_the_busiest_air_routes'
        ]
        city_to_iata = {
            'sydney': 'SYD', 'melbourne': 'MEL', 'brisbane': 'BNE', 'perth': 'PER',
            'adelaide': 'ADL', 'canberra': 'CBR', 'darwin': 'DRW', 'hobart': 'HBA',
            'gold coast': 'OOL'
        }
        results: List[Dict] = []
        for url in url_candidates:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, 'lxml')
                tables = soup.select('table.wikitable')
                for table in tables:
                    for tr in table.select('tr')[1:]:
                        tds = [td.get_text(strip=True) for td in tr.select('td')]
                        if len(tds) < 2:
                            continue
                        # Try to extract a route like "Sydney–Melbourne" and a volume number
                        route_text = tds[0].lower()
                        vol_text = ''.join(ch for ch in ''.join(tds[1:3]) if ch.isdigit())
                        # Map city names to IATA if both ends known
                        sep = '–' if '–' in route_text else '-' if '-' in route_text else ' to '
                        parts = [p.strip() for p in route_text.replace('—', '-').replace(' to ', '-').split('-')]
                        if len(parts) != 2:
                            continue
                        a, b = parts[0], parts[1]
                        a_iata = city_to_iata.get(a, None)
                        b_iata = city_to_iata.get(b, None)
                        if not (a_iata and b_iata):
                            # Try contains (e.g., 'sydney (domestic)')
                            for city, code in city_to_iata.items():
                                if city in a and not a_iata:
                                    a_iata = code
                                if city in b and not b_iata:
                                    b_iata = code
                        if a_iata and b_iata:
                            volume = int(vol_text) if vol_text.isdigit() else None
                            results.append({'route': f'{a_iata}-{b_iata}', 'volume': volume or 0, 'trend': 'up'})
                if results:
                    break
            except Exception as e:
                logger.debug(f"Wikipedia scrape error for {url}: {e}")
                continue
        # Deduplicate by route
        unique = {}
        for r in results:
            unique[r['route']] = r
        return list(unique.values())[:10]

    def _cache_data(self, data: Dict) -> None:
        """Cache collected data for future use"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        cache_file = os.path.join(self.cache_dir, f'flight_data_{timestamp}.json')

        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data cached to {cache_file}")
        except Exception as e:
            logger.error(f"Failed to cache data: {str(e)}")

    def get_cached_data(self, max_age_hours: int = 24) -> Optional[Dict]:
        """Retrieve recent cached data if available"""

        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith('flight_data_')]
            if not cache_files:
                return None

            # Get most recent cache file
            latest_file = max(cache_files)
            cache_path = os.path.join(self.cache_dir, latest_file)

            # Check if cache is still fresh
            file_time = os.path.getmtime(cache_path)
            if time.time() - file_time > max_age_hours * 3600:
                return None

            with open(cache_path, 'r') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load cached data: {str(e)}")
            return None
