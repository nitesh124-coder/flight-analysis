"""
Basic tests for the Airline Market Analyzer application
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collector import DataCollector
from data_processor import DataProcessor
from api_integrator import APIIntegrator
from visualizer import DataVisualizer

class TestDataCollector(unittest.TestCase):
    """Test the DataCollector class"""
    
    def setUp(self):
        self.collector = DataCollector()
    
    def test_generate_sample_data(self):
        """Test sample data generation"""
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = self.collector._generate_sample_data('SYD', 'MEL', today, next_week)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check first flight data structure
        if data:
            flight = data[0]
            self.assertIn('price', flight)
            self.assertIn('origin', flight)
            self.assertIn('destination', flight)
            self.assertIn('date', flight)
    
    def test_collect_flight_data(self):
        """Test flight data collection"""
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = self.collector.collect_flight_data('SYD', 'MEL', today, next_week)
        
        self.assertIsInstance(data, dict)
        self.assertIn('flights', data)
        self.assertIn('search_params', data)
        self.assertIn('market_data', data)

class TestDataProcessor(unittest.TestCase):
    """Test the DataProcessor class"""
    
    def setUp(self):
        self.processor = DataProcessor()
        
        # Create sample data for testing
        self.sample_data = {
            'flights': [
                {'price': 150, 'origin': 'SYD', 'destination': 'MEL', 'date': '2024-01-01', 'airline': 'Qantas'},
                {'price': 180, 'origin': 'SYD', 'destination': 'MEL', 'date': '2024-01-02', 'airline': 'Virgin'},
                {'price': 160, 'origin': 'SYD', 'destination': 'MEL', 'date': '2024-01-03', 'airline': 'Jetstar'},
            ]
        }
    
    def test_process_data(self):
        """Test data processing"""
        result = self.processor.process_data(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('analysis', result)
        self.assertIn('flights_data', result)
        self.assertIn('total_flights', result)
    
    def test_get_sample_data(self):
        """Test sample data retrieval"""
        data = self.processor.get_sample_data()
        
        self.assertIsInstance(data, dict)
        self.assertIn('popular_routes', data)
        self.assertIn('price_trends', data)

class TestAPIIntegrator(unittest.TestCase):
    """Test the APIIntegrator class"""
    
    def setUp(self):
        self.integrator = APIIntegrator()
        
        # Sample processed data
        self.sample_processed_data = {
            'analysis': {
                'summary': {
                    'total_flights': 100,
                    'price_range': {'avg': 175, 'min': 120, 'max': 250}
                },
                'route_analysis': {
                    'popular_routes': [
                        {'route': 'SYD-MEL', 'flight_count': 45, 'avg_price': 165}
                    ]
                }
            }
        }
    
    def test_get_insights(self):
        """Test insights generation"""
        insights = self.integrator.get_insights(self.sample_processed_data)
        
        self.assertIsInstance(insights, dict)
        self.assertIn('source', insights)
        self.assertIn('generated_at', insights)
    
    def test_rule_based_insights(self):
        """Test rule-based insights generation"""
        insights = self.integrator._generate_rule_based_insights(self.sample_processed_data)
        
        self.assertIsInstance(insights, dict)
        self.assertIn('demand_trends', insights)
        self.assertIn('pricing_insights', insights)

class TestDataVisualizer(unittest.TestCase):
    """Test the DataVisualizer class"""
    
    def setUp(self):
        self.visualizer = DataVisualizer()
        
        # Sample processed data
        self.sample_data = {
            'flights_data': [
                {'price': 150, 'date': '2024-01-01', 'airline': 'Qantas'},
                {'price': 180, 'date': '2024-01-02', 'airline': 'Virgin'},
            ],
            'analysis': {
                'summary': {
                    'total_flights': 2,
                    'price_range': {'avg': 165, 'min': 150, 'max': 180}
                },
                'price_analysis': {
                    'by_day_of_week': {'Monday': 150, 'Tuesday': 180}
                }
            }
        }
    
    def test_create_charts(self):
        """Test chart creation"""
        charts = self.visualizer.create_charts(self.sample_data)
        
        self.assertIsInstance(charts, dict)
        # Charts should be created even if data is limited
        self.assertGreater(len(charts), 0)
    
    def test_create_summary_metrics(self):
        """Test summary metrics creation"""
        metrics = self.visualizer.create_summary_metrics(self.sample_data)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_flights', metrics)
        self.assertIn('avg_price', metrics)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def test_complete_workflow(self):
        """Test the complete data processing workflow"""
        # Initialize components
        collector = DataCollector()
        processor = DataProcessor()
        integrator = APIIntegrator()
        visualizer = DataVisualizer()
        
        # Collect data
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        raw_data = collector.collect_flight_data('SYD', 'MEL', today, next_week)
        self.assertIsInstance(raw_data, dict)
        
        # Process data
        processed_data = processor.process_data(raw_data)
        self.assertIsInstance(processed_data, dict)
        
        # Generate insights
        insights = integrator.get_insights(processed_data)
        self.assertIsInstance(insights, dict)
        
        # Create visualizations
        charts = visualizer.create_charts(processed_data)
        self.assertIsInstance(charts, dict)
        
        print("✅ Complete workflow test passed!")

def run_tests():
    """Run all tests"""
    print("🧪 Running Airline Market Analyzer Tests...\n")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataCollector,
        TestDataProcessor,
        TestAPIIntegrator,
        TestDataVisualizer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️ Some tests failed!")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
