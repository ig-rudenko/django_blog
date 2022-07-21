from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save
from faker import Faker
from ckeditor.fields import RichTextField

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
        ordering = ['date']

    def __str__(self):
        return 'Post: ' + self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=100, null=True)
    hobby = models.CharField(max_length=200, null=True)


class Log(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    obj = models.CharField('model', max_length=10)
    message = models.CharField(max_length=300)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        print('created', instance)
        f = Faker('ru_RU')
        Profile.objects.create(
            user=instance,
            phone=f.phone_number(),
            address=f.address()
        )

#
# @receiver([post_save], sender=User)
# def user_log(sender, instance: User, created, **kwargs):
#     Log.objects.create(
#         obj=sender,
#         message=f'{instance.username} saved: {created}, with: {kwargs}'
#     )


# @receiver(post_delete, sender=User)
# def delete_user(sender, instance, **kwargs):
#     Log.objects.create(
#         obj=str(type(sender))[:10],
#         message=f'{instance.username} has been deleted | {kwargs}'
#     )
