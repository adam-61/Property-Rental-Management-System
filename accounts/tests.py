from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile


class AuthAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'HavenHues Properties')

    def test_account_pages_titles(self):
        # Login page title
        res_login = self.client.get(reverse('login'))
        self.assertContains(res_login, '<title>Sign In | HavenHues Properties</title>')

        # Register page title
        res_reg = self.client.get(reverse('register'))
        self.assertContains(res_reg, '<title>Register | HavenHues Properties</title>')

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'Person',
            'email': 'newuser@example.com',
            'role': 'owner',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
        self.assertEqual(new_user.profile.role, 'owner')
        self.assertTrue(new_user.profile.is_owner)

    def test_user_login_and_logout(self):
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, Test!')

        # Logout
        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertContains(logout_response, 'You have been successfully logged out')

    def test_profile_update(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('profile'), {
            'username': 'testuser',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@example.com',
            'bio': 'Software Engineer and builder.',
            'location': 'San Francisco, CA',
            'phone': '+1 234 567 8900'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.profile.bio, 'Software Engineer and builder.')
        self.assertEqual(self.user.profile.location, 'San Francisco, CA')
        self.assertEqual(self.user.profile.phone, '+1 234 567 8900')
