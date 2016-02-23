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
        fields = {'username','email','resource_uri'}
        allowed_method =['get','post','put','patch']
        authentication = SessionAuthentication()
        authorization = Authorization()

    def override_urls(self):
        return [
            url(r"(?P<resource_name>%s)/login%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('login'),name="api_login"),
            url(r"(?P<resource_name>%s)/logout%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('logout'),name="api_logout"),
            url(r"(?P<resource_name>%s)/register%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('register'),name="api_register"),
            url(r"(?P<resource_name>%s)/changepassword%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('changepassword'),name="api_changepassword"),
        ]

    def register(self, request, **kwargs):
        self.method_check(request,allowed=['post'])

        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')

        if User.objects.filter(username=username).exists():
            return self.create_response(request,{'success':False,'reason':'Username Existed!',},HttpForbidden)

        new_user = User.objects.create_user(username=username, email=username, password=password)
        new_user.group = '1'
        new_user.save()

        return self.create_response(request,{'success':True})

    def login(self,request,**kwargs):
        self.method_check(request,allowed=['post'])
        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')

        if not User.objects.filter(username=username).exists():
            return self.create_response(request,{'success':False,'reason':'User Not Existed!',},HttpForbidden)

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

    def changepassword(self,request,**kwargs):
        self.method_check(request,allowed=['post'])
        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        oldpassword = data.get('oldpassword','')
        newpassword = data.get('newpassword','')

        user = authenticate(username=request.user.username, password=oldpassword)
        if user is not None and user.is_active:
            if request.user.check_password(oldpassword):
                user.set_password(newpassword)
                user.save()
                login(request,user)
                return self.create_response(request,{'success': True,'reason':"Change Password Success!"},HttpForbidden)
            else:
                return self.create_response(request,{'success':False,'reason':'Incorrect Password!'},HttpForbidden)
        else:
            return self.create_response(request,{'success':user.id,'reason':'Time out! Login again please!'},HttpForbidden)

class UserProfileResource(ModelResource):

    class Meta:
        queryset = UserProfile.objects.all()
        resource_name ='userprofile'
        authorization = ProfileAuthorization()
        authentication = SessionAuthentication()
        allowed_method =['get','post','put','patch']
        detail_allowed_methods =['get','post','put','patch']
    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/show%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('current_user'),name="api_showprofile"),
            url(r"(?P<resource_name>%s)/edit%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('editprofile'),name="api_editprofile"),
        ]

    def editprofile(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        user = request.user
        profile = UserProfile.objects.get(user_id = user.id)
        return super(UserProfileResource,self).put_detail(request,pk=profile.id)

    def current_user(self,request,**kwargs):
        user = request.user
        profile = UserProfile.objects.get(user_id = user.id)
        if user and not user.is_anonymous():
            return self.dispatch_detail(request,pk = profile.id)

    def dehydrate(self, bundle):
        bundle.data['email'] = '**'+bundle.obj.email
        bundle.data['user_resource_uri'] = "/api/v1/user/" + str(bundle.obj.user.id) +"/"
        return bundle

class ProfileAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user





