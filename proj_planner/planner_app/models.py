from django.db import models


class Planner(models.Model):
    username = models.CharField(max_length=10, unique=True)
    password_hash = models.CharField(max_length=128)
    type = models.CharField(max_length=10)  # 'admin' or 'employee'
    dark_mode = models.BooleanField(default=False)  # Dark mode toggle
    class Meta:
        abstract = True  

class Admin(Planner):
    admin_id = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.username} (Admin)"

class Employee(Planner):
    employee_id = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.employee_id})"

class Project(models.Model):
    project_id = models.CharField(max_length=10, unique=True)
    project_title = models.CharField(max_length=100)
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.project_title

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    task_id = models.CharField(max_length=10, unique=True)
    task_title = models.CharField(max_length=100)
    task_description = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')  # New priority field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_title
    
    def get_priority_color(self):
        """Return color badge for priority"""
        colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#dc3545'}
        return colors.get(self.priority, '#6c757d')


class Activity(models.Model):
    """Track user actions for activity timeline"""
    ACTION_CHOICES = [
        ('project_created', '📁 Project Created'),
        ('task_created', '✅ Task Created'),
        ('task_assigned', '👤 Task Assigned'),
        ('task_updated', '🔄 Task Updated'),
        ('task_completed', '🎉 Task Completed'),
        ('login', '🚪 User Login'),
    ]
    
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    username = models.CharField(max_length=100)  # Store username as string
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.username}"