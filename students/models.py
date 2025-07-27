from django.db import models

class Student(models.Model):
    FEES_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('yearly', 'Yearly'),
    ]

    roll_number = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    student_class = models.SmallIntegerField()
    address = models.CharField(max_length=255, blank=True)
    paid_till_date = models.DateField(null=True, blank=True)
    fees_period = models.CharField(max_length=20, choices=FEES_PERIOD_CHOICES, default='quarterly')

    def __str__(self):
        return self.name