# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate,login,logout
from django.db import models
from django.conf.urls import url
from django.contrib.auth.models import User,Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication,SessionAuthentication,MultiAuthentication
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.compat import get_user_model, get_username_field
from tastypie.models import ApiKey,create_api_key
from tastypie.http import HttpUnauthorized,HttpForbidden,HttpNotFound,HttpAccepted
from tastypie.serializers import Serializer
from models import Provider,NormalUser,Notification,Article,Application,OnlineApply,MaterialApply,VisaApply,HouseAndTicketApply,Status #create_user_profile
from django.http import HttpResponse
from tastypie import resources
import json

#create api key
models.signals.post_save.connect(create_api_key, sender=User)
#status dict
status_enum = {1:'准备回应',2:'马上回应',3:'已经回应'}

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
            url(r"(?P<resource_name>%s)/show_provider%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('show_user_provider_profile'),name="api_show_user_provider_profile"),
        ]

    #provider用户编辑自己的profile
    def edit_provider_profile(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        user = request.user
        try:
            profile = Provider.objects.get(user_id = user.id)
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Provider Not Existed!'},HttpNotFound)

        return super(ProviderResource,self).put_detail(request,pk=profile.id)

    #provider用户看自己的profile
    def show_provider_profile(self,request,**kwargs):
        user = request.user
        try:
            profile = Provider.objects.get(user_id = user.id)
            if user and not user.is_anonymous():
                return self.dispatch_detail(request,pk = profile.id)
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Provider Not Existed!'},HttpNotFound)

    def show_user_provider_profile(self,request,**kwargs):
        self.is_authenticated(request)
        user = request.user
        print 'bb' + str(user.id)
        providerId = request.GET['pid']
        try:
            profile = Provider.objects.get(user_id = providerId)
            if user and not user.is_anonymous():
                return self.dispatch_detail(request,pk = profile.id)
        except Provider.DoesNotExist:
            return self.create_response(request,{'success':False,'reason':'Provider Not Existed!'},HttpNotFound)

    def dehydrate(self, bundle):
        user = bundle.request.user
        bundle.data['username'] = bundle.obj.user
        bundle.data['userid'] = bundle.obj.user.id
        bundle.data['hasapply'] = False
        providerId =  bundle.request.GET.get('pid')
        if providerId!=None:
            normaluser = NormalUser.objects.get(user_id=user.id)
            provider = Provider.objects.get(user_id=providerId)
            if Application.objects.filter(normaluser=normaluser, provider=provider).exists():
                bundle.data['hasapply'] = True
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
    provider = fields.ForeignKey(ProviderResource,'provider',full=True)

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/post%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('post_article'),name="api_post_article"),
            url(r"(?P<resource_name>%s)/comment%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('comment_article'),name="api_comment_article"),
            url(r"(?P<resource_name>%s)/like%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('like_article'),name="api_like_article"),
            url(r"(?P<resource_name>%s)/list%s$"%(self._meta.resource_name,trailing_slash()),self.wrap_view('list_article'),name="api_list_article"),
        ]

    def dehydrate(self, bundle):
     	is_brief =  bundle.request.GET.get('is_brief')
        if is_brief != None and is_brief == 'True':
            bundle.data['brief'] = bundle.data['content'][0:40] + '......'
            del bundle.data['content']
        return bundle

    def list_article(self,request,**kwargs):
        # obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        # return self.create_response(request,obj)
        return self.dispatch_list(request)

    #文章点赞
    def like_article(self,request, **kwargs):
        self.method_check(request,allowed=['post','put'])
        id = request.GET['id']
        try:
            article = Article.objects.get(pk =id)
            article.likes = article.likes + 1
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

class ApplicationResource(MyModelResource):
    normaluser = fields.ForeignKey(NormalUserResource,'normaluser')
    provider = fields.ForeignKey(ProviderResource, 'provider',full=True)
    class Meta:
        queryset = Application.objects.all()
        ordering  = ['create_time']
        resource_name = 'application'
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
        allowed_method = ['get', 'post', 'put', 'patch']
        detail_allowed_methods = ['get', 'post', 'put', 'patch']
        filtering = {
            'normaluser':ALL_WITH_RELATIONS
        }

    def override_urls(self):
        return [
            url(r"(?P<resource_name>%s)/generate%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('generate'), name="api_application_generate"),
            url(r"(?P<resource_name>%s)/list%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('list'), name="api_application_list"),
            url(r"(?P<resource_name>%s)/edit_app%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('edit_app'), name="api_application_edit"),
            url(r"(?P<resource_name>%s)/hasapply%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('hasapply'), name="api_application_hasapply"),
            url(r"(?P<resource_name>%s)/get_status%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_status'), name="api_application_get_status"),
            url(r"(?P<resource_name>%s)/edit_status%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('edit_app_status'), name="api_application_edit"),
            url(r"(?P<resource_name>%s)/create_status%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('create_status'), name="api_application_create_status"),
        ]

    #编辑Application各个阶段状态
    def edit_app_status(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'put'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        applicationId = data.get('appid', '')
        onlineapply_status = data.get('onlineapply', '')
        materialapply_status = data.get('materialapply', '')
        visaapply_status = data.get('visaapply', '')
        houseticketapply_status = data.get('houseticketapply', '')

        try:
            app = Application.objects.get(pk=applicationId)
        except Application.DoesNotExist:
            return self.create_response(request, {'success': False, 'reason': 'Application Not Existed!'}, HttpNotFound)
        if onlineapply_status != '':
        	app.onlineapply.status = int(onlineapply_status)
        	app.onlineapply.save()
        if materialapply_status !='':
        	app.materialapply.status = int(materialapply_status)
        	app.materialapply.save()
        if visaapply_status != '':
        	app.visaapply.status = int(visaapply_status)
        	app.visaapply.save()
        if houseticketapply_status != '':
        	app.houseticketapply.status = int(houseticketapply_status)
        	app.houseticketapply.save()

        return self.create_response(request, {'success': True, 'reason': 'Application Status Modified!'})

    #获取Application各个阶段状态
    def get_status(self, request, **kwargs):
        self.is_authenticated(request)
        appId = request.GET['appid']
        user = request.user
        app = Application.objects.get(pk = appId)
        requestset = {}
        statusList = Status.objects.filter(application = app).order_by('-update_time')
        status = {}

        #给每个过程设立process
        if app.onlineapply is not None:
            requestset['OnlineApply'] = serializers.serialize("json", [app.onlineapply,])
            requestset['OnlineApplyStatus'] = serializers.serialize("json", statusList.filter(serviceType='onlineapply'))
        if app.materialapply is not None:
            requestset['MaterialApply'] = serializers.serialize("json", [app.materialapply,])
            requestset['MaterialApplyStatus'] = serializers.serialize("json", statusList.filter(serviceType='materialapply'))
        if app.visaapply is not None:
            requestset['VisaApply'] = serializers.serialize("json", [app.visaapply,])
            requestset['VisaApplyStatus'] = serializers.serialize("json", statusList.filter(serviceType='visaapply'))
        if app.houseticketapply is not None:
            requestset['HouseAndTicketApply'] = serializers.serialize("json", [app.houseticketapply,])
            requestset['HouseAndTicketApplyStatus'] = serializers.serialize("json", statusList.filter(serviceType='houseticketapply'))

        return self.create_response(request, {'success': True, 'result':requestset})

    #查询User 和 Provider 是否有Application
    def hasapply (self, request, **kwargs):
        self.method_check(request, allowed=['post', 'options'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        providerId = data.get('providerId', '')
        user = request.user
        normaluser = NormalUser.objects.get(user_id=user.id)
        provider = Provider.objects.get(user_id=providerId)

        if Application.objects.filter(normaluser=normaluser, provider=provider).exists():
            return self.create_response(request, {'success': False, 'reason': 'Application Existed!'})
        return self.create_response(request, {'success': True, 'reason': 'Application Not Existed!'})

    # 生成status
    def create_status(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'options'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        appId = data.get('appId', 0)
        serviceType = data.get('serviceType', "")
        status_string = data.get('status_string', "")

        try:
            app = Application.objects.get(pk=appId)
        except Application.DoesNotExist:
            return self.create_response(request, {'success': False, 'reason': 'Application Not Existed!'}, HttpNotFound)

        app_status = Status.objects.create()
        app_status.application = app
        app_status.serviceType = serviceType
        app_status.status_string = status_string
        app_status.save()

        return self.create_response(request, {'success': True, 'reason': 'Create Status Success'})

        

    # 生成application
    def generate(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'options'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        providerId = data.get('providerId', '')
        onlineapply_check = data.get('onlineapply',0)
        materialapply_check = data.get('materialapply',0)
        visaapply_check = data.get('visaapply',0)
        houseticketapply_check = data.get('houseticketapply',0)


        user = request.user
        normaluser = NormalUser.objects.get(user_id = user.id)
        provider = Provider.objects.get(user_id = providerId)

        if Application.objects.filter(normaluser = normaluser,provider = provider).exists():
        	return self.create_response(request, {'success': False, 'reason': 'Application Existed!'})

        onlineapply = None
        materialapply = None
        visaapply = None
        houseticketapply = None

        if onlineapply_check == 1:
        	onlineapply = OnlineApply.objects.create()
        	onlineapply.status = 0
        	onlineapply.save()
        if materialapply_check == 1:
	        materialapply = MaterialApply.objects.create()
	        cv_status.status = 0
	        materialapply.save()
        if visaapply_check == 1:   
	        visaapply = VisaApply.objects.create()
	        visaapply.status = 0
	        visaapply.save()
        if houseticketapply_check == 1:
	        houseticketapply = HouseAndTicketApply.objects.create()
	        houseticketapply.status = 0
	        houseticketapply.save()
        application = Application.objects.create(normaluser=normaluser, provider = provider,onlineapply = onlineapply,materialapply=materialapply,visaapply=visaapply,houseticketapply=houseticketapply)
        application.save()

        return self.create_response(request, {'success': True, 'reason': 'Create Application Success'})
    def list(self,request,**kwargs):
        self.method_check(request, allowed=['post', 'options','get'])
        self.is_authenticated(request)
        user = request.user
        normaluser = NormalUser.objects.get(user_id = user.id)
        return self.dispatch_list(request,normaluser=normaluser)

    def edit_app(self, request, **kwargs):
        self.method_check(request, allowed=['post', 'put'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        applicationId = data.get('applicationId', '')
        try:
            app = Application.objects.get(pk=applicationId)
        except Application.DoesNotExist:
            return self.create_response(request, {'success': False, 'reason': 'Application Not Existed!'}, HttpNotFound)
        return super(ApplicationResource, self).put_detail(request, pk=app.id)


    def dehydrate(self, bundle):

    	status = ""

    	if bundle.obj.onlineapply !=None:
        	bundle.data['onlineapply'] = bundle.obj.onlineapply.status
        	status = status + '网申 '
        else: 
        	bundle.data['onlineapply'] = 0

        if bundle.obj.materialapply !=None:
        	bundle.data['materialapply'] = bundle.obj.materialapply.cv_status
        	status = status + "递交材料 "
        else: 
        	bundle.data['materialapply'] = 0

        if bundle.obj.visaapply !=None:
        	bundle.data['visaapply'] = bundle.obj.visaapply.status
        	status = status + "签证 "
        else:
        	bundle.data['visaapply'] = 0

        if bundle.obj.houseticketapply !=None:
        	bundle.data['houseticketapply'] = bundle.obj.houseticketapply.status
        	status = status + "租房 "
        else: 
        	bundle.data['houseticketapply'] = 0
        print status
        bundle.data['status'] = status
        return bundle
    # def show_user_profile(self, request, **kwargs):
    #     user = request.user
    #     try:
    #         profile = NormalUser.objects.get(user_id=user.id)
    #         if user and not user.is_anonymous():
    #             return self.dispatch_detail(request, pk=profile.id)
    #     except NormalUser.DoesNotExist:
    #         return self.create_response(request, {'success': False, 'reason': 'User Not Existed!'}, HttpNotFound)
