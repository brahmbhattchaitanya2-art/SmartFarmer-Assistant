from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

class LeafScannerViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testfarmer', password='password123')
        self.scan_url = reverse('leaf_scanner:scan')

    def test_scan_view_requires_login(self):
        response = self.client.get(self.scan_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_scan_view_accessible_after_login(self):
        self.client.login(username='testfarmer', password='password123')
        response = self.client.get(self.scan_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaf_scanner/scan.html')

    @patch('os.path.exists')
    def test_scan_view_shows_alert_when_model_missing(self, mock_exists):
        # Force os.path.exists to return False to simulate missing model
        mock_exists.return_value = False
        self.client.login(username='testfarmer', password='password123')
        response = self.client.get(self.scan_url)
        self.assertEqual(response.status_code, 200)
        # Should inform the user that the model is missing/needs training
        self.assertContains(response, "Classifier Model is Missing")
