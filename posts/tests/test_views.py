from django.test import TestCase
from posts import models
from django.contrib.auth.models import User


class CreatePostTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = User(username='test_user')
        u.set_password('password')
        u.save()

    def test_create_post(self):
        self.client.login(username='test_user', password='password')
        resp = self.client.post(
            '/posts/create',
            data={
                'title': 'Title',
                'content': '<p>Content</p>'
            },
            follow=True
        )

        post = models.Post.objects.get(title='Title')
        self.assertEqual(post.content, '<p>Content</p>')
        self.assertTrue(post.user)

        self.assertRedirects(
            resp,
            f'/posts/{post.id}'
        )
        resp = self.client.get(f'/posts/{post.id}')

        self.assertEqual(resp.status_code, 200)

    def test_delete_post(self):
        self.client.login(username='test_user', password='password')
        resp = self.client.post(
            '/posts/create',
            data={
                'title': 'Title',
                'content': '<p>Content</p>'
            },
            follow=True
        )

        post = models.Post.objects.get(title='Title')

        resp = self.client.post(
            f'/posts/delete/{post.id}'
        )
        self.assertRedirects(
            resp,
            '/'
        )

        with self.assertRaises(models.Post.DoesNotExist):
            post = models.Post.objects.get(title='Title')
