#!/usr/bin/env python3
"""
Start the Airline Market Analyzer Flask server
"""

import os
import sys

# Set environment variables
os.environ['FLASK_DEBUG'] = 'True'
os.environ['FLASK_ENV'] = 'development'

# Import Flask app
from app import app

if __name__ == '__main__':
    print("🚀 Starting Airline Market Analyzer...")
    print("📊 Access the application at: http://localhost:5000")
    print("✨ Press Ctrl+C to stop\n")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
