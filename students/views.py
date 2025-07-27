from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Student
from .forms import StudentForm, SearchForm

def search_student(request):
    form = SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            try:
                student = Student.objects.get(roll_number=roll_number)
                return redirect('student_detail', roll_number=student.roll_number)
            except Student.DoesNotExist:
                return render(request, 'students/search_student.html', {'form': form, 'message': 'Student not found.'})
    return render(request, 'students/search_student.html', {'form': form})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            return redirect('student_detail', roll_number=student.roll_number)
    else:
        form = StudentForm()
    return render(request, 'students/add_student.html', {'form': form})

def student_detail(request, roll_number):
    student = get_object_or_404(Student, roll_number=roll_number)
    if request.method == 'POST':
        # Assuming a simple form for updating paid_till_date directly
        paid_till_date_str = request.POST.get('paid_till_date')
        if paid_till_date_str:
            student.paid_till_date = paid_till_date_str
            student.save()
            return redirect('student_detail', roll_number=student.roll_number)
    return render(request, 'students/student_detail.html', {'student': student})

def pending_fees_list(request):
    today = timezone.now().date()
    pending_students = Student.objects.filter(paid_till_date__lt=today).order_by('paid_till_date')
    return render(request, 'students/pending_fees_list.html', {'pending_students': pending_students})

def due_soon_fees_list(request):
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)
    due_soon_students = Student.objects.filter(paid_till_date__gte=today, paid_till_date__lte=seven_days_from_now).order_by('paid_till_date')
    return render(request, 'students/due_soon_fees_list.html', {'due_soon_students': due_soon_students})
