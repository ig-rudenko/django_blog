from django_blog.celery import app
import time


@app.task
def add(x, y):
    time.sleep(20)
    return int(x) + int(y)


@app.task
def mul(x, y):
    time.sleep(20)
    return int(x) * int(y)


@app.task
def sub(x, y):
    time.sleep(20)
    return int(x) - int(y)


@app.task
def div(x, y):
    time.sleep(20)
    return int(x) / int(y)
