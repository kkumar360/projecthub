from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Admin, Employee, Project, Task, Activity
from .forms import ProjectForm, TaskForm, TaskStatusForm, RegisterEmployeeForm, LoginForm


# Helper function to calculate project progress
def get_project_progress(project):
    """Calculate percentage of completed tasks in project"""
    total = project.tasks.count()
    if total == 0:
        return 0
    completed = project.tasks.filter(status='completed').count()
    return round((completed / total) * 100)


def log_activity(username, action_type, project=None, task=None, description=''):
    """Log user activity"""
    Activity.objects.create(
        action_type=action_type,
        username=username,
        project=project,
        task=task,
        description=description
    )


# Home and Authentication Views
def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        if user_type == 'admin':
            admin = Admin.objects.filter(username=username).first()
            if admin and check_password(password, admin.password_hash):
                request.session['user_id'] = admin.id
                request.session['user_type'] = 'admin'
                request.session['username'] = admin.username
                request.session['dark_mode'] = admin.dark_mode
                log_activity(admin.username, 'login', description=f'{admin.username} logged in')
                return redirect('admin_dashboard')
        else:
            employee = Employee.objects.filter(username=username).first()
            if employee and check_password(password, employee.password_hash):
                request.session['user_id'] = employee.id
                request.session['user_type'] = 'employee'
                request.session['username'] = employee.username
                request.session['dark_mode'] = employee.dark_mode
                log_activity(employee.username, 'login', description=f'{employee.username} logged in')
                return redirect('employee_dashboard')
        
        return render(request, 'home.html', {'error': 'Invalid credentials'})
    
    return render(request, 'home.html')


def logout(request):
    request.session.flush()
    return redirect('home')


def create_admin(request):
    """Create a new admin account from login page"""
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([admin_id, username, password, confirm_password]):
            return render(request, 'home.html', {'error': 'All fields are required'})
        
        if len(password) < 6:
            return render(request, 'home.html', {'error': 'Password must be at least 6 characters'})
        
        if password != confirm_password:
            return render(request, 'home.html', {'error': 'Passwords do not match'})
        
        if Admin.objects.filter(username=username).exists():
            return render(request, 'home.html', {'error': f'Username "{username}" already exists'})
        
        if Admin.objects.filter(admin_id=admin_id).exists():
            return render(request, 'home.html', {'error': f'Admin ID "{admin_id}" already exists'})
        
        # Create admin
        from django.contrib.auth.hashers import make_password
        try:
            admin = Admin.objects.create(
                admin_id=admin_id,
                username=username,
                password_hash=make_password(password),
                type='admin'
            )
            log_activity(username, 'login', description=f'Admin account "{username}" created')
            return render(request, 'home.html', {'success': f'✅ Admin account "{username}" created successfully! You can now login.'})
        except Exception as e:
            return render(request, 'home.html', {'error': f'Error creating admin: {str(e)}'})
    
    return redirect('home')


