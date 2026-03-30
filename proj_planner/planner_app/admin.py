from django.contrib import admin

from .models import Admin, Employee, Project, Task
admin.site.register(Admin)
admin.site.register(Employee)   
admin.site.register(Project)
admin.site.register(Task)
# Register your models here.
