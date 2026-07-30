import unittest

from app import app, extract_location_details


class SkyCastTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_empty_city_shows_error(self):
        response = self.client.post("/", data={"city": "   "}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter a city name", response.data)

    def test_extract_location_details_falls_back_to_display_name(self):
        location = {
            "display_name": "Karnataka, India",
            "address": {"state": "Karnataka"},
        }
        details = extract_location_details(location)
        self.assertEqual(details["city"], "Karnataka")
        self.assertEqual(details["country"], "India")


if __name__ == "__main__":
    unittest.main()
