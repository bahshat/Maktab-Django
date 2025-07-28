from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search_student, name='search_student'),
    path('admission/', views.add_student, name='add_student'),
    path('student/<int:roll_number>/', views.student_detail, name='student_detail'),
    path('pending/', views.pending_fees_list, name='pending_fees_list'),
    path('due_soon/', views.due_soon_fees_list, name='due_soon_fees_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
