from django.core.management.base import BaseCommand
from students.models import Student
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample student data for testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating student data...'))

        # Clear existing data to avoid duplicates on repeated runs
        Student.objects.all().delete()

        students_data = [
            # Student with no fees paid yet (paid_till_date is None)
            {
                'roll_number': 1001,
                'name': 'Alice Smith',
                'phone_number': 9876543210,
                'student_class': 5,
                'address': '123 Main St',
                'paid_till_date': None
            },
            # Student with fees pending (paid_till_date in the past)
            {
                'roll_number': 1002,
                'name': 'Bob Johnson',
                'phone_number': 9876543211,
                'student_class': 7,
                'address': '456 Oak Ave',
                'paid_till_date': date.today() - timedelta(days=30)
            },
            # Student with fees due soon (paid_till_date in the next 7 days)
            {
                'roll_number': 1003,
                'name': 'Charlie Brown',
                'phone_number': 9876543212,
                'student_class': 6,
                'address': '789 Pine Ln',
                'paid_till_date': date.today() + timedelta(days=5)
            },
            # Student with fees paid up to date (paid_till_date is today)
            {
                'roll_number': 1004,
                'name': 'Diana Prince',
                'phone_number': 9876543213,
                'student_class': 8,
                'address': '101 Hero Way',
                'paid_till_date': date.today()
            },
            # Student with fees paid in the future (not pending, not due soon)
            {
                'roll_number': 1005,
                'name': 'Eve Adams',
                'phone_number': 9876543214,
                'student_class': 9,
                'address': '202 Future Rd',
                'paid_till_date': date.today() + timedelta(days=60)
            },
            # Another pending student
            {
                'roll_number': 1006,
                'name': 'Frank White',
                'phone_number': 9876543215,
                'student_class': 4,
                'address': '303 Old St',
                'paid_till_date': date.today() - timedelta(days=15)
            },
            # Another due soon student
            {
                'roll_number': 1007,
                'name': 'Grace Green',
                'phone_number': 9876543216,
                'student_class': 10,
                'address': '404 New Blvd',
                'paid_till_date': date.today() + timedelta(days=2)
            },
        ]

        for data in students_data:
            Student.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Successfully added student: {data['name']}'))

        self.stdout.write(self.style.SUCCESS('Student data population complete.'))
