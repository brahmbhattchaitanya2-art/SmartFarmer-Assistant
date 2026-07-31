from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.forms import FarmerRegistrationForm
from core.models import UserProfile

class RegistrationTestCase(TestCase):
    def test_registration_form_no_primary_crop_field(self):
        """Test that primary_crop is not in the form fields."""
        form = FarmerRegistrationForm()
        self.assertNotIn('primary_crop', form.fields)

    def test_registration_form_validation_and_save(self):
        """Test that the registration form is valid and saves profile with default primary_crop."""
        form_data = {
            'username': 'testfarmer',
            'first_name': 'Ramesh',
            'last_name': 'Kumar',
            'email': 'ramesh@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '9876543210',
            'village': 'Rampur',
            'district': 'Patiala',
            'state': 'PB',
            'land_size': '5.5',
        }
        form = FarmerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        user = form.save()
        
        # Verify user model fields
        self.assertEqual(user.username, 'testfarmer')
        self.assertEqual(user.first_name, 'Ramesh')
        self.assertEqual(user.last_name, 'Kumar')
        self.assertEqual(user.email, 'ramesh@example.com')
        
        # Verify user profile was created and has default primary_crop
        self.assertTrue(hasattr(user, 'profile'))
        profile = user.profile
        self.assertEqual(profile.phone_number, '9876543210')
        self.assertEqual(profile.village, 'Rampur')
        self.assertEqual(profile.district, 'Patiala')
        self.assertEqual(profile.state, 'PB')
        self.assertEqual(profile.primary_crop, 'Not Specified')
        self.assertEqual(float(profile.land_size), 5.5)

    def test_registration_view_get(self):
        """Test that GET request to register page works and does not contain primary_crop input."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="primary_crop"')
        self.assertNotContains(response, 'Primary Crop *')

    def test_registration_view_post_success(self):
        """Test that submitting valid registration data succeeds and redirects to dashboard."""
        post_data = {
            'username': 'testfarmer2',
            'first_name': 'Suresh',
            'last_name': 'Kumar',
            'email': 'suresh@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '9876543210',
            'village': 'Rampur',
            'district': 'Patiala',
            'state': 'PB',
            'land_size': '10.0',
        }
        response = self.client.post(reverse('register'), data=post_data)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Check that user and profile were created
        user = User.objects.get(username='testfarmer2')
        self.assertEqual(user.profile.primary_crop, 'Not Specified')

