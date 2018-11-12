from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save

# Create your models here.

class Author(models.Model):
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    birth_date = models.DateField(null = True, blank = True)
    picture =  models.ImageField(default = '', blank = True)
    birth_place = models.CharField(max_length = 100, blank = True)
    description = models.TextField(max_length=5000, blank = True)
    website = models.CharField(max_length = 100, blank = True)
    sign = models.CharField(max_length = 100, blank = True)

    def __str__(self):
        return self.last_name + " " + self.first_name


class Book(models.Model):
    title = models.CharField(max_length = 200)
    description = models.TextField(max_length=5000)
    genre = models.IntegerField(choices=[
        (1, "Fiction"),
        (2, "Biography & Memoirs"),
        (3, "History"),
        (4, "Motivational"),
        (5, "Religious"),
        (6, "Business & Economy"),
        (7, "Dictionary"),
        (8, "Specialty Books"),
        (9, "Romance"),
        (10, "Mystery"),
        (11, "Science Fiction"),
        (12, "Fantasy"),
        (13, "Classics"),
    ])
    score = models.FloatField(default=0.0)
    appearance_date = models.DateField()
    publishing_house = models.CharField(max_length = 200)
    cover = models.ImageField(default = '', blank = True)
    authors = models.ManyToManyField(Author, related_name='Books')

    votes = models.ManyToManyField(User, blank = True, related_name='UserBook')

    def __str__(self):
        return self.title

class BUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buser')
    birth_date = models.DateField(null=True, blank=True)
    favourites = models.ManyToManyField(Book, related_name='Favourites', blank = True)
    read = models.ManyToManyField(Book, related_name='Read', blank = True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 100)
    content = models.TextField(max_length = 5000)

    def __str__(self):
        return self.title

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        BUser.objects.create(user=instance)
    instance.buser.save()
