# -*- coding: utf-8 -*-
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
from tastypie.http import HttpUnauthorized,HttpForbidden,HttpNotFound,HttpAccepted
from tastypie.serializers import Serializer
from models import Provider,NormalUser,Notification,Article #create_user_profile
from django.http import HttpResponse
from tastypie import resources

#create api key
models.signals.post_save.connect(create_api_key, sender=User)

def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)

class MyModelResource(resources.ModelResource):
    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        response =response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response


class GroupResource(MyModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'id': ALL,
            'name': ALL,
        }

class UserResource(MyModelResource):
    groups = fields.ToManyField(GroupResource, 'groups',blank=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = {'username','email','resource_uri'}
        allowed_method =['get','post','put','patch']
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'plist'])
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
            url(r"(?P<resource_name>%s)/userexist%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('userexist'),name="api_userexist"),
        ]
    #注册
    def register(self, request, **kwargs):
        self.method_check(request,allowed=['post','options'])

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

        response = self.create_response(request,{'success':True})
    	response['Access-Control-Allow-Origin'] = "*"
        response['Access-Control-Allow-Methods'] = "GET, PUT, POST, PATCH"
        return response


    #登录Return group of user or provider
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

    #注销
    def logout(self,request,**kwargs):
        self.method_check(request,allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request,{'success':True})
        else:
            return self.create_response(request,{'success':False},HttpUnauthorized)
    #用户名存在
    def userexist(self,request,**kwargs):
        self.method_check(request,allowed=['get'])
        #data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        #username = request.get('username','')
        username = request.GET['username']
        if User.objects.filter(username=username).exists():
            return self.create_response(request,{'result':True},HttpForbidden)
        else:
            return self.create_response(request,{'result':False},HttpUnauthorized)

    #修改密码
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

class ProviderResource(MyModelResource):
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


class NormalUserResource(MyModelResource):

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

class ArticleResource(MyModelResource):
    provider = fields.ForeignKey(ProviderResource,'provider')

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/post%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('post_article'),name="api_post_article"),
            url(r"(?P<resource_name>%s)/comment%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('comment_article'),name="api_comment_article"),
            url(r"(?P<resource_name>%s)/like%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('like_article'),name="api_like_article"),
            url(r"(?P<resource_name>%s)/list%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('list_article'),name="api_list_article"),
        ]

    def dehydrate(self, bundle):
        #bundle.obj.slug = str(bundle.data['content'])[1:40]
        bundle.data['brief'] = bundle.data['content'][0:40] + '......'
        return bundle

    def list_article(self,request,**kwargs):
        obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        return self.create_response(request,obj)
        #return self.dispatch_list(request)

    #文章点赞
    def like_article(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        id = request.GET['id']
        try:
            article = Article.objects.get(pk =id)
            article.like = article.like + 1
            article.save()
            return self.create_response(request,{'success':True,'reason':'Article Like'})
        except Article.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Article Not Existed!'},HttpNotFound)

    #文章评论
    def comment_article(self,request, **kwargs):
        pass
    #文章发布
    def post_article(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        data = self.deserialize(request,request.body,format=request.META.get('CONTENT_TYPE','application/json'))
        content = data.get('content','')
        title = data.get('title','')
        user = request.user
        try:
            provider = Provider.objects.get(user_id = user.id)
            article = Article.objects.create(content=content,title=title, provider=provider)
            article.save()
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'You are not a Provider!'})

        return self.create_response(request,{'success':False,'reason':'Artical Post Success!',})

    class Meta:
        queryset = Article.objects.all()
        resource_name = 'article'
        filtering = {
            'provider':ALL_WITH_RELATIONS
        }
        authorization = Authorization()
        authentication = MultiAuthentication(SessionAuthentication(),ApiKeyAuthentication())

class NotificationResource(MyModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        filtering = {
            'user':ALL_WITH_RELATIONS
        }
        authorization = Authorization()
        authentication = MultiAuthentication(SessionAuthentication(),ApiKeyAuthentication())


