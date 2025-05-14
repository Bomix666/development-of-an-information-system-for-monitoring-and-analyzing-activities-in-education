from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime, timedelta

@login_required
def login_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'teacher'):
        return redirect('teacher_dashboard')
    elif hasattr(request.user, 'student'):
        return redirect('student_dashboard')
    else:
        messages.error(request, 'Invalid user role')
        return redirect('login')

def is_admin(user):
    return user.is_staff

def is_teacher(user):
    return hasattr(user, 'teacher')

def is_student(user):
    return hasattr(user, 'student')

# Admin views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    teachers = Teacher.objects.all()
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'diary/admin/dashboard.html', {
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects
    })

@login_required
@user_passes_test(is_admin)
def create_teacher(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        teacher = Teacher.objects.create(user=user)
        teacher.subjects.set(request.POST.getlist('subjects'))
        teacher.classes.set(request.POST.getlist('classes'))
        
        messages.success(request, 'Teacher created successfully!')
        return redirect('admin_dashboard')
    
    subjects = Subject.objects.all()
    classes = Class.objects.all()
    return render(request, 'diary/admin/create_teacher.html', {
        'subjects': subjects,
        'classes': classes
    })

@login_required
@user_passes_test(is_admin)
def create_class(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        year = request.POST.get('year')
        Class.objects.create(name=name, year=year)
        messages.success(request, 'Class created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'diary/admin/create_class.html')

@login_required
@user_passes_test(is_admin)
def create_lesson(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subject_id = request.POST.get('subject')
        description = request.POST.get('description')
        
        subject = get_object_or_404(Subject, id=subject_id)
        Lesson.objects.create(
            name=name,
            subject=subject,
            description=description
        )
        messages.success(request, 'Lesson created successfully!')
        return redirect('admin_dashboard')
    
    subjects = Subject.objects.all()
    return render(request, 'diary/admin/create_lesson.html', {
        'subjects': subjects
    })

@login_required
@user_passes_test(is_admin)
def create_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Subject.objects.create(name=name)
        messages.success(request, 'Subject created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'diary/admin/create_subject.html')

@login_required
@user_passes_test(is_admin)
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        # Update user information
        user = teacher.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        if request.POST.get('password'):  # Only update password if provided
            user.set_password(request.POST.get('password'))
        user.save()
        
        # Update teacher's subjects and classes
        teacher.subjects.set(request.POST.getlist('subjects'))
        teacher.classes.set(request.POST.getlist('classes'))
        
        messages.success(request, 'Teacher updated successfully!')
        return redirect('admin_dashboard')
    
    subjects = Subject.objects.all()
    classes = Class.objects.all()
    return render(request, 'diary/admin/edit_teacher.html', {
        'teacher': teacher,
        'subjects': subjects,
        'classes': classes
    })

@login_required
@user_passes_test(is_admin)
def create_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        class_id = request.POST.get('class_group')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        class_group = get_object_or_404(Class, id=class_id)
        Student.objects.create(user=user, class_group=class_group)
        
        messages.success(request, 'Student created successfully!')
        return redirect('admin_dashboard')
    
    classes = Class.objects.all()
    return render(request, 'diary/admin/create_student.html', {
        'classes': classes
    })

# Teacher views
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher = request.user.teacher
    classes = teacher.classes.all()
    subjects = teacher.subjects.all()
    
    # Get today's schedule
    today = datetime.now()
    today_schedule = Schedule.objects.filter(
        teacher=teacher,
        day_of_week=today.weekday() + 1  # Convert Monday=0 to Monday=1
    ).order_by('lesson_number')
    
    return render(request, 'diary/teacher/dashboard.html', {
        'classes': classes,
        'subjects': subjects,
        'today_schedule': today_schedule
    })

@login_required
@user_passes_test(is_teacher)
def add_grade(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject')
        value = request.POST.get('grade')
        date = request.POST.get('date')
        
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        Grade.objects.create(
            student=student,
            subject=subject,
            value=value,
            date=date,
            teacher=request.user.teacher
        )
        messages.success(request, 'Grade added successfully!')
        return redirect('view_class', class_id=student.class_group.id)
    
    return redirect('teacher_dashboard')

@login_required
@user_passes_test(is_teacher)
def mark_attendance(request, class_id, subject_id):
    class_group = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    students = class_group.students.all()
    
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            Attendance.objects.create(
                student=student,
                subject=subject,
                date=date,
                status=status,
                teacher=request.user.teacher
            )
        messages.success(request, 'Attendance marked successfully!')
        return redirect('teacher_dashboard')
    
    return render(request, 'diary/teacher/mark_attendance.html', {
        'students': students,
        'subject': subject
    })

@login_required
@user_passes_test(is_teacher)
def create_schedule(request):
    if request.method == 'POST':
        class_group = get_object_or_404(Class, id=request.POST.get('class_group'))
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        day_of_week = request.POST.get('day_of_week')
        lesson_number = request.POST.get('lesson_number')
        
        Schedule.objects.create(
            class_group=class_group,
            subject=subject,
            teacher=request.user.teacher,
            day_of_week=day_of_week,
            lesson_number=lesson_number
        )
        messages.success(request, 'Schedule created successfully!')
        return redirect('teacher_dashboard')
    
    classes = request.user.teacher.classes.all()
    subjects = request.user.teacher.subjects.all()
    return render(request, 'diary/teacher/create_schedule.html', {
        'classes': classes,
        'subjects': subjects
    })

@login_required
@user_passes_test(is_teacher)
def add_grade_bulk(request, class_id, subject_id):
    if request.method == 'POST':
        class_group = get_object_or_404(Class, id=class_id)
        subject = get_object_or_404(Subject, id=subject_id)
        teacher = request.user.teacher
        
        # Get today's date
        today = datetime.now().date()
        
        # Process grades for each student
        for student in class_group.students.all():
            grade_value = request.POST.get(f'grade_{student.id}')
            
            if grade_value:  # Only create grade if a value was selected
                Grade.objects.create(
                    student=student,
                    subject=subject,
                    value=grade_value,
                    date=today,
                    teacher=teacher
                )
        
        messages.success(request, 'Оценки успешно добавлены!')
        return redirect('teacher_dashboard')
    
    return redirect('teacher_dashboard')

@login_required
@user_passes_test(is_teacher)
def view_class(request, class_id):
    class_group = get_object_or_404(Class, id=class_id)
    teacher = request.user.teacher
    students = class_group.students.all()
    
    # Get subjects that this teacher teaches to this class
    subjects = Subject.objects.filter(
        schedule__class_group=class_group,
        schedule__teacher=teacher
    ).distinct()
    
    # Get grades and attendance for each student
    student_data = []
    for student in students:
        grades = Grade.objects.filter(student=student).order_by('-date')[:5]
        attendance = Attendance.objects.filter(student=student).order_by('-date')[:5]
        student_data.append({
            'student': student,
            'grades': grades,
            'attendance': attendance
        })
    
    return render(request, 'diary/teacher/view_class.html', {
        'class_group': class_group,
        'student_data': student_data,
        'subjects': subjects,
        'today': datetime.now().date()
    })

@login_required
@user_passes_test(is_teacher)
def view_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    teacher = request.user.teacher
    
    # Get classes where this subject is taught
    classes = Class.objects.filter(schedule__subject=subject, schedule__teacher=teacher).distinct()
    
    # Get all grades for this subject
    grades = Grade.objects.filter(subject=subject, teacher=teacher).order_by('-date')
    
    # Get all attendance records for this subject
    attendance = Attendance.objects.filter(subject=subject, teacher=teacher).order_by('-date')
    
    return render(request, 'diary/teacher/view_subject.html', {
        'subject': subject,
        'classes': classes,
        'grades': grades,
        'attendance': attendance
    })

@login_required
@user_passes_test(is_teacher)
def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        value = request.POST.get('grade')
        date = request.POST.get('date')
        if value and date:
            grade.value = value
            grade.date = date
            grade.save()
            messages.success(request, 'Оценка успешно изменена!')
            return redirect('teacher_dashboard')
    return render(request, 'diary/teacher/edit_grade.html', {'grade': grade})

@login_required
@user_passes_test(is_teacher)
def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Оценка удалена!')
        return redirect('teacher_dashboard')
    return render(request, 'diary/teacher/delete_grade.html', {'grade': grade})

# Student views
@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = request.user.student
    grades = Grade.objects.filter(student=student).order_by('-date')[:10]  # Last 10 grades
    attendance_list = Attendance.objects.filter(student=student).order_by('-date')[:10]  # Last 10 attendance records
    
    # Get current week's dates
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    week_dates = [monday + timedelta(days=i) for i in range(6)]  # Monday to Saturday
    
    # Get schedule
    schedules = Schedule.objects.filter(class_group=student.class_group).order_by('day_of_week', 'lesson_number')
    
    # Create weekly schedule with grades and attendance
    weekly_schedule = []
    for lesson in range(1, 9):  # 8 lessons
        row = []
        for day in range(1, 7):  # Monday to Saturday
            day_schedules = schedules.filter(day_of_week=day, lesson_number=lesson)
            day_data = []
            for schedule in day_schedules:
                # Get grade for this lesson
                grade = Grade.objects.filter(
                    student=student,
                    subject=schedule.subject,
                    date=week_dates[day-1].date()
                ).first()
                
                # Get attendance for this lesson
                attendance = Attendance.objects.filter(
                    student=student,
                    subject=schedule.subject,
                    date=week_dates[day-1].date()
                ).first()
                
                day_data.append({
                    'schedule': schedule,
                    'grade': grade,
                    'attendance': attendance,
                    'date': week_dates[day-1].date()
                })
            row.append(day_data)
        weekly_schedule.append(row)
    
    return render(request, 'diary/student/dashboard.html', {
        'grades': grades,
        'attendance_list': attendance_list,
        'weekly_schedule': weekly_schedule,
        'week_dates': week_dates,
        'today': today.date()
    })

@login_required
def view_schedule(request):
    if is_teacher(request.user):
        teacher = Teacher.objects.get(user=request.user)
        schedules = Schedule.objects.filter(teacher=teacher).order_by('day_of_week', 'lesson_number')
        # Create a schedule matrix
        schedule_matrix = []
        for lesson in range(1, 9):  # 8 lessons
            row = []
            for day in range(1, 7):  # Monday to Saturday
                lesson_schedules = schedules.filter(day_of_week=day, lesson_number=lesson)
                row.append(lesson_schedules)
            schedule_matrix.append(row)

        context = {
            'schedule_matrix': schedule_matrix,
        }
        return render(request, 'diary/schedule.html', context)
    elif is_student(request.user):
        student = Student.objects.get(user=request.user)
        schedules = Schedule.objects.filter(class_group=student.class_group).order_by('day_of_week', 'lesson_number')
        
        # Get current week's dates
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        week_dates = [monday + timedelta(days=i) for i in range(6)]  # Monday to Saturday
        
        # Create weekly schedule with grades and attendance
        weekly_schedule = []
        for lesson in range(1, 9):  # 8 lessons
            row = []
            for day in range(1, 7):  # Monday to Saturday
                day_schedules = schedules.filter(day_of_week=day, lesson_number=lesson)
                day_data = []
                for schedule in day_schedules:
                    # Get grade for this lesson
                    grade = Grade.objects.filter(
                        student=student,
                        subject=schedule.subject,
                        date=week_dates[day-1].date()
                    ).first()
                    
                    # Get attendance for this lesson
                    attendance = Attendance.objects.filter(
                        student=student,
                        subject=schedule.subject,
                        date=week_dates[day-1].date()
                    ).first()
                    
                    day_data.append({
                        'schedule': schedule,
                        'grade': grade,
                        'attendance': attendance,
                        'date': week_dates[day-1].date()
                    })
                row.append(day_data)
            weekly_schedule.append(row)

        context = {
            'weekly_schedule': weekly_schedule,
            'week_dates': week_dates,
        }
        return render(request, 'diary/student_schedule.html', context)
    else:
        messages.error(request, 'You do not have permission to view schedules.')
        return redirect('login')
