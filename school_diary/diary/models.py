from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Class(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Lesson(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.subject.name})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    classes = models.ManyToManyField(Class)
    
    def __str__(self):
        return f"{self.user.get_full_name()}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    
    def __str__(self):
        return f"{self.user.get_full_name()}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.value}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Присутствует'),
        ('absent', 'Отсутствует'),
        ('late', 'Опоздание'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.student} - {self.subject} - {self.get_status_display()}"

class Schedule(models.Model):
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 1-7 (Monday-Sunday)
    lesson_number = models.IntegerField()  # 1-8
    
    def __str__(self):
        return f"{self.class_group} - {self.subject} - {self.get_day_display()} - Lesson {self.lesson_number}"

    def get_day_display(self):
        days = {
            1: 'Monday',
            2: 'Tuesday',
            3: 'Wednesday',
            4: 'Thursday',
            5: 'Friday',
            6: 'Saturday',
            7: 'Sunday'
        }
        return days.get(self.day_of_week, 'Unknown')

class Homework(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.class_group}) до {self.due_date}"
