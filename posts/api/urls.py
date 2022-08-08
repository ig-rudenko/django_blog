from django.urls import path
from posts.api import views
from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# /api/

urlpatterns = [
    # API
    path('posts', views.PostViewAPIView.as_view()),
    path('posts/<int:pk>', views.PostDetailAPIView.as_view()),

    path('users', views.UserListCreateAPIView.as_view()),
    path('users/<username>', views.UserDetailAPIView.as_view()),

    path('profiles', views.ProfileListCreateAPIView.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'csv'])
