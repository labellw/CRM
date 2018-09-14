from .models import *
from stark.service.sites import site,ModelStark
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.http import JsonResponse
from django.shortcuts import HttpResponse,redirect,render



site.register(School)
site.register(Order)
site.register(UserInfo)

class ClassConfig(ModelStark):
    list_display = ["course","semester","teachers","tutor"]

site.register(ClassList,ClassConfig)


class CustomerConfig(ModelStark):
    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"

        return obj.get_gender_display()

    def display_course(self,obj=None,is_header=False):
        if is_header:
            return "咨询课程"

        link_list=[]

        for course in obj.course.all():
            s="<a>%s</a>"%course.name
            link_list.append(s)

        return mark_safe(" ".join(link_list))

    list_display = ["name",display_gender,"consultant",display_course]

site.register(Customer,CustomerConfig)

class StudentConfig(ModelStark):
    def display_score(self,obj=None,is_header=False):
        if is_header:
            return "详细信息"

        return mark_safe("<a href='/stark/app01/student/%s/info'>详细信息</a>"%obj.pk)

    def student_info(self,request,sid):

        if request.is_ajax():
            cid =request.GET.get("cid")

            #查询学生sid在班级cid下的所有的学生学习记录对象

            studentstudyrecord_list = StudentStudyRecord.objects.filter(student_id=sid,classstudyrecord__class_obj=cid)

            ret = [["day%s"%studentstudyrecord.classstudyrecord.day_num,studentstudyrecord.score] for studentstudyrecord in studentstudyrecord_list]
            print(ret)


            return JsonResponse(ret,safe=False)

        student_obj = Student.objects.filter(pk=sid).first()
        class_list= student_obj.class_list.all()

        return render(request,"student_info.html",locals())

    def extra_url(self):
        temp =[]

        temp.append(url("(\d+)/info/",self.student_info))

        return temp

    list_display= ["customer","class_list",display_score]





site.register(Student,StudentConfig)
site.register(ConsultRecord)

class ClassStudyRecordConfig(ModelStark):
    def record_score(self,request,cls_record_id):
        if request.is_ajax():
            action=request.POST.get("action")
            sid = request.POST.get("sid")
            val = request.POST.get("val")
            # 方式1：
            # if action == "score":
            #     StudentStudyRecord.objects.filter(pk=sid).update(score=val)
            #
            # else:
            #     StudentStudyRecord.objects.filter(pk=sid).update(homework_note=val)
            # 方式2：
            StudentStudyRecord.objects.filter(pk=sid).update(**{action:val})

            return HttpResponse("OK")
        if request.method == "POST":
            # <QueryDict: {'score_1': ['50'], 'homework_note_1': ['12323'], 'score_2': ['80'], 'homework_note_2': ['456']}>
            print(request.POST)
            dic={}

            for key,val in request.POST.items():
                field,pk = key.rsplit("_",1)

                if pk in dic:
                    dic[pk][field] = val

                else:
                    dic[pk] = {field:val}

            for pk,update_data in dic.items():
                StudentStudyRecord.objects.filter(pk=pk).update(**update_data)

            '''难点构造数据结构 减少数据库操作,一个同学添加一次数据库
            想办法构造以下数据结构
                       {
                         1:{score:50,homework_note:12323},
                         2:{score:80,homework_note:456},
                       }

                       '''
            # StudentStudyRecord.objects.filter(pk=pk).update(**{field:val})
            return redirect(request.path)

        #     班级学习记录对象
        cls_record = ClassStudyRecord.objects.get(pk=cls_record_id)

        #     该班级学习记录对象关联的所有的学生学习记录对象
        studentstudyrecord_list = cls_record.studentstudyrecord_set.all()
        print("studentstudyrecord_list",studentstudyrecord_list)

        score_choices = StudentStudyRecord.score_choices

        return render(request,"record_score.html",locals())

    def extra_url(self):

        temp = []

        temp.append(url("(\d+)/record_score/",self.record_score))

        return temp





    def display_info(self,obj=None,is_header=False):

        if is_header:
            return "详细信息"

        return mark_safe("<a href='/stark/app01/studentstudyrecord/?classstudyrecord=%s'>详细信息</a>"%obj.pk)
    def handle_score(self, obj=None, is_header=False):
        if is_header:
            return "录入成绩"

        return mark_safe("<a href='/stark/app01/classstudyrecord/%s/record_score/'>录入成绩</a>"%(obj.pk,))
    list_display = ["class_obj","day_num","teacher","homework_title",display_info,handle_score]

    def patch_init(self,request,queryset):#此queryset是班级课程对象

        for cls_study_obj in queryset:

            #查询班级关联的所有的学生
            student_list = cls_study_obj.class_obj.student_set.all()

            ssr_list=[]
            for student in student_list:
                ssr = StudentStudyRecord(student=student,classstudyrecord=cls_study_obj)
                ssr_list.append(ssr)

            StudentStudyRecord.objects.bulk_create(ssr_list) #批量创建

    patch_init.desc = "创建关联学生学习记录"
    actions = [patch_init]

site.register(ClassStudyRecord,ClassStudyRecordConfig)


class StudentStudyRecordConfig(ModelStark):


    def edit_record(self,request,id):

        print(id)
        print(request.POST.get("record"))
        record = request.POST.get("record")

        StudentStudyRecord.objects.filter(pk=id).update(record=record)


        return HttpResponse("okokokokokokokokok")

    def extra_url(self):

        temp=[]

        temp.append(url(r"(\d+)/edit_record/$",self.edit_record),)

        return temp

    def display_record(self,obj=None,is_header=False):

        if is_header:
            return "出勤"

        html ="<select name='record' class='record' pk = %s>"%obj.pk
        for item in StudentStudyRecord.record_choices:

            if obj.record == item[0]:

                option="<option selected value='%s'>%s</option>"%(item[0],item[1])

            else:
                option="<option value='%s'>%s</option>"%(item[0],item[1])

            html += option

        html+="</select>"


        return mark_safe(html)

    def display_score(self,obj=None, is_header=False):
        if is_header:
            return "成绩"

        return obj.get_score_display()
    list_display = ["student","classstudyrecord",display_record,display_score]

    def patch_late(self,request,queryset):
        queryset.update(record="late")

    patch_late.desc = "迟到"

    actions = [patch_late]



site.register(StudentStudyRecord,StudentStudyRecordConfig)

site.register(Department)

site.register(Course)

