from django import forms
from .models import Student, Payment

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'phone_number1', 'phone_number2', 'student_class', 'address', 'paid_till_date', 'fees_period']
        widgets = {
            'paid_till_date': forms.DateInput(attrs={'type': 'date'}),
            'phone_number1': forms.TextInput(attrs={'pattern': '[0-9]{10}', 'title': 'Enter 10 digits only', 'maxlength': '10'}),
            'phone_number2': forms.TextInput(attrs={'pattern': '[0-9]{10}', 'title': 'Enter 10 digits only', 'maxlength': '10'}),
        }

class SearchForm(forms.Form):
    roll_number = forms.IntegerField(label='Roll Number')

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'paid_for_months']