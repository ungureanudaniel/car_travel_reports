import unittest
from kivy.app import App
from core.main import CarReportApp
import os
import pdb; pdb.set_trace()


class TestCarReportApp(unittest.TestCase):

    def setUp(self):
        """Create an instance of the app before each test."""
        self.app = CarReportApp()
        self.app.build()  # Build the app's UI
        
        # Set the relative path for the test CSV file
        self.test_file_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_files', 'Foaie parcurs_B51JFF_apr_2024.csv')

    def test_fuel_input_conversion(self):
        """Test the conversion of fuel input to float."""
        self.app.fuel_float_input.text = "12.50"
        converted_value = float(self.app.fuel_float_input.text)
        self.assertEqual(converted_value, 12.50)

    def test_invalid_fuel_input(self):
        """Test handling of invalid fuel input."""
        self.app.fuel_float_input.text = "invalid"
        with self.assertRaises(ValueError):
            float(self.app.fuel_float_input.text)  # This will raise a ValueError

    def test_csv_file_selection(self):
        """Test the CSV file selection functionality."""
        self.app._set_csv_path([self.test_file_path])
        self.assertEqual(self.app.csv_file_path, self.test_file_path)
        self.assertEqual(self.app.file_path_label.text, f"Fișier selectat: {self.test_file_path}")

    def test_generate_report_with_invalid_pdf_path(self):
        """Test the report generation with an invalid PDF path."""
        self.app.pdf_save_path = None  # Simulate no PDF path
        self.app.generate_report()  # Call the report generation method
        self.assertIn("Nu ați selectat încă locul de salvare.", self.app.status_label.text)

if __name__ == '__main__':
    unittest.main()
