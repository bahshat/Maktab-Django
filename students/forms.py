from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['roll_number']
        widgets = {
            'paid_till_date': forms.DateInput(attrs={'type': 'date'})
        }

class SearchForm(forms.Form):
    roll_number = forms.IntegerField(label='Roll Number')
