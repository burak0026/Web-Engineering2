from API_functions import API_functions
import unittest

class TestApp(unittest.TestCase):
    """Unit tests defined for app.py"""

    def test_status(self):
        """Test return backwards simple string"""
        response=API_functions.reservations_status()
        self.assertEqual(200, response.status_code)

if __name__ == "__main__":
    unittest.main()