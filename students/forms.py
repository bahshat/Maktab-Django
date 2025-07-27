from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class SearchForm(forms.Form):
    roll_number = forms.IntegerField(label='Roll Number')
