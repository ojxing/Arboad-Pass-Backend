接口描述
==
## 1.Base URL

    http://localhost:8000/api/v1/
    
<br/><br/> 
## 2.Authentication
### Register

```
Method:POST
Url:   http://localhost:8000/api/v1/user/register/
Body:  {'username':'name','password':'password','type':'normaluser'}
Response: {'success':bool_result,'reason':'if error occur,show error'}
```
Tips: Type includes __normaluser__ and __provider__. Type can not be modified once registered

### Login

```
Method:POST
Url:   http://localhost:8000/api/v1/user/login/
Body:  {'username':'name','password':'password'}
Response: {'success':bool_result,'api':api-key ,'group':"normaluser",'reason':'if error occur,show error'}
```
Tips: User and Provider share the same login api. The group paras in response tells the user type (__normaluser__ or __provider__)

### Logout
```
Method:GET
Url:   http://localhost:8000/api/v1/user/logout/
Response: {'success':bool_result}
```

### Changepassword
```
Method:POST
Url:   http://localhost:8000/api/v1/user/changepassword/
Body： {'oldpassword':'oldpassword','newpassword':'newpassword'}
Response:{'success': bool_result ,'reason':'if error occur,show error'}
```
<br/><br/>
## 3.Normal User Profile Management
###View normaluser profile list
```
Method:GET
Url:   http://localhost:8000/api/v1/normaluser/
Cookies:"sessionid","csrftoken"
Response: NormaluserProfileResource with corresponding user list
```
Tips: Details in the [Test.py](../AbroadPassProject/AbroadPassApp/Test.py)

###View single normaluser profile (Logged in User)
```
Method:GET
Url:   http://localhost:8000/api/v1/normaluser/show/
Cookies:"sessionid","csrftoken"
Response: NormaluserProfileResource with corresponding user
```
Tips: Details in the [Test.py](../AbroadPassProject/AbroadPassApp/Test.py)

###Edit normaluser profile
```
Method:PUT
Url:   http://localhost:8000/api/v1/normaluser/edit/
Cookies:"sessionid","csrftoken"
Body:{'email':'abc@abc.com'}
Response: NormaluserProfileResource with corresponding user
```
Tips: Details in the [Test.py](../AbroadPassProject/AbroadPassApp/Test.py)

<br/><br/>
## 4.Provider Profile Management
###View provider profile list
```
Method:GET
Url:   http://localhost:8000/api/v1/provider/
Cookies:"sessionid","csrftoken"
Response: ProviderProfileResource with corresponding provider list
```

###View single provider profile (Logged in User)
```
Method:GET
Url:   http://localhost:8000/api/v1/provider/show/
Cookies:"sessionid","csrftoken"
Response: ProviderProfileResource with corresponding provider
```
Tips: Details in the [Test.py](../AbroadPassProject/AbroadPassApp/Test.py)

###Edit provider profile
```
Method:PUT
Url:   http://localhost:8000/api/v1/provider/edit/
Cookies:"sessionid","csrftoken"
Body:{'email':'abc@abc.com'}
Response: ProviderProfileResource with corresponding provider
```
Tips: Details in the [Test.py](../AbroadPassProject/AbroadPassApp/Test.py)

<br/><br/>
## 5.Get School、Major Infor list
###Get Country List
```
Method:GET
Url:   http://localhost:8000/api/v1/country/
Response: country list
```

###Get City List By Country
```
Method:GET
Url:   http://localhost:8000/api/v1/city/?country__name=中国/
Response: city list
```

###Get School List By City
```
Method:GET
Url:   http://localhost:8000/api/v1/school/?city__name=北京/
Response: school list
```

###Get Major Category List
```
Method:GET
Url:   http://localhost:8000/api/v1/major/
Response: major category list
```

<br/><br/>
## 4.申请流程状态管理（请求结尾带上username和api_key）
###查看user和Provider是否已有application
```
Method:POST
Url:   http://121.42.178.246:8008/api/v1/application/hasapply/
Body： {'providerId':11}
Response:{'success':ture,'reason':''}
```

###生成application
```
Method:POST
Url:   http://121.42.178.246:8008/api/v1/application/generate/
Body： {'providerId':11}
Response:{'success':ture,'reason':'Create Application Success'}
```

###查看user的所有application
```
Method:GET
Url:   http://121.42.178.246:8008/api/v1/application/
Response:application list
```

###查看user某一application的所有流程的状态
```
Method:GET
Url:   http://121.42.178.246:8008/api/v1/application/get_status/?appid=3
Response:{'success':ture,'OnlineApply':0,'MaterialApply':0,'VisaApply':0,'HouseAndTicketApply':0}
```

###更改application某一流程的状态
```
Method:POST
Url:   http://121.42.178.246:8008/api/v1/application/edit_status/
Body： {'providerId':11,'appid':3,'onlineapply':1} //可选 'materialapply':1,'visaapply':1,'houseticketapply':1
Response:{'success':ture,'reason':'Application Status Modified!'}
```

###更改application 除状态外的信息（很少用）
```
Method:PUT
Url:   http://121.42.178.246:8008/api/v1/application/edit_app/
Body： {'applicationId':3,//其他信息}
Response:{'success':ture,'reason':'Application Status Modified!'}
```

###补充 查询Provider（附带user 与该Provider有无application）
###（用户角度点开Provider, 上面的/provider/show是Provider登录进去看自己的profile）
```
Method:GET
Url:   http://121.42.178.246:8008/api/v1/provider/show_provider/?pid=12
Response:{'success':ture,} Provider Information  备注：其中hasapply 显示当前用户与该Provider是否有application
```

##----------------------------------6/21号更新-----------------

增加create_status 接口<br/>
修改get_status 接口

###增加create_status
provider 填写状态，每次都增加一条记录
```
Method:POST
Url:   http://121.42.178.246:8008/api/v1/application/create_status/
Body： {'appId':18,'serviceType':'onlineapply','status_string':'准备网申的东西'} //serviceType为以下四种之一【'onlineapply','materialapply','visaapply','houseticketapply'】
Response:{'success':ture,'reason':'Create Status Success!'}
```

###修改get_status
get_status接口返回增加 显示provider定义的状态 比如 OnlineApplyStatus ，按添加时间倒序排列
