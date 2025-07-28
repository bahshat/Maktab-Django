from django.db import models

class Student(models.Model):
    FEES_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('yearly', 'Yearly'),
    ]

    roll_number = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number1 = models.CharField(max_length=15, blank=True, null=True)
    phone_number2 = models.CharField(max_length=15, blank=True, null=True)
    student_class = models.SmallIntegerField()
    address = models.CharField(max_length=255, blank=True)
    paid_till_date = models.DateField(null=False, blank=False)
    fees_period = models.CharField(max_length=20, choices=FEES_PERIOD_CHOICES, default='quarterly')

    class Meta:
        unique_together = ('name', 'student_class')

    def __str__(self):
        return self.name

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_for_months = models.SmallIntegerField()

    def __str__(self):
        return f'{self.student.name} - {self.amount_paid} on {self.payment_date}'
