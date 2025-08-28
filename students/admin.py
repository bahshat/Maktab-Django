from django.contrib import admin
from .models import Student, Payment
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'student_class', 'paid_till_date', 'fees_period')
    search_fields = ('name', 'roll_number')
    list_filter = ('student_class', 'fees_period')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'payment_date', 'amount_paid', 'paid_for_months')
    list_filter = ('payment_date',)
    search_fields = ('student__name', 'student__roll_number')

    def save_model(self, request, obj, form, change):
        # Save the payment object first
        super().save_model(request, obj, form, change)

        # Update the associated student's paid_till_date
        student = obj.student
        months_per_period = {
            'monthly': 1,
            'quarterly': 3,
            'half_yearly': 6,
            'yearly': 12,
        }[student.fees_period]

        months_to_add = obj.paid_for_months * months_per_period

        if student.paid_till_date:
            student.paid_till_date += relativedelta(months=months_to_add)
        else:
            student.paid_till_date = timezone.now().date() + relativedelta(months=months_to_add)
        student.save()

admin.site.register(Student, StudentAdmin)
admin.site.register(Payment, PaymentAdmin)