from django.db import models
from django.contrib.auth.models import User

from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor.fields import RichTextField
import os

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts_img/%Y/%m/%d/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(
                name='posts_date_time_idx',
                fields=['date']
            )
        ]
        ordering = ['-date']

    def get_absolute_url(self):
        return reverse('get_post', kwargs={'post_id': self.pk})

    def __str__(self):
        return 'Post: ' + self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            img = Post.objects.get(id=self.id).image
            if img and not self.image or img and self.image.path != img.path:
                # Удаляем предыдущий файл картинки
                print('Удаляем старую картинку')
                if os.path.exists(img.path):
                    os.remove(img.path)
        except Post.DoesNotExist:
            pass

        return super(Post, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    hobby = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'auth_user_profile'


class Log(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    obj = models.CharField('model', max_length=10)
    message = models.CharField(max_length=300)

    class Meta:
        db_table = 'posts_logs'
        indexes = [
            models.Index(fields=['datetime'], name='datetime_index')
        ]


@receiver([post_save], sender=User)
def user_log(sender, instance: User, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
