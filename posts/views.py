import datetime

from django.shortcuts import render, redirect

from django.http import HttpResponseNotAllowed, HttpResponseNotFound
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .forms import PostCreateForm

from faker import Faker
from posts import models


def fake_create_user(request):
    f = Faker('ru_RU')
    for i in range(100):
        print(i)
        p = f.profile()
        User.objects.create(
            username=p['username'],
            email=p['mail'],
            password=f.password(length=8)
        )
    return redirect('/')


def fake_create_posts(request):
    f = Faker('ru_RU')
    users = User.objects.all()

    for u in users:
        models.Post.objects.bulk_create(
            [
                models.Post(
                    title=f.sentence(nb_words=5),
                    content=f.sentence(nb_words=100),
                    date=f.date_time_between(),
                    user=u
                ) for _ in range(10000)
            ]
        )
        print(u.username)
    return redirect('/')


def profile(request, user_name):
    try:
        p = int(request.GET.get('p', 1))
    except ValueError:
        p = 1

    try:
        user_profile = models.Profile.objects.get(user__username=user_name)
        posts = models.Post.objects.filter(user__username=user_name).order_by('-date')
        pages = Paginator(posts, 100)
        return render(
            request,
            'registration/profile.html',
            {
                'profile': user_profile,
                'posts': pages.page(p),
                'page': p,
                'num_pages': int(pages.num_pages)
            }
        )

    except (User.DoesNotExist, models.Profile.DoesNotExist):
        return redirect('home')


def show_posts(request):
    posts_limit = 50

    print(request.GET)
    try:
        p = int(request.GET.get('p', 1))
    except ValueError:
        p = 1

    if request.GET.get('d'):
        date = datetime.datetime.strptime(request.GET['d'], '%Y-%m-%d')
        date_to = date + datetime.timedelta(days=10)

        date_query = (Q(date__gte=date) & Q(date__lt=date_to))

    else:
        date_query = Q()

    if request.GET.get('s'):
        s = request.GET['s']

        q1 = models.Post.objects.filter(
            date_query & Q(title__contains=s) & ~Q(content__contains=s)
        ).order_by('-date')

        print(q1.query)

        q2 = models.Post.objects.filter(
            date_query & ~Q(title__contains=s) & Q(content__contains=s)
        ).order_by('-date')

        pages = Paginator(list(q1) + list(q2), posts_limit)

    else:
        q = models.Post.objects.filter(date_query).order_by('-date').all()
        print(q.query)
        pages = Paginator(q, posts_limit)

    if p > pages.num_pages:
        p = pages.num_pages
    if p < 1:
        p = 1
    print(pages.count)
    return render(
        request, 'posts/posts.html',
        {
            'posts': pages.page(p),
            'search_str': request.GET.get('s', ''),
            'page': p,
            'num_pages': int(pages.num_pages),
        }
    )


def update_post(request, post_id):
    print('UPDATE FUNC')

    try:
        user_post = models.Post.objects.get(id=post_id)

        if request.user != user_post.user and not request.user.is_superuser:  # Нельзя редактировать пост другого пользователя
            return HttpResponseNotAllowed(request)

    except models.Post.DoesNotExist:
        return HttpResponseNotFound(request)

    if request.method == 'GET':
        return render(request, 'posts/create.html',
                      {'title': user_post.title, 'content': user_post.content, 'delete': True, 'post_id': post_id})

    elif request.method == 'POST':
        print(request.POST)

        # Переопределяем переменные, если их нет, то пустая строка
        title = request.POST.get('title') or ''
        content = request.POST.get('content') or ''

        if title and content:  # Проверяем все ли данные ввел пользователь
            # Создаем экземпляр класса Post
            update_fields = []

            if user_post.title != title:
                update_fields.append('title')
                user_post.title = title

            if user_post.content != content:
                update_fields.append('content')
                user_post.content = content

            return redirect('/posts')

        else:  # Если пользователь ввел не все данные
            error = 'Укажите все поля!'
            return render(request, 'posts/create.html',
                          {'title': title, 'content': content, 'error': error, 'delete': True, 'post_id': post_id}
                          )


def delete(request, post_id):
    if request.method == 'POST':
        try:
            models.Post.objects.get(id=post_id).delete()
            return redirect('/posts/')
        except models.Post.DoesNotExist:
            return HttpResponseNotFound(request)
    else:
        return HttpResponseNotAllowed(request)


def post(request, post_id):
    try:
        user_post = models.Post.objects.get(id=post_id)
        author = user_post.user.username

        return render(request, 'posts/user_post.html', {'post': user_post, 'user': author})
    except models.Post.DoesNotExist:
        return HttpResponseNotFound(request)


def create_post(request):
    user_form = PostCreateForm()

    print('CREATE FUNC')
    if request.method == 'GET':
        return render(request, 'posts/create_2.html', {'form': user_form})

    elif request.method == 'POST':
        print(request.POST)

        user_form = PostCreateForm(request.POST, request.FILES)

        if user_form.is_valid():  # Проверяем все ли данные ввел пользователь
            models.Post.objects.create(
                title=user_form.cleaned_data['title'],
                content=user_form.cleaned_data['content'],
                image=user_form.cleaned_data['image'],
                user=User.objects.get(username=request.user.username)
            )
            return redirect('/')

        else:  # Если пользователь ввел не все данные
            return render(request, 'posts/create_2.html', {'form': user_form})
