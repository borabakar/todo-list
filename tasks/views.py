from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task
from .forms import TaskForm
from django.contrib import messages

def is_admin(user):
    return user.is_superuser

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, completed=True)

    # sadece admin veya kendi tamamladığı görevleri silebilir
    if request.user.is_superuser or task.assigned_to == request.user:
        task.delete()
        messages.success(request, "Task deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this task.")

    return redirect('completed_tasks')

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
            task = form.save(commit=False)  # görevi oluştur ama kaydetme
            task.save()  # kaydet (ID oluşturulsun)
            form.save_m2m()  # assigned_to gibi ManyToMany alanları kaydet
            messages.success(request, "New task successfully assigned.")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(completed=True).count()
    incomplete_tasks = Task.objects.filter(completed=False).count()

    priority_high = Task.objects.filter(priority='High').count()
    priority_medium = Task.objects.filter(priority='Medium').count()
    priority_low = Task.objects.filter(priority='Low').count()

    # Kullanıcı başına görev sayısı
    from django.contrib.auth.models import User
    user_task_counts = []
    for user in User.objects.all():
        user_tasks = Task.objects.filter(assigned_to=user).count()
        user_task_counts.append((user.username, user_tasks))

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'incomplete_tasks': incomplete_tasks,
        'priority_high': priority_high,
        'priority_medium': priority_medium,
        'priority_low': priority_low,
        'user_task_counts': user_task_counts,
    }

    return render(request, 'tasks/admin_dashboard.html', context)

@user_passes_test(is_admin)
def incomplete_tasks(request):
    tasks = Task.objects.filter(completed=False)
    return render(request, 'tasks/incomplete_tasks.html', {'tasks': tasks})


@user_passes_test(is_admin)
def all_tasks(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/all_tasks.html', {'tasks': tasks})

@user_passes_test(is_admin)
def calendar_view(request):
    tasks = Task.objects.all()
    events = []

    for task in tasks:
        events.append({
            'title': task.title,
            'start': str(task.due_date),
            'color': '#28a745' if task.completed else '#dc3545',
        })

    return render(request, 'tasks/calendar_view.html', {'events': events})
