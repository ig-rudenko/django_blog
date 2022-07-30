from django.urls import path
from posts.api import views
from rest_framework.urlpatterns import format_suffix_patterns

# /api/

urlpatterns = [
    # API
    path('posts', views.PostViewAPIView.as_view()),
    path('posts/<int:pk>', views.PostDetailAPIView.as_view()),

    path('users', views.UserListAPIView.as_view()),
    path('users/<username>', views.UserDetailAPIView.as_view()),

    path('profiles', views.ProfileListCreateAPIView.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])
