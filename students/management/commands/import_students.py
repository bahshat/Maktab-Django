import csv
from datetime import date
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from students.models import Student, Payment

class Command(BaseCommand):
    help = 'Imports student data from Student-Records.csv and clears existing data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting all existing Student and Payment records...'))
        Payment.objects.all().delete()
        Student.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Existing records deleted.'))

        csv_file_path = 'Student-Records.csv'
        default_class = 5
        default_paid_till_date = date(2025, 7, 1)

        self.stdout.write(self.style.SUCCESS(f'Importing data from {csv_file_path}...'))

        imported_students = set()

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student_name = row['Student Name'].strip()
                    address = row['Address'].strip()
                    phone_number1 = row['Contact Number 1'].strip() if row['Contact Number 1'].strip() else None
                    phone_number2 = row['Contact Number 2'].strip() if row['Contact Number 2'].strip() else None

                    # Create a unique key for checking duplicates based on name and phone_number1
                    student_key = (student_name, phone_number1)

                    if student_key in imported_students:
                        self.stdout.write(self.style.WARNING(f'Skipping duplicate entry: {student_name} ({phone_number1})'))
                        continue

                    try:
                        Student.objects.create(
                            name=student_name,
                            address=address,
                            phone_number1=phone_number1,
                            phone_number2=phone_number2,
                            student_class=default_class,
                            paid_till_date=default_paid_till_date,
                            fees_period='quarterly',
                        )
                        imported_students.add(student_key)
                    except IntegrityError:
                        self.stdout.write(self.style.WARNING(f'Skipping entry due to integrity error (likely duplicate name/class): {student_name}'))
                        continue

            self.stdout.write(self.style.SUCCESS('Successfully imported student data.'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Error: The file {csv_file_path} was not found.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))