from django.contrib.auth import authenticate,login,logout
from django.db import models
from django.conf.urls import url
from django.contrib.auth.models import User,Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication,SessionAuthentication,MultiAuthentication
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey,create_api_key
from tastypie.http import HttpUnauthorized,HttpForbidden,HttpNotFound
from models import Provider,NormalUser,Notification #create_user_profile

#create api key
models.signals.post_save.connect(create_api_key, sender=User)

class GroupResource(ModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'id': ALL,
            'name': ALL,
        }

class UserResource(ModelResource):
    groups = fields.ToManyField(GroupResource, 'groups',blank=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = {'username','email','resource_uri'}
        allowed_method =['get','post','put','patch']
        authentication = SessionAuthentication()
        authorization = Authorization()
        filtering = {
            'groups':ALL_WITH_RELATIONS
        }

    def override_urls(self):
        return [
            url(r"(?P<resource_name>%s)/login%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('login'),name="api_login"),
            url(r"(?P<resource_name>%s)/logout%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('logout'),name="api_logout"),
            url(r"(?P<resource_name>%s)/register%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('register'),name="api_register"),
            url(r"(?P<resource_name>%s)/changepassword%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('changepassword'),name="api_changepassword"),
        ]
    #Register as a user
    def register(self, request, **kwargs):
        self.method_check(request,allowed=['post'])

        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')
        type = data.get('type','')

        #Basic Validation
        if User.objects.filter(username=username).exists():
            return self.create_response(request,{'success':False,'reason':'Username Existed!',},HttpForbidden)
        new_user = User.objects.create_user(username=username, email=username, password=password)
        new_user.save()

        #Devider User Type => Normal User or Provider
        #user group
        if type == 'provider':
            provider_g = Group.objects.get_or_create(name='provider')[0]
            provider_g.user_set.add(new_user)
            provider = Provider(user=new_user)
            provider.save()
        else:  #By default, register as normal user
            normaluser_g = Group.objects.get_or_create(name='normaluser')[0]
            normaluser_g.user_set.add(new_user)
            normaluser = NormalUser(user=new_user)
            normaluser.save()
        return self.create_response(request,{'success':True})

    #Return group of user or provider
    def login(self,request,**kwargs):
        self.method_check(request,allowed=['post'])
        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        username = data.get('username','')
        password = data.get('password','')

        #Check Existed
        if not User.objects.filter(username=username).exists():
            return self.create_response(request,{'success':False,'reason':'User Not Existed!',},HttpForbidden)

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                api_key = ApiKey.objects.get(user=user)
                return self.create_response(request,{'success':True,'api':api_key.key,'group':user.groups.all()[0]})
            else:
                return self.create_response(request,{'success':False,'reason':'disabled',},HttpForbidden)
        else:
            return self.create_response(request,{'success':False,'reason':'Invalid Password',},HttpUnauthorized)

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

class ProviderResource(ModelResource):
    class Meta:
        queryset = Provider.objects.all()
        resource_name ='provider'
        authorization = Authorization()
        authentication = MultiAuthentication(SessionAuthentication(),ApiKeyAuthentication())
        allowed_method =['get','post','put','patch']
        detail_allowed_methods =['get','post','put','patch']

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/edit%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('edit_provider_profile'),name="api_edit_provider_profile"),
            url(r"(?P<resource_name>%s)/show%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('show_provider_profile'),name="api_show_provider_profile"),
        ]

    def edit_provider_profile(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        user = request.user
        try:
            profile = Provider.objects.get(user_id = user.id)
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Provider Not Existed!'},HttpNotFound)

        return super(ProviderResource,self).put_detail(request,pk=profile.id)

    def show_provider_profile(self,request,**kwargs):
        user = request.user
        try:
            profile = Provider.objects.get(user_id = user.id)
            if user and not user.is_anonymous():
                return self.dispatch_detail(request,pk = profile.id)
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Provider Not Existed!'},HttpNotFound)

    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.user
        bundle.data['userid'] = bundle.obj.user.id
        return bundle


class NormalUserResource(ModelResource):

    class Meta:
        queryset = NormalUser.objects.all()
        resource_name ='normaluser'
        authorization = Authorization()
        authentication = SessionAuthentication()
        allowed_method =['get','post','put','patch']
        detail_allowed_methods =['get','post','put','patch']
    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/show%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('show_user_profile'),name="api_show_user_profile"),
            url(r"(?P<resource_name>%s)/edit%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('edit_user_profile'),name="api_edit_user_profile"),
        ]

    def edit_user_profile(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        user = request.user
        try:
            profile = NormalUser.objects.get(user_id = user.id)
        except NormalUser.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'User Not Existed!'},HttpNotFound)
        return super(NormalUserResource,self).put_detail(request,pk=profile.id)

    def show_user_profile(self,request,**kwargs):
        user = request.user
        try:
            profile = NormalUser.objects.get(user_id = user.id)
            if user and not user.is_anonymous():
                return self.dispatch_detail(request,pk = profile.id)
        except NormalUser.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'User Not Existed!'},HttpNotFound)

    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.user
        bundle.data['userid'] = bundle.obj.user.id
        return bundle


class NotificationResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        filtering = {
            'user':ALL_WITH_RELATIONS
        }
        authorization = Authorization()
        authentication = MultiAuthentication(SessionAuthentication(),ApiKeyAuthentication())


