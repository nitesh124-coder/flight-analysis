"""
Airline Booking Market Demand Analysis Web App
Main Flask application entry point
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

# Import our custom modules
from src.data_collector import DataCollector
from src.data_processor import DataProcessor
from src.api_integrator import APIIntegrator
from src.visualizer import DataVisualizer

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Jinja helper: safe_url_for to avoid BuildError if route missing
@app.context_processor
def utility_processor():
    def safe_url_for(endpoint, **values):
        try:
            return url_for(endpoint, **values)
        except Exception:
            return '#'
    return dict(safe_url_for=safe_url_for)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize our modules
data_collector = DataCollector()
data_processor = DataProcessor()
api_integrator = APIIntegrator()
visualizer = DataVisualizer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search and filter page"""
    if request.method == 'POST':
        # Get form data
        origin = request.form.get('origin', '')
        destination = request.form.get('destination', '')
        date_from = request.form.get('date_from', '')
        date_to = request.form.get('date_to', '')
        
        # Redirect to results with parameters
        return redirect(url_for('results', 
                              origin=origin, 
                              destination=destination,
                              date_from=date_from,
                              date_to=date_to))
    
    return render_template('search.html')

@app.route('/results')
def results():
    """Results page showing analysis and visualizations"""
    # Get query parameters
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    try:
        # Collect data based on search parameters
        raw_data = data_collector.collect_flight_data(origin, destination, date_from, date_to)
        
        # Process the data
        processed_data = data_processor.process_data(raw_data)
        
        # Get AI insights
        insights = api_integrator.get_insights(processed_data)
        
        # Generate visualizations
        charts = visualizer.create_charts(processed_data)
        
        return render_template('results.html', 
                             data=processed_data,
                             insights=insights,
                             charts=charts,
                             search_params={
                                 'origin': origin,
                                 'destination': destination,
                                 'date_from': date_from,
                                 'date_to': date_to
                             })
    
    except Exception as e:
        logger.error(f"Error processing results: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/api/data')
def api_data():
    """API endpoint for getting processed data"""
    try:
        # Get sample data for demonstration
        sample_data = data_processor.get_sample_data()
        return jsonify(sample_data)
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/trends')
def trends():
    """Trends analysis page"""
    try:
        # Get trending routes and insights
        trending_data = data_processor.get_trending_routes()
        price_trends = data_processor.get_price_trends()
        
        return render_template('trends.html', 
                             trending_routes=trending_data,
                             price_trends=price_trends)
    except Exception as e:
        logger.error(f"Error loading trends: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/about')
def about():
    """About page"""
    year = datetime.now().year
    return render_template('about.html', current_year=year)

@app.route('/demo')
def demo():
    """UI Demo page showcasing enhanced features"""
    return render_template('demo.html')

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Run the app
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
