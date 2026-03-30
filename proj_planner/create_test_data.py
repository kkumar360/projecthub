import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj_planner.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from planner_app.models import Admin, Employee, Project, Task

# Create test admin
admin, created = Admin.objects.get_or_create(
    username='admin1',
    defaults={
        'admin_id': 'ADM001',
        'password_hash': make_password('admin123'),
        'type': 'admin'
    }
)
print(f"Admin created: {created}, {admin.username}")

# Create test employees
employees_data = [
    {'username': 'employee1', 'employee_id': 'EMP001'},
    {'username': 'employee2', 'employee_id': 'EMP002'},
    {'username': 'employee3', 'employee_id': 'EMP003'},
]

for emp_data in employees_data:
    employee, created = Employee.objects.get_or_create(
        username=emp_data['username'],
        defaults={
            'employee_id': emp_data['employee_id'],
            'password_hash': make_password('emp123'),
            'type': 'employee'
        }
    )
    print(f"Employee created: {created}, {employee.username}")

# Create test projects
project1, created = Project.objects.get_or_create(
    project_id='PROJ001',
    defaults={
        'project_title': 'E-Commerce Website',
        'created_by': admin
    }
)
print(f"Project created: {created}, {project1.project_title}")

project2, created = Project.objects.get_or_create(
    project_id='PROJ002',
    defaults={
        'project_title': 'Mobile App Development',
        'created_by': admin
    }
)
print(f"Project created: {created}, {project2.project_title}")

# Create test tasks
task_data = [
    {
        'task_id': 'TASK001',
        'task_title': 'Design Database Schema',
        'task_description': 'Create the ER diagram and database schema',
        'project': project1,
        'assigned_to': Employee.objects.get(username='employee1')
    },
    {
        'task_id': 'TASK002',
        'task_title': 'Set up Backend API',
        'task_description': 'Develop REST API endpoints',
        'project': project1,
        'assigned_to': Employee.objects.get(username='employee2')
    },
    {
        'task_id': 'TASK003',
        'task_title': 'Frontend UI Development',
        'task_description': 'Create responsive UI with Bootstrap',
        'project': project1,
        'assigned_to': Employee.objects.get(username='employee3')
    },
    {
        'task_id': 'TASK004',
        'task_title': 'App Architecture Design',
        'task_description': 'Design MVVM architecture',
        'project': project2,
        'assigned_to': Employee.objects.get(username='employee1')
    },
]

for task in task_data:
    t, created = Task.objects.get_or_create(
        task_id=task['task_id'],
        defaults={
            'task_title': task['task_title'],
            'task_description': task['task_description'],
            'project': task['project'],
            'assigned_to': task['assigned_to'],
            'status': 'pending'
        }
    )
    print(f"Task created: {created}, {t.task_title}")

print("\n✅ Test data created successfully!")
print("\nYou can now login with:")
print("Admin: username=admin1, password=admin123")
print("Employee: username=employee1, password=emp123")
