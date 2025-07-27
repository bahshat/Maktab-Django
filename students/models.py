from django.db import models

class Student(models.Model):
    roll_number = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    student_class = models.SmallIntegerField()
    address = models.CharField(max_length=255, blank=True)
    paid_till_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name