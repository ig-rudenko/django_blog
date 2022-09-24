from django_blog.celery import app
import time
from functools import reduce
from faker import Faker
from django.contrib.auth import get_user_model
from .models import Post
from django.contrib.auth.hashers import make_password

User = get_user_model()


@app.task(bind=True, autoretry_for=(ValueError,),
          retry_kwargs={'max_retries': 5, 'countdown': 5})
def add(self, x, y):
    time.sleep(2)
    return int(x) + int(y)


@app.task
def xsum(n):
    return sum(n)


@app.task
def factorial(n):
    time.sleep(5)
    return reduce(lambda x, y: x*y, range(1, int(n)+1))


@app.task
def ssum(n):
    time.sleep(5)
    return reduce(lambda x, y: x+y, range(1, int(n)+1))


@app.task
def div(x, y):
    time.sleep(20)
    return int(x) / int(y)


@app.task(ignore_result=True)
def fake_user():
    f = Faker('ru_RU')
    p = f.profile()
    User.objects.create(
        username=p['username'],
        email=p['mail'],
        password=make_password(f.password(length=8)),
    )


@app.task(ignore_result=True)
def fake_post(user_id):
    f = Faker('ru_RU')
    Post.objects.create(
        title=f.sentence(nb_words=5),
        content=f.sentence(nb_words=500),
        date=f.date_time_between(),
        user_id=user_id
    )
