from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.task_list, name='task_list'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('completed/', views.completed_tasks, name='completed_tasks'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create/', views.create_task, name='create_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('incomplete/', views.incomplete_tasks, name='incomplete_tasks'),        # ✅ yeni
    path('all-tasks/', views.all_tasks, name='all_tasks'),                        # ✅ yeni
]
