from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import Student, Payment
from .views import calculate_pending_periods, MONTHLY_FEE

class StudentModelTest(TestCase):
    def test_create_student(self):
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=10,
            address='123 Test St',
            paid_till_date=timezone.now().date()
        )
        self.assertEqual(student.name, 'Test Student')
        self.assertIsNotNone(student.roll_number)

class PaymentModelTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=10,
            address='123 Test St',
            paid_till_date=timezone.now().date()
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            student=self.student,
            amount_paid=400.00,
            paid_for_months=1
        )
        self.assertEqual(payment.student, self.student)
        self.assertEqual(payment.amount_paid, 400.00)
        self.assertEqual(payment.paid_for_months, 1)
        self.assertIsNotNone(payment.payment_date)

class FeesCalculationTest(TestCase):
    def test_calculate_pending_periods_no_pending(self):
        today = timezone.now().date()
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today + relativedelta(months=1)
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 0)
        self.assertEqual(pending_amount, 0)

    def test_calculate_pending_periods_one_month_pending(self):
        today = timezone.now().date()
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today - relativedelta(months=1)
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 1)
        self.assertEqual(pending_amount, MONTHLY_FEE)

    def test_calculate_pending_periods_multiple_months_pending(self):
        today = timezone.now().date()
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today - relativedelta(months=3)
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 3)
        self.assertEqual(pending_amount, MONTHLY_FEE * 3)

    def test_calculate_pending_periods_partial_month_pending(self):
        today = timezone.now().date()
        # Paid till 15th of last month, so current month is also pending
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today - relativedelta(months=1, days=today.day - 15)
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 2) # Last month + current month
        self.assertEqual(pending_amount, MONTHLY_FEE * 2)

    def test_calculate_pending_periods_paid_till_today(self):
        today = timezone.now().date()
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 0)
        self.assertEqual(pending_amount, 0)

    def test_calculate_pending_periods_paid_till_future(self):
        today = timezone.now().date()
        student = Student.objects.create(
            name='Test Student',
            phone_number1='1234567890',
            phone_number2='0987654321',
            student_class=1,
            address='abc',
            paid_till_date=today + relativedelta(days=5)
        )
        pending_periods, pending_amount = calculate_pending_periods(student, today)
        self.assertEqual(pending_periods, 0)
        self.assertEqual(pending_amount, 0)
