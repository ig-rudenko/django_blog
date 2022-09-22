import re

from django.test import TestCase
from registration.tasks import render_message
from django.contrib.auth.models import User
from django.core import mail


class RenderMessageTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = User(username='test_user', is_active=False, email='test@mail.com')
        u.set_password('password')
        u.save()

    def test_send_email(self):
        user = User.objects.get(username='test_user')
        mail_subject, message, user_email = render_message(
            current_site_domain='example.com',
            user_id=user.id,
            template='registration/email_confirm.html'
        )

        self.assertEqual(user_email, user.email)

        mail.send_mail(
            subject=mail_subject,
            message=message,
            from_email='from@mail.com',
            recipient_list=[user_email]
        )

        self.assertTrue(mail.outbox)

        self.assertEqual(mail.outbox[0].subject, 'Ссылка на активацию аккаунта на сайте example.com')

        accept_message = mail.outbox[0].body

        # /registration/activate/MQ/bbgd7k-39d3b165ed31291da9186c081e68c319/
        url = re.findall(
            r'href="http:\/\/example\.com(\/registration\/activate\S+)\"',
            accept_message
        )

        self.assertTrue(url)

        resp = self.client.get(url[0])

        self.assertEqual(resp.status_code, 200)

        user = User.objects.get(username='test_user')

        self.assertTrue(user.is_active)

