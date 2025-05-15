from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    # Admin URLs
    path('customadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customadmin/create-teacher/', views.create_teacher, name='create_teacher'),
    path('customadmin/edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('customadmin/create-student/', views.create_student, name='create_student'),
    path('customadmin/create-class/', views.create_class, name='create_class'),
    path('customadmin/create-lesson/', views.create_lesson, name='create_lesson'),
    path('customadmin/create-subject/', views.create_subject, name='create_subject'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-grade/', views.add_grade, name='add_grade'),
    path('teacher/mark-attendance/<int:class_id>/<int:subject_id>/', views.mark_attendance, name='mark_attendance'),
    path('teacher/add-grade-bulk/<int:class_id>/<int:subject_id>/', views.add_grade_bulk, name='add_grade_bulk'),
    path('teacher/create-schedule/', views.create_schedule, name='create_schedule'),
    path('teacher/class/<int:class_id>/', views.view_class, name='view_class'),
    path('teacher/subject/<int:subject_id>/', views.view_subject, name='view_subject'),
    path('teacher/edit-grade/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    path('teacher/delete-grade/<int:grade_id>/', views.delete_grade, name='delete_grade'),
    path('teacher/edit-or-add-schedule/', views.edit_or_add_schedule, name='edit_or_add_schedule'),
    path('teacher/delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('teacher/homework/', views.teacher_homework_list, name='teacher_homework_list'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('schedule/', views.view_schedule, name='view_schedule'),
    
    # API URLs
    path('api/lessons-by-class/<int:class_id>/', views.get_lessons_by_class, name='get_lessons_by_class'),
] 