"""
URL configuration for ticket_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create/', views.create_ticket, name='create_ticket'),
    path('list/', views.ticket_list, name='ticket_list'),
    path('all/', views.all_tickets, name='all_tickets'),
    path('escalated/', views.escalated_tickets, name='escalated_tickets'),
    path('detail/<int:id>/', views.ticket_detail, name='ticket_detail'),
    path('dashboard/departments/', views.department_list, name='department_list'),
    path('dashboard/departments/edit/<int:id>/', views.edit_department, name='edit_department'),
    path('dashboard/departments/delete/<int:id>/', views.delete_department, name='delete_department'),
    path('assign/<int:ticket_id>/', views.assign_ticket, name='assign_ticket'),
    path('staff/', views.staff_tickets, name='staff_tickets'),
    path('update/<int:ticket_id>/', views.update_ticket_status, name='update_ticket_status'),
    path('escalate/<int:ticket_id>/', views.escalate_ticket, name='escalate_ticket'),
    path('edit/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('ai-prediction/', views.ai_prediction, name='ai_prediction'),
]
