# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tastypie.utils.timezone import now
# Create your models here.

class Grade(models.Model):
   user = models.ForeignKey(User)
   gpa = models.CharField(max_length=5)
   toefl_reading = models.CharField(max_length=5)
   toefl_listening = models.CharField(max_length=5)
   toefl_speaking = models.CharField(max_length=5)
   toefl_writing = models.CharField(max_length=5)
   toefl_total = models.CharField(max_length=5)
   gre_verbal = models.CharField(max_length=5)
   gre_quantitative = models.CharField(max_length=5)
   gre_writing = models.CharField(max_length=5)
   gre_total = models.CharField(max_length=5)
   gmat = models.CharField(max_length=5)     # three parts?
   ielts_reading = models.CharField(max_length=5)
   ielts_listening = models.CharField(max_length=5)
   ielts_speaking = models.CharField(max_length=5)
   ielts_writing = models.CharField(max_length=5)
   ielts_total = models.CharField(max_length=5)

class Goal(models.Model):
   user = models.ForeignKey(User)
   country = models.CharField(max_length=20)
   city = models.CharField(max_length=10)
   school = models.CharField(max_length=50)

class NormalUser(models.Model):
    user = models.OneToOneField(User,related_name='normaluser')
    user_realname = models.CharField(max_length=10,null=False,default="")
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
    avatar = models.CharField(max_length=100,null=True)
    headline = models.CharField(max_length=50,default="")

class Provider(models.Model):
    user = models.OneToOneField(User,related_name='provider')
    user_realname = models.CharField(max_length=10,null=False,default="")
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
    avatar = models.CharField(max_length=100, null=True)
    headline = models.CharField(max_length=50,default="")

#Application
class OnlineApply(models.Model):
   school = models.CharField(max_length=50)
   major = models.CharField(max_length=50)
   school_link = models.URLField(max_length=200)
   major_link = models.URLField(max_length=200)
   application_link = models.URLField(max_length=200)
   username = models.CharField(max_length=50)
   password = models.CharField(max_length=50)
   status = models.IntegerField(default=0)  # 0: false, 1: create(, 2: approve)
class MaterialApply(models.Model):
   cv = models.FileField(upload_to="/Material/CV")
   ps = models.FileField(upload_to="/Material/PS")
   recommend_letter1 = models.FileField(upload_to="/Material/RL")
   recommend_letter2 = models.FileField(upload_to="/Material/RL")
   recommend_letter3 = models.FileField(upload_to="/Material/RL")

   recommend_letter1_status = models.IntegerField(default=0)  # 0: false, 1: submit, 2: approve
   recommend_letter2_status = models.IntegerField(default=0)
   recommend_letter3_status = models.IntegerField(default=0)
   cv_status = models.IntegerField(default=0)
   ps_status = models.IntegerField(default=0)

class VisaApply(models.Model):
   create_time = models.DateTimeField(auto_now_add=True)
   status = models.IntegerField(default=0)  # 0: false, 1: create(, 2: approve)

class HouseAndTicketApply(models.Model):
   create_time = models.DateTimeField(auto_now_add=True)
   status = models.IntegerField(default=0)  # 0: false, 1: create(, 2: approve)

class Application(models.Model):
   normaluser = models.ForeignKey(NormalUser,related_name='application')
   provider= models.ForeignKey(Provider,related_name='application')
   onlineapply = models.OneToOneField(OnlineApply,related_name='application')
   materialapply = models.OneToOneField(MaterialApply,related_name='application')
   visaapply = models.OneToOneField(VisaApply,related_name='application')
   houseticketapply = models.OneToOneField(HouseAndTicketApply,related_name='application')
   app_status = models.IntegerField(default=0)
   onlineapply_status = models.IntegerField(default=0)
   cvapply_status = models.IntegerField(default=0)
   hardmaterialapply_status = models.IntegerField(default=0)
   visaapply_status = models.IntegerField(default=0)
   houseticketapply_status = models.IntegerField(default=0)
   create_time = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    provider = models.ForeignKey(Provider)
    create_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50,default="")
    content = models.TextField()
    likes = models.IntegerField(default=0)
    read = models.IntegerField(default=0)

#Country,City and School List
class CountryManager(models.Manager):
    def get_by_natural_key(self,name):
        return self.get(name=name);
class Country(models.Model):
    objects = CountryManager()
    name = models.CharField(max_length=10)
    class Meta:
        unique_together=('name',)

class CityManager(models.Manager):
    def get_by_natural_key(self,name):
        return self.get(name=name);
class City(models.Model):
    objects = CityManager()
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=20)
    class Meta:
        unique_together=('name',)

class School(models.Model):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=50)

class Major(models.Model):
    name = models.CharField(max_length=50)

class Notification(models.Model):
    user = models.ForeignKey(User)
    create_date = models.DateTimeField(default=now())
    content = models.TextField()
    is_read = models.BooleanField(default=False)


#profile auto-created when user register
# def create_user_profile(sender,**kwargs):
#     user = kwargs["instance"]
#     if kwargs["created"]:
#         profile = UserProfile(user=user)
#         profile.save()
#
# post_save.connect(create_user_profile, sender=User)