# Admin Views
def admin_dashboard(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    admin_id = request.session.get('user_id')
    admin = Admin.objects.get(id=admin_id)
    projects = Project.objects.filter(created_by=admin)
    employees = Employee.objects.all()
    
    # Prepare employee data with task counts
    employee_data = []
    for emp in employees:
        employee_data.append({
            'employee': emp,
            'total_tasks': emp.tasks.count(),
            'completed_tasks': emp.tasks.filter(status='completed').count()
        })
    
    # Add project progress
    project_data = []
    for proj in projects:
        project_data.append({
            'project': proj,
            'progress': get_project_progress(proj),
            'total_tasks': proj.tasks.count(),
            'completed_tasks': proj.tasks.filter(status='completed').count(),
        })
    
    # Get recent activities
    recent_activities = Activity.objects.all()[:10]
    
    context = {
        'admin': admin,
        'projects': projects,
        'project_data': project_data,
        'employees': employees,
        'employee_data': employee_data,
        'total_projects': projects.count(),
        'total_employees': employees.count(),
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_dashboard.html', context)


def create_project(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            admin = Admin.objects.get(id=request.session.get('user_id'))
            project.created_by = admin
            project.save()
            log_activity(admin.username, 'project_created', project=project, description=f'Created project "{project.project_title}"')
            return redirect('admin_dashboard')
    else:
        form = ProjectForm()
    
    return render(request, 'create_project.html', {'form': form})


def create_task(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    admin = Admin.objects.get(id=request.session.get('user_id'))
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            admin = Admin.objects.get(id=request.session.get('user_id'))
            log_activity(admin.username, 'task_created', project=task.project, task=task, description=f'Created task "{task.task_title}"')
            return redirect('admin_dashboard')
    else:
        form = TaskForm()
        form.fields['project'].queryset = Project.objects.filter(created_by=admin)
    
    return render(request, 'create_task.html', {'form': form})


def assign_task(request, task_id):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    task = get_object_or_404(Task, id=task_id)
    admin = Admin.objects.get(id=request.session.get('user_id'))
    
    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            old_employee = task.assigned_to
            form.save()
            if old_employee != form.cleaned_data.get('assigned_to'):
                log_activity(admin.username, 'task_assigned', task=task, description=f'Assigned "{task.task_title}" to {task.assigned_to.username if task.assigned_to else "Unassigned"}')
            else:
                log_activity(admin.username, 'task_updated', task=task, description=f'Updated task "{task.task_title}"')
            return redirect('admin_dashboard')
    else:
        form = TaskStatusForm(instance=task)
    
    return render(request, 'assign_task.html', {'task': task, 'form': form})


def project_details(request, project_id):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    
    # Make sure admin that created the project can access it
    if project.created_by.id != request.session.get('user_id'):
        return redirect('admin_dashboard')
    
    context = {
        'project': project,
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'in_progress_tasks': tasks.filter(status='in_progress').count(),
        'completed_tasks': tasks.filter(status='completed').count(),
    }
    return render(request, 'project_details.html', context)


def register_employee(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RegisterEmployeeForm()
    
    return render(request, 'register_employee.html', {'form': form})


# Employee Views
def employee_dashboard(request):
    if request.session.get('user_type') != 'employee':
        return redirect('home')
    
    employee = Employee.objects.get(id=request.session.get('user_id'))
    tasks = Task.objects.filter(assigned_to=employee)
    projects = Project.objects.filter(tasks__assigned_to=employee).distinct()
    
    context = {
        'employee': employee,
        'tasks': tasks,
        'projects': projects,
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'in_progress_tasks': tasks.filter(status='in_progress').count(),
        'completed_tasks': tasks.filter(status='completed').count(),
    }
    return render(request, 'employee_dashboard.html', context)


def task_details(request, task_id):
    if request.session.get('user_type') != 'employee':
        return redirect('home')
    
    employee = Employee.objects.get(id=request.session.get('user_id'))
    task = get_object_or_404(Task, id=task_id)
    
    # Make sure employee assigned to the task can access it
    if task.assigned_to.id != employee.id:
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        old_status = task.status
        status = request.POST.get('status')
        task.status = status
        task.save()
        if old_status != 'completed' and status == 'completed':
            log_activity(employee.username, 'task_completed', task=task, description=f'Completed task "{task.task_title}"')
        else:
            log_activity(employee.username, 'task_updated', task=task, description=f'Updated task "{task.task_title}" status')
        return redirect('employee_dashboard')
    
    context = {
        'task': task,
        'project': task.project,
    }
    return render(request, 'task_details.html', context)


def update_task_status(request, task_id):
    if request.session.get('user_type') != 'employee':
        return redirect('home')
    
    employee = Employee.objects.get(id=request.session.get('user_id'))
    task = get_object_or_404(Task, id=task_id)
    
    # Make sure employee assigned to the task can update it
    if task.assigned_to.id != employee.id:
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_details', task_id=task.id)
    else:
        form = TaskStatusForm(instance=task)
    
    return render(request, 'update_task_status.html', {'task': task, 'form': form})