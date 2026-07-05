from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CustomUserModelTests(TestCase):
    def test_create_user_with_role(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='password123',
            role='student',
        )

        self.assertEqual(user.role, 'student')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_signup_page_renders(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create an account')

    def test_login_redirects_admin_to_admin_site(self):
        User = get_user_model()
        User.objects.create_superuser(username='admin', email='admin@example.com', password='password123', role='admin')

        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'password123'},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:index'))

    def test_logout_redirects_to_home(self):
        User = get_user_model()
        user = User.objects.create_user(username='student', email='student@example.com', password='password123', role='student')
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
