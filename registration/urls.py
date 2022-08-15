from django.urls import path, re_path
from .views import signup, activate, reset_password, new_password

# /registration/

urlpatterns = [
    path('', signup, name='sign-up'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/', activate, name='activate'),

    path('reset_password', reset_password, name='reset-password'),
    re_path(r'new_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/', new_password,
            name='reset-password-confirm'),
]
