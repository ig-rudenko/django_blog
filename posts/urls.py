from django.urls import path
from posts import views as posts_views


urlpatterns = [
    path('', posts_views.show_posts, name='show_posts'),

    path('create', posts_views.create_post, name='create_post'),

    path('update/<int:post_id>', posts_views.update_post, name='update'),

    path('delete/<int:post_id>', posts_views.delete, name='delete'),

    path('<int:post_id>', posts_views.post, name='get_post'),

    path('profile/<user_name>', posts_views.profile, name='profile'),

    # FAKE
    path('fake/users', posts_views.fake_create_user),
    path('fake/posts', posts_views.fake_create_posts),
]
