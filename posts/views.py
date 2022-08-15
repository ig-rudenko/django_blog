import datetime
from faker import Faker

from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, HttpResponseNotFound
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import PostModelForm
from .paginator import LargeTablePaginator, CachedPaginator
from .api.serializers import PostsModelSerializer
from posts import models

from rest_framework.decorators import api_view
from rest_framework.views import Response
from rest_framework import status

from django.views.decorators.cache import cache_page
from .tasks import add, sub, mul, div
from celery.result import AsyncResult


def task(request):
    opt = request.GET.get('opt')
    x = request.GET.get('x')
    y = request.GET.get('y')
    res = add(x, y)
    return Response(res)


def get_task(request, uuid: str):
    res = AsyncResult(uuid)
    return Response(f'{res}<br>{res.status}<br>{res.result}')


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
        print(user_name, models.Profile.objects.all())
        user_profile = models.Profile.objects.get(user__username=user_name)
        print(user_profile)
        posts = models.Post.objects.filter(user__username=user_name).order_by('-date')
        print(posts)
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


def delete(request, post_id):
    if request.method == 'POST':
        try:
            models.Post.objects.get(id=post_id).delete()
            return redirect('/posts/')
        except models.Post.DoesNotExist:
            return HttpResponseNotFound(request)
    else:
        return HttpResponseNotAllowed(request)


@cache_page(60 * 10)
def post(request, post_id):
    try:
        user_post = models.Post.objects.get(id=post_id)
        author = user_post.user.username
        print(user_post.image)
        return render(request, 'posts/user_post.html', {'post': user_post, 'user': author})
    except models.Post.DoesNotExist:
        return HttpResponseNotFound(request)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = models.Post
    form_class = PostModelForm
    template_name = 'posts/create_2.html'

    def form_valid(self, form):
        r = super(PostCreateView, self).form_valid(form)
        self.object.user = self.request.user
        self.object.save()
        print(self.object, self.object.user)
        return r


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = models.Post
    form_class = PostModelForm
    success_url = '/posts/{id}'
    template_name = 'posts/update.html'
    permission_denied_message = 'Нет доступа к редактированию данного поста!'

    def test_func(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        post_user_id = models.Post.objects.filter(id=pk).values('user_id').first()['user_id']
        return self.request.user.id == post_user_id


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Post
    success_url = '/'


class PostShowView(ListView):
    model = models.Post
    paginate_by = 100
    template_name = 'posts/posts.html'
    context_object_name = 'posts'
    ordering = ('-date',)
    page_kwarg = 'p'

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        # Имя для кеша
        cache_name = f'{self.model.__name__}{self.request.GET.get("d", "")}{self.request.GET.get("s", "")}'
        # Возвращаем paginator
        return CachedPaginator(queryset, per_page, orphans, allow_empty_first_page, cache_name)

    def get_queryset(self):
        if self.request.GET.get('d'):
            date = datetime.datetime.strptime(self.request.GET['d'], '%Y-%m-%d')
            date_to = date + datetime.timedelta(days=1)
            date_query = (Q(date__gte=date) & Q(date__lt=date_to))
        else:
            date_query = Q()

        if self.request.GET.get('s'):
            s = self.request.GET['s']
            q1 = models.Post.objects.filter(
                date_query & Q(title__contains=s) & ~Q(content__contains=s)
            ).order_by('-date')
            q2 = models.Post.objects.filter(
                date_query & ~Q(title__contains=s) & Q(content__contains=s)
            ).order_by('-date')

            q = q1 | q2

        else:
            q = models.Post.objects.filter(date_query).order_by('-date').all().values('id', 'title', 'user', 'date')
            print(q.query)
        return q


@api_view(['GET', 'POST'])
def posts_api(request):
    print(request.user, request.data)
    if request.method == 'GET':
        posts = models.Post.objects.all()[:100]
        serializer = PostsModelSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST' and not request.user.is_anonymous:
        serializer = PostsModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'detail': 'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def posts_api_m(request, pk):
    try:
        post = models.Post.objects.get(id=pk)
    except models.Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        s = PostsModelSerializer(post)
        return Response(s.data)

    elif request.method == 'PUT':
        s = PostsModelSerializer(post, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
