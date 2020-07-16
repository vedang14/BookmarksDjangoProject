# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# class User(models.Model):
#     username = models.CharField(unique=True,max_length=50)

class Link(models.Model):
    url = models.URLField(unique=True)

class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)