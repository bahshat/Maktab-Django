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

    if paid_till_date and paid_till_date >= current_date:
        return 0, 0

    if paid_till_date is None:
        first_pending_month_start = date(current_date.year, 1, 1)
    else:
        # Calculate the first day of the month *after* paid_till_date
        next_month_date = paid_till_date + relativedelta(months=1)
        first_pending_month_start = date(next_month_date.year, next_month_date.month, 1)

    # If the first pending month is in the future, no fees are pending yet.
    if first_pending_month_start > current_date:
        return 0, 0

    # Calculate the number of full months between first_pending_month_start and current_date
    # This will count the number of months that are fully or partially pending.
    delta_months = relativedelta(current_date, first_pending_month_start)
    total_pending_months = delta_months.years * 12 + delta_months.months + 1 # +1 to include the current month

    months_per_period = {
        'monthly': 1,
        'quarterly': 3,
        'half_yearly': 6,
        'yearly': 12,
    }[fees_period_type]

    pending_periods = (total_pending_months + months_per_period - 1) // months_per_period
    pending_amount = pending_periods * MONTHLY_FEE * months_per_period

    return max(0, pending_periods), pending_amount

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
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        students_with_pending_amount.append({
            'student': student,
            'pending_amount': pending_amount,
            'pending_periods': pending_periods,
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
    pending_periods, pending_amount = calculate_pending_periods(student, today)
    from_date = None
    to_date = None

    # Check for pending fees
    pending_periods, pending_amount = calculate_pending_periods(student, today)
    if pending_amount > 0:
        fee_status = f"Pending: {pending_periods} periods"
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