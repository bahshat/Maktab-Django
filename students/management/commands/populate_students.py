from django.core.management.base import BaseCommand
from students.models import Student, Payment
from datetime import date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta

MONTHLY_FEE = 400

class Command(BaseCommand):
    help = 'Populates the database with sample student data and initial payment records.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating student data...'))

        # Clear existing data to avoid duplicates on repeated runs
        Payment.objects.all().delete() # Delete payments first due to ForeignKey
        Student.objects.all().delete()

        today = timezone.now().date()

        students_initial_config = [
            # Student admitted 6 months ago, paid for 4 months (2 months pending)
            {
                'name': 'Bob Johnson',
                'phone_number1': '9876543211',
                'phone_number2': '9988776655',
                'student_class': 7,
                'address': '456 Oak Ave',
                'admission_offset_months': 6, # Admitted 6 months ago
                'initial_months_paid': 4, # Paid for 4 months from admission
                'fees_period': 'monthly'
            },
            # Student admitted 3 months ago, paid for 3 months (due today)
            {
                'name': 'Charlie Brown',
                'phone_number1': '9876543212',
                'phone_number2': '',
                'student_class': 6,
                'address': '789 Pine Ln',
                'admission_offset_months': 3,
                'initial_months_paid': 3,
                'fees_period': 'quarterly'
            },
            # Student admitted 1 month ago, paid for 2 months (paid till next month)
            {
                'name': 'Diana Prince',
                'phone_number1': '9876543213',
                'phone_number2': '9123456789',
                'student_class': 8,
                'address': '101 Hero Way',
                'admission_offset_months': 1,
                'initial_months_paid': 2,
                'fees_period': 'monthly'
            },
            # Student admitted today, paid for 1 month
            {
                'name': 'Eve Adams',
                'phone_number1': '9876543214',
                'phone_number2': '',
                'student_class': 9,
                'address': '202 Future Rd',
                'admission_offset_months': 0,
                'initial_months_paid': 1,
                'fees_period': 'monthly'
            },
            # Another pending student (admitted 4 months ago, paid for 2 months)
            {
                'name': 'Frank White',
                'phone_number1': '9776543215',
                'phone_number2': '9000000000',
                'student_class': 4,
                'address': '303 Old St',
                'admission_offset_months': 4,
                'initial_months_paid': 2,
                'fees_period': 'half_yearly'
            },
            # Another due soon student (admitted 2 months ago, paid for 2 months)
            {
                'name': 'Grace Green',
                'phone_number1': '9676543216',
                'phone_number2': '',
                'student_class': 10,
                'address': '404 New Blvd',
                'admission_offset_months': 2,
                'initial_months_paid': 2,
                'fees_period': 'yearly'
            },
        ]

        for config in students_initial_config:
            admission_date = today - relativedelta(months=config['admission_offset_months'])
            paid_till_date = admission_date + relativedelta(months=config['initial_months_paid'])

            student = Student.objects.create(
                name=config['name'],
                phone_number1=config['phone_number1'],
                phone_number2=config['phone_number2'],
                student_class=config['student_class'],
                address=config['address'],
                paid_till_date=paid_till_date,
                fees_period=config['fees_period']
            )

            Payment.objects.create(
                student=student,
                payment_date=admission_date,
                amount_paid=MONTHLY_FEE * config['initial_months_paid'],
                paid_for_months=config['initial_months_paid']
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added student: {student.name} and initial payment.'))

        self.stdout.write(self.style.SUCCESS('Student data population complete.'))