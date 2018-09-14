from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from stark.page import MyPage
from django.db.models import Q
from app01.models import *
import copy


# 展示类
class ShowList(object):

    def __init__(self, config_obj, data_list, request):
        self.config_obj = config_obj
        self.data_list = data_list
        self.request = request

        # 分页
        self.pagination = MyPage(request.GET.get("page", 1), self.data_list.count(), request, per_page_data=10)
        self.page_queryset = self.data_list[self.pagination.start:self.pagination.end]

    def get_new_action(self):
        temp = []
        temp.extend(self.config_obj.actions)
        temp.append(self.config_obj.patch_delete)

        new_actions = []

        for func in temp:  # 页面展示<option>的文本内容和标签name   在页面调用   列表也可以在前端循环
            new_actions.append({
                "text": func.desc,
                "name": func.__name__
            })

        return new_actions

    def get_headers(self):  # 在页面调用的方法#[checkbox,__str__,或"title", "price", "publish", "authors"，edit,delete]
        # 构建表头
        header_list = []
        for field_or_func in self.config_obj.new_list_display():
            if callable(field_or_func):  # 是否可以被调用（类，对象）
                val = field_or_func(self.config_obj, is_header=True)

            else:
                if field_or_func == "__str__":
                    val = self.config_obj.model._meta.model_name

                else:
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)
                    val = field_obj.verbose_name

            header_list.append(val)

        return header_list

    def get_body(self):  # 在页面调用的方法#[checkbox,__str__,或"title", "price", "publish", "authors"，edit,delete]
        # 构建数据表单部分

        new_data_list = []
        # 构建数据表单部分的数据结构利用[[每一行的数据],[每一行的数据],[每一行的数据]]
        # 在页面展示数据是利用大循环套小循环***************************************重点

        for obj in self.page_queryset:  # 一个个的book对象

            temp = []

            for field_or_func in self.config_obj.new_list_display():

                if callable(field_or_func):
                    val = field_or_func(self.config_obj, obj)
                else:
                    try:
                        from django.db.models.fields.related import ManyToManyField
                        field_obj = self.config_obj.model._meta.get_field(field_or_func)  # 根据字段字符串找到字段对象
                        if isinstance(field_obj, ManyToManyField):
                            rel_data_list = getattr(obj, field_or_func).all()  # 多对多类型

                            l = [str(item) for item in rel_data_list]
                            val = ",".join(l)

                        else:
                            val = getattr(obj, field_or_func)  # 一对多，普通字段
                            if field_or_func in self.config_obj.list_display_links:  # list_display_links
                                _url = self.config_obj.get_change_url(obj)
                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))

                    except Exception as e:
                        val = getattr(obj, field_or_func)  # __str__

                temp.append(val)

            new_data_list.append(temp)

        return new_data_list

    def get_list_filter_links(self):
        list_filter_links = {}

        for field in self.config_obj.list_filter:
            params = copy.deepcopy(self.request.GET)
            # 利用深拷贝把GET请求的到的类字典数据类型改成可变数据类型这样就可以修改其中的内容

            current_field_pk = params.get(field, 0)

            field_obj = self.config_obj.model._meta.get_field(field)  # 获得字段对象

            rel_model = field_obj.rel.to  # 根据字段对象获得相关联的表对象

            rel_model_queryset = rel_model.objects.all()

            temp = []

            for obj in rel_model_queryset:

                params[field] = obj.pk
                if obj.pk == int(current_field_pk):
                    link = "<a class='active' href='?%s'>%s</a>" % (params.urlencode(), str(obj))

                else:
                    link = "<a href='?%s'>%s</a>" % (params.urlencode(), str(obj))

                temp.append(link)

            list_filter_links[field] = temp

        return list_filter_links


