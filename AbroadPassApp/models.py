from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.

class NormalUser(models.Model):
    user = models.OneToOneField(User,related_name='normaluser')
    gender = models.CharField(max_length=10)
    birth = models.DateField(null=True)
    province = models.CharField(max_length=50)
    qq = models.CharField(max_length=20)
    email = models.EmailField()
    mobile = models.CharField(max_length=20,default="")
    nationality = models.CharField(max_length=20)
    locate_province = models.CharField(max_length=10)
    locate_city = models.CharField(max_length=10)
    major = models.CharField(max_length=20)
    school = models.CharField(max_length=50)
    gpa = models.CharField(max_length=5)

class Provider(models.Model):
    user = models.OneToOneField(User,related_name='provider')
    gender = models.CharField(max_length=10)
    birth = models.DateField(null=True)
    province = models.CharField(max_length=50)
    qq = models.CharField(max_length=20)
    email = models.EmailField()
    mobile = models.CharField(max_length=20,default="")
    nationality = models.CharField(max_length=20)
    locate_province = models.CharField(max_length=10)
    locate_city = models.CharField(max_length=10)
    major = models.CharField(max_length=20)
    school = models.CharField(max_length=50)
    gpa = models.CharField(max_length=5)


#profile auto-created when user register
# def create_user_profile(sender,**kwargs):
#     user = kwargs["instance"]
#     if kwargs["created"]:
#         profile = UserProfile(user=user)
#         profile.save()
#
# post_save.connect(create_user_profile, sender=User)

