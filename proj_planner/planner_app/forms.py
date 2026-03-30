from django import forms
from django.contrib.auth.hashers import make_password
from .models import Project, Task, Employee, Admin


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_id', 'project_title']
        widgets = {
            'project_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Project ID'}),
            'project_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Project Title'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_id', 'task_title', 'task_description', 'project', 'assigned_to', 'priority']
        widgets = {
            'task_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Task ID'}),
            'task_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Task Title'}),
            'task_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Task Description'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['assigned_to', 'status', 'priority']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }


class RegisterEmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        min_length=6
    )
    
    class Meta:
        model = Employee
        fields = ['username', 'employee_id']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.password_hash = make_password(self.cleaned_data['password'])
        employee.type = 'employee'
        if commit:
            employee.save()
        return employee


class LoginForm(forms.Form):
    username = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))