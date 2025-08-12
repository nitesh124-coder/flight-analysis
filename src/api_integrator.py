"""
API Integration Module
Handles integration with AI APIs for generating insights from flight data
"""

import openai
import os
import json
import logging
import requests
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class APIIntegrator:
    """Integrates with AI APIs to generate insights from flight data"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def get_insights(self, processed_data: Dict) -> Dict:
        """Generate AI-powered insights from processed flight data"""

        logger.info("Generating AI insights from processed data...")

        # If OpenAI API is available, use it for insights
        if self.openai_api_key:
            try:
                ai_insights = self._get_openai_insights(processed_data)
                return ai_insights
            except Exception as e:
                logger.warning(f"OpenAI API failed: {str(e)}, trying free HF API, else rule-based insights")
                # fallback to free HuggingFace Inference if token is provided
                hf = os.getenv('HUGGINGFACE_API_TOKEN')
                if hf:
                    try:
                        return self._get_hf_insights(processed_data, hf)
                    except Exception as ie:
                        logger.warning(f"HuggingFace API failed: {ie}")
                # Next fallback
                return self._generate_rule_based_insights(processed_data)
        else:
            # No OpenAI key; attempt free HF first if token provided
            hf = os.getenv('HUGGINGFACE_API_TOKEN')
            if hf:
                try:
                    return self._get_hf_insights(processed_data, hf)
                except Exception as e:
                    logger.warning(f"HuggingFace API failed: {e}, using rule-based insights")
            return self._generate_rule_based_insights(processed_data)

    def _get_openai_insights(self, data: Dict) -> Dict:
        """Get insights using OpenAI API"""

        # Prepare data summary for AI analysis
        summary = self._prepare_data_summary(data)

        prompt = f"""
        Analyze the following airline booking data and provide insights for a hostel business
        looking to understand market demand trends:

        {summary}

        Please provide insights in the following areas:
        1. Market demand trends
        2. Pricing patterns and opportunities
        3. Popular routes and timing
        4. Recommendations for hostel business
        5. Future outlook

        Format your response as JSON with the following structure:
        {{
            "demand_trends": "analysis of demand patterns",
            "pricing_insights": "key pricing observations",
            "route_recommendations": "recommended routes to focus on",
            "business_recommendations": "specific advice for hostel business",
            "market_outlook": "future predictions and trends"
        }}
        """

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )

            # Parse the AI response
            ai_text = response.choices[0].text.strip()

            # Try to extract JSON from the response
            try:
                insights = json.loads(ai_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                insights = {
                    "demand_trends": ai_text[:200] + "...",
                    "pricing_insights": "AI analysis provided",
    def _get_hf_insights(self, data: Dict, token: str) -> Dict:
        """Get insights from a free Hugging Face model (e.g., text summarization) as a fallback.
        This keeps costs at zero when OpenAI is not configured.
        """
        summary = self._prepare_data_summary(data)
        # Use a lightweight summarization model
        api_url = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": summary[:2000]}
        try:
            r = requests.post(api_url, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            out = r.json()
            text = ''
            if isinstance(out, list) and out and 'summary_text' in out[0]:
                text = out[0]['summary_text']
            elif isinstance(out, dict) and 'generated_text' in out:
                text = out['generated_text']
            else:
                text = str(out)[:500]
            insights = {
                "demand_trends": text[:200] + ("..." if len(text) > 200 else ""),
                "pricing_insights": "Summarized insights derived from public model",
                "route_recommendations": "Focus on busiest domestic routes and stable corridors",
                "business_recommendations": "Adjust hostel pricing around peak/low seasons; partner on top routes",
                "market_outlook": "Moderately positive outlook based on summarized trends",
                "source": "huggingface_api",
                "generated_at": datetime.now().isoformat()
            }
            return insights
        except Exception as e:
            logger.error(f"HF Inference API error: {e}")
            raise

                    "route_recommendations": "See full analysis",
                    "business_recommendations": "Detailed recommendations available",
                    "market_outlook": "Positive outlook based on data",
                    "full_analysis": ai_text
                }

            # Add metadata
            insights["source"] = "openai_api"
            insights["generated_at"] = datetime.now().isoformat()

            return insights

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _prepare_data_summary(self, data: Dict) -> str:
        """Prepare a concise summary of the data for AI analysis"""

        analysis = data.get('analysis', {})
        summary_stats = analysis.get('summary', {})
        price_analysis = analysis.get('price_analysis', {})
        route_analysis = analysis.get('route_analysis', {})

        summary = f"""
        Flight Data Summary:
        - Total flights analyzed: {summary_stats.get('total_flights', 0)}
        - Date range: {summary_stats.get('date_range', {}).get('start', 'N/A')} to {summary_stats.get('date_range', {}).get('end', 'N/A')}
        - Price range: ${summary_stats.get('price_range', {}).get('min', 0)} - ${summary_stats.get('price_range', {}).get('max', 0)}
        - Average price: ${summary_stats.get('price_range', {}).get('avg', 0):.2f}

        Popular Routes:
        """

        # Add popular routes
        popular_routes = route_analysis.get('popular_routes', [])[:5]
        for route in popular_routes:
            summary += f"- {route.get('route', 'N/A')}: {route.get('flight_count', 0)} flights, avg ${route.get('avg_price', 0):.2f}\n"

        # Add pricing insights
        weekend_premium = price_analysis.get('weekend_premium', {})
        if weekend_premium:
            summary += f"\nWeekend vs Weekday Pricing:\n"
            summary += f"- Weekend average: ${weekend_premium.get('weekend_avg', 0):.2f}\n"
            summary += f"- Weekday average: ${weekend_premium.get('weekday_avg', 0):.2f}\n"

        return summary

    def _generate_rule_based_insights(self, data: Dict) -> Dict:
        """Generate insights using rule-based analysis (fallback when AI API unavailable)"""

        analysis = data.get('analysis', {})
        summary_stats = analysis.get('summary', {})
        price_analysis = analysis.get('price_analysis', {})
        route_analysis = analysis.get('route_analysis', {})
        time_analysis = analysis.get('time_analysis', {})

        insights = {
            "source": "rule_based_analysis",
            "generated_at": datetime.now().isoformat()
        }

        # Demand trends analysis
        total_flights = summary_stats.get('total_flights', 0)
        if total_flights > 100:
            insights["demand_trends"] = "High demand detected with strong booking activity across multiple routes. Market shows healthy competition and frequent flights."
        elif total_flights > 50:
            insights["demand_trends"] = "Moderate demand with steady booking patterns. Good opportunities for targeted marketing."
        else:
            insights["demand_trends"] = "Lower demand period detected. Consider focusing on high-value routes and promotional strategies."

        # Pricing insights
        price_stats = price_analysis.get('statistics', {})
        avg_price = price_stats.get('mean', 0)
        price_std = price_stats.get('std', 0)

        if avg_price > 0 and price_std / avg_price > 0.3:  # High price variation
            insights["pricing_insights"] = f"High price volatility detected (avg: ${avg_price:.2f}). Significant opportunities for finding deals. Price varies by {(price_std/avg_price*100):.1f}% on average."
        else:
            insights["pricing_insights"] = f"Stable pricing environment (avg: ${avg_price:.2f}). Consistent market with predictable costs."

        # Weekend premium analysis
        weekend_premium = price_analysis.get('weekend_premium', {})
        if weekend_premium.get('premium_percentage', 0) > 10:
            insights["pricing_insights"] += f" Weekend flights cost {weekend_premium.get('premium_percentage', 0):.1f}% more than weekdays."

        # Route recommendations
        popular_routes = route_analysis.get('popular_routes', [])[:3]
        if popular_routes:
            route_names = [route.get('route', '') for route in popular_routes]
            insights["route_recommendations"] = f"Focus on top routes: {', '.join(route_names)}. These show highest demand and flight frequency."
        else:
            insights["route_recommendations"] = "Analyze specific routes based on your target markets and customer preferences."

        # Business recommendations for hostels
        insights["business_recommendations"] = self._generate_business_recommendations(analysis)

        # Market outlook
        insights["market_outlook"] = self._generate_market_outlook(analysis)

        return insights

    def _generate_business_recommendations(self, analysis: Dict) -> str:
        """Generate specific recommendations for hostel business"""

        recommendations = []

        # Route-based recommendations
        route_analysis = analysis.get('route_analysis', {})
        popular_routes = route_analysis.get('popular_routes', [])

        if popular_routes:
            top_route = popular_routes[0]
            recommendations.append(f"Consider locations near {top_route.get('route', 'popular routes')} - highest flight volume detected.")

        # Pricing recommendations
        price_analysis = analysis.get('price_analysis', {})
        weekend_premium = price_analysis.get('weekend_premium', {})

        if weekend_premium.get('premium_percentage', 0) > 15:
            recommendations.append("Weekend travel shows significant price premiums - adjust hostel rates accordingly.")

        # Time-based recommendations
        time_analysis = analysis.get('time_analysis', {})
        avg_flights = time_analysis.get('avg_flights_per_day', 0)

        if avg_flights > 20:
            recommendations.append("High daily flight frequency indicates strong market - good opportunity for hostel business.")

        # General recommendations
        recommendations.extend([
            "Monitor price trends to optimize booking timing for your guests.",
            "Consider partnerships with airlines on popular routes.",
            "Offer flight booking assistance as a value-added service."
        ])

        return " ".join(recommendations)

    def _generate_market_outlook(self, analysis: Dict) -> str:
        """Generate market outlook based on data patterns"""

        summary_stats = analysis.get('summary', {})
        total_flights = summary_stats.get('total_flights', 0)
        unique_routes = summary_stats.get('unique_routes', 0)

        if total_flights > 200 and unique_routes > 5:
            return "Strong market outlook with diverse route options and high flight frequency. Excellent environment for travel-related businesses."
        elif total_flights > 100:
            return "Positive market outlook with good flight availability. Steady demand supports business growth opportunities."
        else:
            return "Developing market with growth potential. Monitor trends closely and focus on high-demand periods."

    def get_route_insights(self, route: str, data: Dict) -> Dict:
        """Get specific insights for a particular route"""

        # Filter data for specific route
        flights_data = data.get('flights_data', [])
        route_flights = [f for f in flights_data if f.get('route') == route]

        if not route_flights:
            return {"error": f"No data available for route {route}"}

        # Calculate route-specific metrics
        prices = [f['price'] for f in route_flights]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        insights = {
            "route": route,
            "flight_count": len(route_flights),
            "price_analysis": {
                "average": avg_price,
                "minimum": min_price,
                "maximum": max_price,
                "price_range": max_price - min_price
            },
            "recommendation": self._get_route_recommendation(route_flights, avg_price)
        }

        return insights

    def _get_route_recommendation(self, route_flights: List[Dict], avg_price: float) -> str:
        """Generate recommendation for a specific route"""

        flight_count = len(route_flights)

        if flight_count > 20:
            return f"High-demand route with {flight_count} flights. Average price ${avg_price:.2f}. Excellent for business travelers."
        elif flight_count > 10:
            return f"Popular route with {flight_count} flights. Average price ${avg_price:.2f}. Good market opportunity."
        else:
            return f"Emerging route with {flight_count} flights. Average price ${avg_price:.2f}. Monitor for growth potential."
