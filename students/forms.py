from django import forms
from .models import Student

COURSE_CHOICES = [
    ('', '-- Select Course --'),
    ('B.Tech CSE', 'B.Tech CSE'), ('B.Tech ECE', 'B.Tech ECE'),
    ('B.Tech ME', 'B.Tech ME'), ('B.Tech Civil', 'B.Tech Civil'),
    ('BCA', 'BCA'), ('MCA', 'MCA'), ('MBA', 'MBA'),
    ('B.Sc', 'B.Sc'), ('M.Sc', 'M.Sc'),
]

YEAR_CHOICES = [
    ('', '-- Select Year --'),
    ('1st Year', '1st Year'), ('2nd Year', '2nd Year'),
    ('3rd Year', '3rd Year'), ('4th Year', '4th Year'),
]

class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Student
        fields = ['mobile', 'address', 'photo']
        widgets = {
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        student.user.first_name = self.cleaned_data['first_name']
        student.user.last_name = self.cleaned_data['last_name']
        student.user.email = self.cleaned_data['email']
        if commit:
            student.user.save()
            student.save()
        return student
