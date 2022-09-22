from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from .forms import SignupForm, ResetPassword
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

from .tasks import send_email, delete_user


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            print(f'{current_site=}')

            # Отправка письма
            send_email.delay(current_site.domain, user.id, 'registration/email_confirm.html')

            # Удаление через 300 сек\
            delete_user.apply_async(args=(user.id,), countdown=300)

            return HttpResponse('Пожалуйста, подтвердите вашу регистрацию. На указанную почту было выслано письмо. '
                                'Проверьте папку (Спам), если не видите его во входящих.')
    else:
        form = SignupForm()

    return render(request, 'registration/sign_up.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Спасибо, что подтвердили регистрацию, теперь вы можете зайти на сайт')
    else:
        return HttpResponse('Ссылка активации аккаунта неверна!')


def reset_password(request):
    if request.method == 'GET':
        return render(request, 'registration/reset_password.html')

    if request.method == 'POST':
        to_email = request.POST.get('email')
        if not to_email:
            return render(request, 'registration/reset_password.html', {'error': 'Email не был указан'})

        try:
            user = User.objects.get(email=to_email)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return render(request, 'registration/reset_password.html', {'error': 'Пользователь с таким email не существует!'})

        current_site = get_current_site(request)

        # Письмо
        send_email.delay(current_site.domain, user.id, 'registration/email_reset_password.html')

        return HttpResponse('Ссылка для сброса пароля была отправлена на указанную почту. '
                            'Проверьте папку (Спам), если не видите его во входящих')


def new_password(request, uidb64, token):
    if request.method == 'POST':
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPassword(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password1'])
                user.save()
                return redirect('login')
            else:
                return render(request, 'registration/new_password.html', {'errors': form.errors})
        else:
            return render(request, 'registration/reset_password.html',
                          {'error': 'Пользователь не найден!'})

    return render(request, 'registration/new_password.html')

