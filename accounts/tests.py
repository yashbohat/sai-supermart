from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.password = 'strongpass123'
        self.user = self.user_model.objects.create_user(
            email='existing@example.com',
            password=self.password,
            first_name='Existing',
        )

    def test_signup_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {
                'name': 'Sai Shopper',
                'email': 'shopper@example.com',
                'password1': 'complexpass123',
                'password2': 'complexpass123',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('products:home'))
        user = self.user_model.objects.get(email='shopper@example.com')
        self.assertEqual(user.first_name, 'Sai Shopper')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_requires_unique_email(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {
                'name': 'Duplicate User',
                'email': self.user.email,
                'password1': 'complexpass123',
                'password2': 'complexpass123',
            },
        )

        self.assertContains(response, 'An account with this email already exists.')

    def test_login_uses_email_and_password_only(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': self.user.email, 'password': self.password},
            follow=True,
        )

        self.assertRedirects(response, reverse('products:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
