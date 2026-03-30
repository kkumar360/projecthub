from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('create-admin/', views.create_admin, name='create_admin'),
    
    # Admin/Manager URLs
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-project/', views.create_project, name='create_project'),
    path('create-task/', views.create_task, name='create_task'),
    path('project/<int:project_id>/', views.project_details, name='project_details'),
    path('assign-task/<int:task_id>/', views.assign_task, name='assign_task'),
    path('register-employee/', views.register_employee, name='register_employee'),
    
    # Employee URLs
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/task/<int:task_id>/', views.task_details, name='task_details'),
    path('employee/task/<int:task_id>/update/', views.update_task_status, name='update_task_status'),
]