from django.contrib.auth import authenticate,login,logout
from django.db import models
from django.conf.urls import url
from django.contrib.auth.models import User
from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication,SessionAuthentication
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey,create_api_key
from tastypie.http import HttpUnauthorized,HttpForbidden
from AbroadPassApp.models import UserProfile,create_user_profile

#create api key
models.signals.post_save.connect(create_api_key, sender=User)
class ProfileAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)


class UserResource(ModelResource):
    userprofile = fields.ToOneField('AbroadPassApp.api.UserProfileResource',related_name='user', attribute='userprofile',full=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = {'username','email'}
        allowed_method =['get','post']

    def override_urls(self):
        return [
            url(r"(?P<resource_name>%s)/login%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('login'),name="api_login"),
            url(r"(?P<resource_name>%s)/logout%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('logout'),name="api_logout"),
            url(r"(?P<resource_name>%s)/register%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('register'),name="api_register"),
        ]

    def register(self, request, **kwargs):
        self.method_check(request,allowed=['post'])

        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')

        new_user = User.objects.create_user(username=username, email=username, password=password)
        new_user.save()

        return self.create_response(request,{'Create_success':True})

    def login(self,request,**kwargs):
        self.method_check(request,allowed=['post'])
        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                api_key = ApiKey.objects.get(user=user)
                return self.create_response(request,{'success':True,'api':api_key})
            else:
                return self.create_response(request,{'success':False,'reason':'disabled',},HttpForbidden)
        else:
            return self.create_response(request,{'success':False,'reason':'incorrect',},HttpUnauthorized)

    def logout(self,request,**kwargs):
        self.method_check(request,allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request,{'success':True})
        else:
            return self.create_response(request,{'success':False},HttpUnauthorized)

class UserProfileResource(ModelResource):

    # user = fields.ToOneField(UserResource,attribute='user',related_name='userprofile')

    # def hydrate(self, bundle):
    #     bundle.obj.user = User.objects.get(id=14)
    #     return bundle

    class Meta:
        queryset = UserProfile.objects.all()
        resource_name ='userprofile'
        authorization = ProfileAuthorization()
        authentication = SessionAuthentication()

    # def obj_create(self, bundle, **kwargs):
    #     #user = User.objects.get(pk=14)
    #     profile = UserProfile(user=user)
    #     profile.save()

class ProfileAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)







