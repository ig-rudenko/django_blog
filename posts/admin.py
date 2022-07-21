from django.contrib import admin
from .models import Post, Profile, Log
from django.utils.html import mark_safe

from django.contrib.auth.models import User


@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'user', 'user_info', 'link')
    fieldsets = (
        ('Заголовок и дата', {"fields": ("title", "date")}),
        ('Содержимое', {"fields": ("content", 'user')})
    )
    ordering = ('-date',)
    search_fields = ('date', 'title')

    list_filter = ('user',)

    def get_queryset(self, request):
        if len(request.GET) == 0:
            return Post.objects.none()
        else:
            return super().get_queryset(request)

    @admin.display(description='Номер телефона / Адрес')
    def user_info(self, post: Post):
        u = Profile.objects.get(user_id=post.user.id)
        return mark_safe(f"""
<li style="color: green;">{u.phone}</li>
<li style="color: blue;">{u.address}</li>
""")

    @admin.display(description='Открыть')
    def link(self, post: Post):
        return mark_safe(f'<a href="/posts/{post.id}" target="_blank">Читать</a>')


admin.site.unregister(User)


@admin.register(User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'user_info', 'posts_count')
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    sortable_by = ('username', 'is_active')

    actions = ['deactivate']

    @admin.display(description='Номер телефона / Адрес')
    def user_info(self, user: User):
        u = Profile.objects.get(user_id=user.id)
        return mark_safe(f"""
    <li style="color: green;">{u.phone}</li>
    <li style="color: blue;">{u.address}</li>
    """)

    @admin.display(description='Написано постов')
    def posts_count(self, user: User):
        return Post.objects.filter(user_id=user.id).count()

    @admin.action(description='Деактивировать выбранных пользователей')
    def deactivate(self, request, queryset):
        print(request, queryset)
        queryset.update(is_active=False)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('obj', 'message', 'datetime')
