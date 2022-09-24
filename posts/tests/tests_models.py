from django.test import TestCase
from posts import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PostsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        print('setUpTestData')
        u = User(username='test_user')
        u.set_password('password')
        u.save()

        models.Post.objects.create(
            title='Title',
            content='Content'
        )

    def test_model_post_max_length(self):
        post = models.Post.objects.get(title='Title')
        max_length = post._meta.get_field('title').max_length

        self.assertEqual(max_length, 100)

    def test_post_get_absolute_url(self):
        post = models.Post.objects.get(title='Title')

        self.assertEqual(
            post.get_absolute_url(),
            f'/posts/{post.id}'
        )

    def test_post_str(self):
        post = models.Post.objects.get(title='Title')

        self.assertEqual(
            str(post),
            'Post: Title'
        )
