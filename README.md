# Airline Booking Market Demand Analysis Web App

A comprehensive web application for analyzing airline booking market demand trends, designed to help hostels and travel businesses understand market dynamics.

## Features

- **Data Collection**: Scrapes airline booking data from multiple sources
- **AI-Powered Insights**: Uses OpenAI API to analyze trends and patterns
- **Interactive Visualizations**: Charts and graphs for easy data interpretation
- **User-Friendly Interface**: Simple web interface for non-technical users
- **Real-time Analysis**: Fresh data collection and processing

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd airline-demand-analyzer
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Web App**
   Open your browser to `http://localhost:5000`

## API Keys Required

- **OpenAI API**: For generating insights and analysis
- **RapidAPI**: For accessing flight data APIs
- **Amadeus API** (optional): Alternative flight data source

## Project Structure

```
airline-demand-analyzer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── src/                  # Core application modules
│   ├── data_collector.py # Data scraping and API integration
│   ├── data_processor.py # Data cleaning and analysis
│   ├── api_integrator.py # AI API integration
│   └── visualizer.py     # Chart and graph generation
├── templates/            # HTML templates
├── static/              # CSS, JS, and images
└── data/               # Data storage and cache
```

## Usage

1. **Search Flights**: Enter origin, destination, and date range
2. **View Results**: See processed data with insights and visualizations
3. **Analyze Trends**: Explore popular routes and pricing patterns
4. **Export Data**: Download results for further analysis

## Development

- Built with Flask for the web framework
- Uses BeautifulSoup and Selenium for web scraping
- Integrates with OpenAI for intelligent analysis
- Plotly for interactive visualizations
- Responsive design for mobile and desktop

## License

MIT License - see LICENSE file for details
