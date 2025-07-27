from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Student
from .forms import StudentForm, SearchForm

MONTHLY_FEE = 400

def calculate_pending_periods(student, current_date):
    paid_till_date = student.paid_till_date
    fees_period_type = student.fees_period

    # Determine the month and year from which fees are considered pending
    if paid_till_date is None:
        # If never paid, assume pending from the start of the current year (January of current_date's year)
        pending_from_month = 1
        pending_from_year = current_date.year
    else:
        # If paid_till_date is in the future (e.g., Aug 12, current is July 28), then nothing is pending.
        # Also, if paid_till_date is today or later in the current month, nothing is pending.
        if paid_till_date.year > current_date.year or \
           (paid_till_date.year == current_date.year and paid_till_date.month > current_date.month) or \
           (paid_till_date.year == current_date.year and paid_till_date.month == current_date.month and paid_till_date.day >= current_date.day):
            # Fees are paid up to or beyond the current date/month
            return 0, 0

        # If paid_till_date is in the past, pending starts from its month
        pending_from_month = paid_till_date.month
        pending_from_year = paid_till_date.year

    # Calculate the total number of months from pending_from_month/year to current_date's month/year (inclusive)
    total_months_to_consider = (current_date.year - pending_from_year) * 12 + \
                               (current_date.month - pending_from_month) + 1 # +1 to include the current month

    pending_periods = 0
    months_per_period = 0

    if fees_period_type == 'monthly':
        pending_periods = total_months_to_consider
        months_per_period = 1
    elif fees_period_type == 'quarterly':
        # Calculate full quarters. If there's a partial quarter, it counts as a full pending period.
        pending_periods = (total_months_to_consider + 2) // 3 # +2 for ceiling division for quarters
        months_per_period = 3
    elif fees_period_type == 'half_yearly':
        pending_periods = (total_months_to_consider + 5) // 6 # +5 for ceiling division for half-yearly
        months_per_period = 6
    elif fees_period_type == 'yearly':
        pending_periods = (total_months_to_consider + 11) // 12 # +11 for ceiling division for yearly
        months_per_period = 12

    return max(0, pending_periods), months_per_period

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
        paid_till_date_str = request.POST.get('paid_till_date')
        if paid_till_date_str:
            student.paid_till_date = paid_till_date_str
            student.save()
            return redirect('student_detail', roll_number=student.roll_number)
    return render(request, 'students/student_detail.html', {'student': student})

def pending_fees_list(request):
    today = timezone.now().date()
    print(f"[DEBUG] pending_fees_list: Today is {today}")
    all_pending_students = Student.objects.filter(paid_till_date__lt=today) | \
                           Student.objects.filter(paid_till_date__isnull=True)

    students_with_pending_amount = []
    for student in all_pending_students:
        print(f"[DEBUG] pending_fees_list: Processing student {student.roll_number}, paid_till_date: {student.paid_till_date}")
        pending_periods, months_per_period = calculate_pending_periods(student, today)
        pending_amount = pending_periods * (MONTHLY_FEE * months_per_period)
        students_with_pending_amount.append({
            'student': student,
            'pending_amount': pending_amount,
            'pending_periods': pending_periods,
            'months_per_period': months_per_period,
        })
    return render(request, 'students/pending_fees_list.html', {'pending_students': students_with_pending_amount})

def due_soon_fees_list(request):
    today = timezone.now().date()
    print(f"[DEBUG] due_soon_fees_list: Today is {today}")
    seven_days_from_now = today + timedelta(days=7)
    due_soon_students = Student.objects.filter(paid_till_date__gte=today, paid_till_date__lte=seven_days_from_now).order_by('paid_till_date')
    for student in due_soon_students:
        print(f"[DEBUG] due_soon_fees_list: Processing student {student.roll_number}, paid_till_date: {student.paid_till_date}")
    return render(request, 'students/due_soon_fees_list.html', {'due_soon_students': due_soon_students})

def dashboard(request):
    total_students = Student.objects.count()
    today = timezone.now().date()

    pending_students_count = Student.objects.filter(paid_till_date__lt=today) | \
                             Student.objects.filter(paid_till_date__isnull=True)
    pending_students_count = pending_students_count.count()

    seven_days_from_now = today + timedelta(days=7)
    due_soon_students_count = Student.objects.filter(paid_till_date__gte=today, paid_till_date__lte=seven_days_from_now).count()

    paid_up_students_count = total_students - pending_students_count - due_soon_students_count
    if paid_up_students_count < 0:
        paid_up_students_count = 0

    context = {
        'total_students': total_students,
        'pending_students_count': pending_students_count,
        'due_soon_students_count': due_soon_students_count,
        'paid_up_students_count': paid_up_students_count,
        'chart_labels': ['Pending', 'Due Soon', 'Paid Up'],
        'chart_data': [pending_students_count, due_soon_students_count, paid_up_students_count],
        'chart_colors': ['#FF6384', '#FFCE56', '#36A2EB'],
    }
    return render(request, 'students/dashboard.html', context)