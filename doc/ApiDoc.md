接口描述
==
## Base URL

    http://localhost:8000/api/v1/
## Authentication
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
## Normal User Profile Management
###View normaluser profile list
```
Method:GET
Url:   http://localhost:8000/api/v1/normaluser/
Cookies:"sessionid","csrftoken"
Response: NormaluserProfileResource with corresponding user list
```
Tips: Details in the [Test.py](../AbroadPassApp/Test.py)

###View single normaluser profile (Logged in User)
```
Method:GET
Url:   http://localhost:8000/api/v1/normaluser/show/
Cookies:"sessionid","csrftoken"
Response: NormaluserProfileResource with corresponding user
```
Tips: Details in the [Test.py](../AbroadPassApp/Test.py)

###Edit normaluser profile
```
Method:PUT
Url:   http://localhost:8000/api/v1/normaluser/edit/
Cookies:"sessionid","csrftoken"
Body:{'email':'abc@abc.com'}
Response: NormaluserProfileResource with corresponding user
```
Tips: Details in the [Test.py](../AbroadPassApp/Test.py)

## Provider Profile Management
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
Tips: Details in the [Test.py](../AbroadPassApp/Test.py)

###Edit provider profile
```
Method:PUT
Url:   http://localhost:8000/api/v1/provider/edit/
Cookies:"sessionid","csrftoken"
Body:{'email':'abc@abc.com'}
Response: ProviderProfileResource with corresponding provider
```
Tips: Details in the [Test.py](../AbroadPassApp/Test.py)


Api Doc
--
 * [Api Doc](./ApiDoc)
