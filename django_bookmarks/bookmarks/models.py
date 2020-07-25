# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# class User(models.Model):
#     username = models.CharField(unique=True,max_length=50)

class Link(models.Model):
    url = models.URLField(unique=True)
    def __str__(self):
        return self.url
    class Admin:
        pass
class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)
    def __str__(self):
        return '%s, %s' % (self.user.username, self.link.url)
    class Admin:
        pass
class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    bookmarks = models.ManyToManyField(Bookmark)
    def __str__(self):
        return self.name
    class Admin:
        pass