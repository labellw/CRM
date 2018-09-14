from django.utils.deprecation import MiddlewareMixin

from django.shortcuts import HttpResponse,render,redirect

import re

class PermissionMiddleware(MiddlewareMixin):

    def process_request(self,request):

        current_path = request.path


        #白名单
        white_url = ["/login/","index","/admin/*"]

        for reg in white_url:
            ret = re.search(reg,current_path)

            if ret:
                return None

        #校验用户是否登录

        user = request.session.get("user")

        if not user:
            return redirect("/login/")


        #权限认证

        permission_list = request.session.get("permission_list")
        # print(permission_list)

        for reg in permission_list:
            reg = "^%s$"%reg
            # print(reg)
            ret = re.search(reg,current_path)

            if ret:
                return None

        return HttpResponse("无权限访问")



'''
if "/stark/app01/order/1/change/" in 

[
'/stark/app01/order/', 
'/stark/app01/order/add/',
'/stark/app01/order/(\\d+)/change/',
'/stark/app01/order/(\\d+)/delete/', 
'/stark/app01/school/', 
'/stark/app01/school/add/', 
'/stark/app01/school/(\\d+)/change/',
'/stark/app01/school/(\\d+)/delete/'
]


'''
