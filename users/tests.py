from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AdminProfile, User

SIGNUP = {
    'full_name': 'Nusrat Jahan',
    'email': 'Nusrat@ULAB.edu.bd',
    'employee_id': 'EMP-1042',
    'department': 'Cafeteria',
    'password': 'lentil-soup-42',
}


class SignupTests(APITestCase):
    url = reverse('auth-signup')

    def test_creates_admin_with_profile_and_returns_tokens(self):
        res = self.client.post(self.url, SIGNUP, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        self.assertEqual(
            res.data['user'],
            {'id': res.data['user']['id'], 'email': 'nusrat@ulab.edu.bd', 'full_name': 'Nusrat Jahan', 'role': 'admin'},
        )
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertNotIn('password', res.data['user'])

        user = User.objects.get(email='nusrat@ulab.edu.bd')
        self.assertTrue(user.check_password('lentil-soup-42'))
        self.assertEqual(user.admin_profile.employee_id, 'EMP-1042')

    def test_department_is_optional(self):
        data = {**SIGNUP}
        del data['department']
        res = self.client.post(self.url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

    def test_rejects_duplicate_email_case_insensitively(self):
        self.client.post(self.url, SIGNUP, format='json')
        res = self.client.post(self.url, {**SIGNUP, 'email': 'nusrat@ulab.edu.bd', 'employee_id': 'EMP-2'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

    def test_rejects_duplicate_employee_id(self):
        self.client.post(self.url, SIGNUP, format='json')
        res = self.client.post(self.url, {**SIGNUP, 'email': 'other@ulab.edu.bd'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('employee_id', res.data)

    def test_rejects_weak_password(self):
        res = self.client.post(self.url, {**SIGNUP, 'password': '12345678'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', res.data)
        self.assertFalse(User.objects.exists())

    def test_requires_fields(self):
        res = self.client.post(self.url, {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ['full_name', 'email', 'employee_id', 'password']:
            self.assertIn(field, res.data)


class LoginTests(APITestCase):
    url = reverse('auth-login')

    def setUp(self):
        self.client.post(reverse('auth-signup'), SIGNUP, format='json')

    def test_returns_tokens_and_user(self):
        res = self.client.post(self.url, {'email': 'nusrat@ulab.edu.bd', 'password': 'lentil-soup-42'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['role'], 'admin')

    def test_email_is_case_insensitive(self):
        res = self.client.post(self.url, {'email': ' NUSRAT@ulab.edu.bd ', 'password': 'lentil-soup-42'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_wrong_password(self):
        res = self.client.post(self.url, {'email': 'nusrat@ulab.edu.bd', 'password': 'wrong'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data['detail'], 'Incorrect email or password.')

    def test_unknown_email_gives_same_error(self):
        res = self.client.post(self.url, {'email': 'nobody@ulab.edu.bd', 'password': 'whatever'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data['detail'], 'Incorrect email or password.')

    def test_inactive_user_cannot_log_in(self):
        User.objects.filter(email='nusrat@ulab.edu.bd').update(is_active=False)
        res = self.client.post(self.url, {'email': 'nusrat@ulab.edu.bd', 'password': 'lentil-soup-42'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenAndMeTests(APITestCase):
    def setUp(self):
        res = self.client.post(reverse('auth-signup'), SIGNUP, format='json')
        self.tokens = res.data

    def test_me_requires_token(self):
        res = self.client.get(reverse('auth-me'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")
        res = self.client.get(reverse('auth-me'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], 'nusrat@ulab.edu.bd')

    def test_refresh_gives_new_access_token(self):
        res = self.client.post(reverse('auth-token-refresh'), {'refresh': self.tokens['refresh']}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)

    def test_superuser_is_admin(self):
        user = User.objects.create_superuser(email='Root@ULAB.edu.bd', password='x', full_name='Root')
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertEqual(user.email, 'root@ulab.edu.bd')
        self.assertFalse(AdminProfile.objects.filter(user=user).exists())
