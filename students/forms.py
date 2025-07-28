from django import forms
from .models import Student, Payment

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'phone_number', 'student_class', 'address', 'paid_till_date']
        widgets = {
            'paid_till_date': forms.DateInput(attrs={'type': 'date'})
        }

class SearchForm(forms.Form):
    roll_number = forms.IntegerField(label='Roll Number')

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'paid_for_months']