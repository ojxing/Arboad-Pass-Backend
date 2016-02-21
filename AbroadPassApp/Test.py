# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json

login = 'http://localhost:8000/api/v1/user/login/'
data1 = {'username':'ojxing','password':'newpass'}
head = {'Content-type':'application/json'}
r1 = requests.post(login,json.dumps(data1),headers=head)
print(r1.status_code)
# print(r1.content)
# print(r1.cookies)
# print(requests.session())
print('------------------------')

# url = 'http://localhost:8000/api/v1/userprofile/'
# head = {'Content-type':'application/json'}
# # auth = HTTPBasicAuth('ojxing','ojx9103123')
# r = requests.get(url,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# if r.content =='':
#     print('没有值')
# else:
#     print(json.dumps(json.loads(r.content),indent=1))

#
# post_url = 'http://localhost:8000/api/v1/userprofile/'
# head = {'Content-type':'application/json'}
# data = {'gender':'t10'}
# r = requests.post(post_url,json.dumps(data),headers=head)
# print(r.status_code)
# print(r.content)

# reg_url = 'http://localhost:8000/api/v1/user/register/'
# head = {'Content-type':'application/json'}
# data = {'username':u'家兴','password':'newpass'}
# r = requests.post(reg_url,json.dumps(data),headers=head)
# print(r.status_code)
# print(r.content)

reg_url = 'http://localhost:8000/api/v1/user/logout/'
head = {'Content-type':'application/json'}
#data = {'username':u'家兴','password':'newpass'}
r = requests.get(reg_url,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
print(r.status_code)
print(r.content)
print(r.cookies)