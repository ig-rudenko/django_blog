from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

User = get_user_model()


class UserLoginTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = User(username='test_user')
        u.set_password('password')
        u.save()

    def test_access_login_url(self):
        self.assertEqual(reverse('login'), '/accounts/login/')
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_no_login(self):
        resp = self.client.get('/posts/create')
        self.assertRedirects(
            resp,
            expected_url='/accounts/login/?next=/posts/create'
        )

    def test_login(self):
        self.client.login(username='test_user', password='password')
        resp = self.client.get('/posts/create')
        self.assertEqual(resp.status_code, 200)
