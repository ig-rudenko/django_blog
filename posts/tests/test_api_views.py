from django.test import TestCase
from django.contrib.auth import get_user_model
from posts import models

User = get_user_model()


class GetTokenTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = User(username='test_user')
        u.set_password('password')
        u.save()

    def test_get_tokens(self):
        resp = self.client.post(
            '/api/token/',
            {
                'username': 'test_user',
                'password': 'password'
            }
        )

        data: dict = resp.json()

        self.assertEqual(len(data), 2)
        self.assertTrue(data.get('refresh'))
        self.assertTrue(data.get('access'))


class CreatePostTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = User(username='test_user')
        u.set_password('password')
        u.save()

    def setUp(self) -> None:
        self.tokens = self.client.post(
            '/api/token/',
            {
                'username': 'test_user',
                'password': 'password'
            }
        ).json()

    def test_create_post(self):
        resp = self.client.post(
            '/api/posts',
            {
                'title': 'Title',
                'content': 'Content'
            },
            HTTP_AUTHORIZATION=f'Bearer {self.tokens["access"]}'
        )

        self.assertEqual(resp.status_code, 201)

        post = models.Post.objects.get(title='Title')
        user = User.objects.get(username='test_user')

        expect_response = {
            "id": post.id,
            "date": post.date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "user": {
                "id": user.id,
                "username": "test_user",
                "email": "",
                "phone": None,
                "address": None,
                "hobby": None
            },
            "url": f"/posts/{post.id}",
            "title": "Title",
            "content": "Content",
            "image": None
        }

        print(resp.json())

        self.assertEqual(
            expect_response,
            resp.json()
        )
