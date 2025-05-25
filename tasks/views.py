from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task
from .forms import TaskForm
from django.contrib import messages

def is_admin(user):
    return user.is_superuser

@login_required
def task_list(request):
    if request.user.is_superuser:
        # Admin: get all incomplete tasks
        base_tasks_query = Task.objects.filter(completed=False)
    else:
        # Regular user: get only assigned incomplete tasks
        base_tasks_query = Task.objects.filter(assigned_to=request.user, completed=False)

    # Filter tasks by priority
    tasks_high = base_tasks_query.filter(priority='High')
    tasks_medium = base_tasks_query.filter(priority='Medium')
    tasks_low = base_tasks_query.filter(priority='Low')

    categorized_tasks = [
        {'category': 'High Priority', 'color': 'danger', 'tasks': tasks_high},
        {'category': 'Medium Priority', 'color': 'warning', 'tasks': tasks_medium},
        {'category': 'Low Priority', 'color': 'success', 'tasks': tasks_low},
    ]

    return render(request, 'tasks/task_list.html', {
        'categorized_tasks': categorized_tasks,
        'user': request.user
    })

@login_required
def complete_task(request, task_id):
    # Admins can complete any task, regular users only their own
    if request.user.is_superuser:
        task = get_object_or_404(Task, id=task_id)
    else:
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    task.completed = True
    task.save()
    messages.success(request, "Task marked as completed.")
    return redirect('task_list')

@login_required
def completed_tasks(request):
    if request.user.is_superuser:
        tasks = Task.objects.filter(completed=True)
    else:
        tasks = Task.objects.filter(assigned_to=request.user, completed=True)

    return render(request, 'tasks/completed_tasks.html', {'tasks': tasks})

@user_passes_test(is_admin)
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New task successfully assigned.")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})

