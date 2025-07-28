from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Student, Payment
from .forms import StudentForm, SearchForm, PaymentForm

MONTHLY_FEE = 400

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('search_student')
        else:
            return render(request, 'students/login.html', {'error': 'Invalid credentials'})
    return render(request, 'students/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def calculate_pending_periods(student, current_date):
    paid_till_date = student.paid_till_date
    fees_period_type = student.fees_period

    months_per_period = {
        'monthly': 1,
        'quarterly': 3,
        'half_yearly': 6,
        'yearly': 12,
    }[fees_period_type]

    pending_periods = 0
    pending_amount = 0
    total_pending_months_display = 0

    # If paid_till_date is today or in the future, no fees are pending.
    if paid_till_date and paid_till_date >= current_date:
        return 0, 0, 0

    # Determine the effective start date for calculating pending fees.
    # If paid_till_date is None, fees are pending from the beginning of the current year.
    # Otherwise, fees are pending from the day after paid_till_date.
    if paid_till_date is None:
        effective_start_date = date(current_date.year, 1, 1)
    else:
        effective_start_date = paid_till_date + timedelta(days=1)

    # Iterate through periods to count pending ones
    current_period_start = effective_start_date
    while current_period_start <= current_date:
        pending_periods += 1
        current_period_start += relativedelta(months=months_per_period)

    pending_amount = pending_periods * MONTHLY_FEE * months_per_period
    total_pending_months_display = pending_periods * months_per_period

    return max(0, pending_periods), pending_amount, total_pending_months_display

@login_required
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

@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            return redirect('student_detail', roll_number=student.roll_number)
    else:
        form = StudentForm()
    return render(request, 'students/add_student.html', {'form': form})

@login_required
def student_detail(request, roll_number):
    student = get_object_or_404(Student, roll_number=roll_number)
    payments = student.payments.all().order_by('-payment_date')
    
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            payment.student = student
            payment.payment_date = timezone.now().date()
            payment.save()

            # Update student's paid_till_date
            print(f"[DEBUG] Before update: student.paid_till_date = {student.paid_till_date}")
            print(f"[DEBUG] Payment paid_for_months = {payment.paid_for_months}")
            if student.paid_till_date:
                student.paid_till_date += relativedelta(months=payment.paid_for_months)
            else:
                student.paid_till_date = timezone.now().date() + relativedelta(months=payment.paid_for_months)
            student.save()
            print(f"[DEBUG] After update: student.paid_till_date = {student.paid_till_date}")
            return redirect(reverse('student_detail', kwargs={'roll_number': student.roll_number}) + f'?payment_success=True&payment_amount={payment.amount_paid}')
    else:
        payment_form = PaymentForm()

    payment_success = request.GET.get('payment_success', False)
    payment_amount = request.GET.get('payment_amount', 0)

    return render(request, 'students/student_detail.html', {
        'student': student,
        'payments': payments,
        'payment_form': payment_form,
        'payment_success': payment_success,
        'payment_amount': payment_amount
    })

@login_required
def pending_fees_list(request):
    today = timezone.now().date()
    all_pending_students = Student.objects.filter(paid_till_date__lt=today)

    students_with_pending_amount = []
    for student in all_pending_students:
        pending_periods, pending_amount, total_pending_months = calculate_pending_periods(student, today)
        students_with_pending_amount.append({
            'student': student,
            'pending_amount': pending_amount,
            'pending_periods': pending_periods,
            'total_pending_months': total_pending_months,
        })
    return render(request, 'students/pending_fees_list.html', {'pending_students': students_with_pending_amount})

@login_required
def due_soon_fees_list(request):
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)
    due_soon_students = Student.objects.filter(paid_till_date__gte=today, paid_till_date__lte=seven_days_from_now).order_by('paid_till_date')
    return render(request, 'students/due_soon_fees_list.html', {'due_soon_students': due_soon_students})

def fees_info(request, roll_number):
    student = get_object_or_404(Student, roll_number=roll_number)
    today = timezone.now().date()
    
    fee_status = "Paid Up"
    fee_amount = 0

    # Check for pending fees
    pending_periods, pending_amount, total_pending_months_display = calculate_pending_periods(student, today)
    
    from_date = None
    to_date = None

    if pending_amount > 0:
        fee_status = f"Pending for {total_pending_months_display} Months"
        fee_amount = pending_amount

        if student.paid_till_date is None:
            from_date = date(today.year, 1, 1)
        else:
            from_date = student.paid_till_date + relativedelta(days=1)

        months_per_period = {
            'monthly': 1,
            'quarterly': 3,
            'half_yearly': 6,
            'yearly': 12,
        }[student.fees_period]
        to_date = from_date + relativedelta(months=pending_periods * months_per_period) - relativedelta(days=1)
    else:
        # Check for due soon fees
        seven_days_from_now = today + timedelta(days=7)
        if student.paid_till_date and today <= student.paid_till_date <= seven_days_from_now:
            fee_status = "Due Soon"
            # Calculate amount for the next period
            months_per_period = {
                'monthly': 1,
                'quarterly': 3,
                'half_yearly': 6,
                'yearly': 12,
            }[student.fees_period]
            fee_amount = MONTHLY_FEE * months_per_period

    payments = student.payments.all().order_by('-payment_date')

    return render(request, 'students/fees_info.html', {
        'student': student,
        'fee_status': fee_status,
        'fee_amount': fee_amount,
        'payments': payments,
        'from_date': from_date,
        'to_date': to_date,
        'total_pending_months': total_pending_months_display,
    })

@login_required
def dashboard(request):
    total_students = Student.objects.count()
    today = timezone.now().date()

    pending_students_count = Student.objects.filter(paid_till_date__lt=today).count()

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
        'chart_colors': ['#FF6384', '#FFCE56', '#4CAF50'], # Pending (Red), Due Soon (Yellow), Paid Up (Green) # Pending (Red), Due Soon (Yellow), Paid Up (Green) # Pending (Red), Due Soon (Yellow), Paid Up (Green)
    }
    return render(request, 'students/dashboard.html', context)