# 配置类 (里面有增删改查的视图函数)
class ModelStark(object):
    list_display = ["__str__"]
    model_form_class = []
    list_display_links = []
    search_fields = []
    list_filter = []

    actions = []

    def __init__(self, model):
        self.model = model
        self.model_name = self.model._meta.model_name
        self.app_label = self.model._meta.app_label

    def patch_delete(self, request, queryset):
        queryset.delete()

    patch_delete.desc = "批量删除"





    # 反向解析当前查看表的增删改查的url

    def get_list_url(self):
        url_name = "%s_%s_list" % (self.app_label, self.model_name)
        _url = reverse(url_name)
        return _url

    def get_add_url(self):
        url_name = "%s_%s_add" % (self.app_label, self.model_name)
        _url = reverse(url_name)
        return _url

    def get_change_url(self, obj):
        url_name = "%s_%s_change" % (self.app_label, self.model_name)
        _url = reverse(url_name, args=(obj.pk,))
        return _url

    def get_del_url(self, obj):
        url_name = "%s_%s_delete" % (self.app_label, self.model_name)
        _url = reverse(url_name, args=(obj.pk,))
        return _url





    # 编辑默认（自定义）列（函数）

    def edit(self, obj=None, is_header=False):

        if is_header:
            return "操作"
        return mark_safe("<a href='%s'>编辑</a>" % self.get_change_url(obj))

    def delete(self, obj=None, is_header=False):

        if is_header:
            return "删除"
        return mark_safe("<a href='%s'>删除</a>" % self.get_del_url(obj))

    def checkbox(self, obj=None, is_header=False):
        print(obj)
        if is_header:
            return "选择"
        return mark_safe("<input type='checkbox' name='pk_list' value=%s>" % obj.pk)





    # 封装的一些方法用来获取新的列表
    def new_list_display(self):  # [checkbox,__str__,或"title", "price", "publish", "authors"，edit,delete]
        temp = []

        temp.extend(self.list_display)
        temp.insert(0, ModelStark.checkbox)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.delete)

        return temp

    def get_search_condition(self, request):  # search方法

        val = request.GET.get("q")
        search_condition = Q()
        if val:
            search_condition.connector = "or"

            for field in self.search_fields:
                search_condition.children.append((field + "__icontains", val))
        return search_condition

    def get_filter_condition(self, request):  # filter方法
        filter_condition = Q()

        for key, val in request.GET.items():
            if key in ["page", "q"]:
                continue

            filter_condition.children.append((key, val))
        return filter_condition

    def get_new_form(self, form):
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField
        for bfield in form:
            if isinstance(bfield.field, ModelChoiceField):  # bfield.field获得字段对象（modelform组件）
                bfield.is_pop = True
                print(bfield.name)  # 字段字符串

                rel_model = self.model._meta.get_field(bfield.name).rel.to

                model_name = rel_model._meta.model_name
                app_label = rel_model._meta.app_label
                _url = reverse("%s_%s_add" % (app_label, model_name))
                bfield.url = _url

                bfield.pop_back_id = "id_" + bfield.name

        return form

    def get_model_form(self):  # 有自定义的modelform用自己的，没有就用通用的
        if self.model_form_class:
            return self.model_form_class
        else:
            from django.forms import widgets as wid
            class ModelFormClass(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormClass






    # 每张表的增删改查视图函数
    def listview(self, request):

        # print(self)   某个配置类
        # print(self.model)某个配置类对应的表名

        if request.method == "POST":  # 批量处理路径
            pk_list = request.POST.getlist("pk_list")

            queryset = self.model.objects.filter(pk__in=pk_list)
            action = request.POST.get("action")
            action = getattr(self, action)
            action(request, queryset)

        data_list = self.model.objects.all()
        # print(data_list)

        add_url = self.get_add_url()
        # search_condition = self.get
        # 获取搜素条件对象
        search_condition = self.get_search_condition(request)
        # 获取filter的condition
        filter_condition = self.get_filter_condition(request)
        # 数据过滤

        data_list = data_list.filter(search_condition).filter(filter_condition)

        showlist = ShowList(self, data_list, request)
        return render(request, "stark/list_view.html", locals())


    def addview(self, request):
        ModelFormClass = self.get_model_form()

        if request.method == "POST":

            form = ModelFormClass(request.POST)
            form = self.get_new_form(form)
            if form.is_valid():
                obj = form.save()
                is_pop = request.GET.get("pop")
                if is_pop:
                    text = str(obj)
                    pk = obj.pk

                    return render(request, "stark/pop.html", locals())

                else:

                    return redirect(self.get_list_url())

            return render(request, "stark/add_view.html", locals())

        form = ModelFormClass()

        form = self.get_new_form(form)

        return render(request, "stark/add_view.html", locals())

    def changeview(self, request, id):

        ModelFormClass = self.get_model_form()
        edit_obj = self.model.objects.get(pk=id)
        if request.method == "POST":
            form = ModelFormClass(data=request.POST, instance=edit_obj)  # 更改之后的form组件
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, "stark/change_view.html", locals())

        form = ModelFormClass(instance=edit_obj)
        form = self.get_new_form(form)

        return render(request, "stark/change_view.html", locals())

    def delview(self, request, id):

        if request.method == "POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(self.get_list_url())

        list_url = self.get_list_url()

        return render(request, "stark/del_view.html", locals())

    def extra_url(self):

        return []

    def get_urls(self):

        model_name = self.model._meta.model_name  # 某个配置类对应的表名
        app_lable = self.model._meta.app_label  # 某个配置类对应的app名
        temp = [
            url(r"^$", self.listview, name="%s_%s_list" % (app_lable, model_name)),
            url(r"add/$", self.addview, name="%s_%s_add" % (app_lable, model_name)),
            url(r"(\d+)/change/$", self.changeview, name="%s_%s_change" % (app_lable, model_name)),
            url(r"(\d+)/delete/$", self.delview, name="%s_%s_delete" % (app_lable, model_name))
        ]
        '''
                   temp=[


                       #(1) url(r"app01/book/",BookConfig(Book).urls)
                       #(2) url(r"app01/book/",(BookConfig(Book).get_urls(), None, None))
                       #(3) url(r"app01/book/",([
                                                       url(r"^$", BookConfig(Book).listview),
                                                       url(r"add/$", BookConfig(Book).addview),
                                                       url(r"(\d+)/change/$", BookConfig(Book).changeview),
                                                       url(r"(\d+)/delete/$", BookConfig(Book).delview),
                                                ], None, None))

                       ###########

                       # url(r"app01/publish/",([
                                                       url(r"^$", ModelStark(Publish).listview),
                                                       url(r"add/$",  ModelStark(Publish).addview),
                                                       url(r"(\d+)/change/$",  ModelStark(Publish).changeview),
                                                       url(r"(\d+)/delete/$",  ModelStark(Publish).delview),
                                                ], None, None))



                   ]



            '''

        temp.extend(self.extra_url())
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


# stark组件的全局类
class AdminSite(object):

    def __init__(self):  # 注册的地方
        self._registry = {}

    def register(self, model, admin_class=None):
        if not admin_class:
            admin_class = ModelStark

        self._registry[model] = admin_class(model)

    def get_urls(self):
        temp = []

        # print("admin----->",admin.site._registry)

        for model, config_obj in self._registry.items():
            # print("model", model)
            # print("config_obj", config_obj)
            model_name = model._meta.model_name  # Book表
            app_label = model._meta.app_label  # app名字
            temp.append(url(r"%s/%s/" % (app_label, model_name), config_obj.urls))

        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = AdminSite()
