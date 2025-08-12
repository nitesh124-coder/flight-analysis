#!/usr/bin/env python3
"""
Simple script to run the Airline Market Analyzer Flask application
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
if __name__ == '__main__':
    from app import app
    print("🚀 Starting Airline Market Analyzer...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔍 Search flights at: http://localhost:5000/search")
    print("📈 View trends at: http://localhost:5000/trends")
    print("\n✨ Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
