from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from cbt.models import Option, Question


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

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse('password_reset'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset password')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_email_for_existing_account(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='password123',
            role='student',
        )

        response = self.client.post(reverse('password_reset'), {'email': user.email})

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password reset', mail.outbox[0].subject)

    def test_dashboard_shows_verify_email_button_for_unverified_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='student3',
            email='student3@example.com',
            password='password123',
            role='student',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('student_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verify your email')

    def test_dashboard_shows_verified_state_for_verified_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='student4',
            email='student4@example.com',
            password='password123',
            role='student',
        )
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        self.client.force_login(user)

        response = self.client.get(reverse('student_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verified')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_request_verification_email_sends_message(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='student4',
            email='student4@example.com',
            password='password123',
            role='student',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('request_email_verification'))

        self.assertRedirects(response, reverse('student_dashboard'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify your email', mail.outbox[0].subject)

    def test_freemium_user_is_redirected_to_subscription_page_for_mock_exam(self):
        User = get_user_model()
        user = User.objects.create_user(username='student5', email='student5@example.com', password='password123', role='student')
        self.client.force_login(user)

        response = self.client.get(reverse('cbt_test'), {'mode': 'mock'})

        self.assertRedirects(response, reverse('subscription_page'))

    def test_premium_user_can_access_mock_exam_with_plan_limit(self):
        User = get_user_model()
        user = User.objects.create_user(username='student6', email='student6@example.com', password='password123', role='student')
        user.subscription_status = 'premium'
        user.subscription_plan = 'basic'
        user.save(update_fields=['subscription_status', 'subscription_plan'])
        self.client.force_login(user)

        question = Question.objects.create(text='What is nursing?', category=Question.Category.FUNDAMENTALS_OF_NURSING)
        Option.objects.create(
            question=question,
            option_a='A',
            option_b='B',
            option_c='C',
            option_d='D',
            correct_option='a',
            rationale='Because it is correct.',
        )

        response = self.client.get(reverse('cbt_test'), {'mode': 'mock'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily Limit')
        self.assertContains(response, '50')
