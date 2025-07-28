from django.db import models

class Student(models.Model):
    roll_number = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    student_class = models.SmallIntegerField()
    address = models.CharField(max_length=255, blank=True)
    paid_till_date = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.name

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_for_months = models.SmallIntegerField()

    def __str__(self):
        return f'{self.student.name} - {self.amount_paid} on {self.payment_date}'
