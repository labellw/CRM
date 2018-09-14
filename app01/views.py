from django.shortcuts import render,HttpResponse,redirect

from rbac.models import User

# Create your views here.

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")

        user = User.objects.filter(user=username,pwd=password).first()

        if user:
            request.session["user"] = user.user   # 存储登录状态

            #查询当前登录用户的所有权限url
            permissions = user.roles.all().values("permissions__url","permissions__code","permissions__title").distinct()

            permission_list = []
            permission_menu_list = []
            for item in permissions:
                permission_list.append(item["permissions__url"])

                if item["permissions__code"] == "list":
                    permission_menu_list.append({
                        "url": item["permissions__url"],
                        "title": item["permissions__title"],

                    })


            #将权限列表放入到session中

            request.session["permission_list"] = permission_list

            #将菜单权限列表注册到session中
            request.session["permission_menu_list"] = permission_menu_list

            return redirect("/index/")









    return render(request,"login.html")

def index(request):

    return render(request,"index.html")
