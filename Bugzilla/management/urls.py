from django.urls import path
from .views import signupForm, loginForm
from .views import projectcreate, allproject, deleteproject,assigndeveloper, assigndeveloperdetail, logoutaccount
from .views import editproject, createbug, reportbug, qa_bug_list
from .views import edit_bug, delete_bug, assignqa, assignqadetail, allprojectq
from .views import dischargedeveloperdetail, dischargedeveloper, dischargeqadetail, dischargeqa
from .views import developer_bug_list, assign_bug_to_self, home, resolve_bug_to_self, notaccess
urlpatterns = [
    path('signupaccount',signupForm,name="signup form"),
    path('loginaccount',  loginForm,name="login form"),
    path('',home,name="home"),
    path('notaccess',notaccess,name="not access"),
    path('createproject', projectcreate, name='create project'),
    path('projects',allproject,name="all projects"),
    path('projectsq',allprojectq,name="all projects"),
    path('delete/<str:name>',deleteproject,name="delete project"),
    path('assigndeveloperdetail/<str:name>',assigndeveloperdetail,name="assign developer detail"),
    path('assigndeveloper/<str:name>',assigndeveloper,name="assign developer"),
    path('dischargedeveloperdetail/<str:name>',dischargedeveloperdetail,name="discharge developer detail"),
    path('dischargedeveloper/<str:name>',dischargedeveloper,name="discharge developer"),
    path('dischargeqadetail/<str:name>',dischargeqadetail,name="discharge qa detail"),
    path('dischargeqa/<str:name>',dischargeqa,name="discharge qa"),
    path('edit/<str:name>/', editproject, name='editproject'),
    path('newbug',createbug,name="new bug"),
    path('reportbug/<str:name>',reportbug,name="project bug"),
    path('qabugs/', qa_bug_list, name="qa_bug_list"),
    path('editbug/<uuid:pk>', edit_bug, name='edit bug'),
    path('deletebug/<uuid:pk>', delete_bug, name='delete bug'),
    path('assignqadetail/<str:name>',assignqadetail,name="assign qa detail"),
    path('assignqa/<str:name>',assignqa,name="assign qa"),
    path('assign_bug/<uuid:bug_id>/', assign_bug_to_self, name='assign_bug_to_self'),
    path('resolve_bug/<uuid:bug_id>/', resolve_bug_to_self, name='resolve_bug_to_self'),
    path('developer_bugs/', developer_bug_list, name='developer_bug_list'),
    path('logoutaccount', logoutaccount, name="logout")


]
