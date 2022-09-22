from django_blog.celery import app
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives


def render_message(current_site_domain: str, user_id: int, template: str):
    mail_subject = 'Ссылка на активацию аккаунта на сайте ' + current_site_domain
    user = User.objects.get(id=user_id)

    message = render_to_string(
        template,
        {
            'user': user,
            'domain': current_site_domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        }
    )
    return mail_subject, message, user.email


@app.task(ignore_result=True)
def send_email(current_site_domain: str, user_id: int, template: str):
    # Письмо пользователю (текст)

    mail_subject, message, user_email = render_message(current_site_domain, user_id, template)

    email = EmailMultiAlternatives(
        mail_subject, message, to=[user_email]
    )
    email.attach_alternative(message, "text/html")  # Тип данных - html
    email.send()  # Отправка письма


@app.task(ignore_result=True)
def delete_user(user_id: int):
    user = User.objects.get(id=user_id)
    if not user.is_active:
        user.delete()
