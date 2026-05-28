from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from participantmgmt.models import Student


COURSE_CHOICES = [
    ('', '-- Select Course --'),
    ('B.Tech CSE', 'B.Tech CSE'),
    ('B.Tech ECE', 'B.Tech ECE'),
    ('B.Tech ME', 'B.Tech ME'),
    ('B.Tech Civil', 'B.Tech Civil'),
    ('BCA', 'BCA'),
    ('MCA', 'MCA'),
    ('MBA', 'MBA'),
    ('B.Sc', 'B.Sc'),
    ('M.Sc', 'M.Sc'),
]

YEAR_CHOICES = [
    ('', '-- Select Year --'),
    ('1st Year', '1st Year'),
    ('2nd Year', '2nd Year'),
    ('3rd Year', '3rd Year'),
    ('4th Year', '4th Year'),
]

GENDER_CHOICES = [
    ('', '-- Select Gender --'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    dob = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}))
    course = forms.ChoiceField(choices=COURSE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    academic_year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                dob=self.cleaned_data['dob'],
                gender=self.cleaned_data['gender'],
                mobile=self.cleaned_data['mobile'],
                address=self.cleaned_data['address'],
                course=self.cleaned_data['course'],
                academic_year=self.cleaned_data['academic_year'],
                photo=self.cleaned_data.get('photo'),
                is_approved=False,
            )
        return user


class PersonalDetailsForm(forms.Form):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    dob = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Full Address'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class AcademicDetailsForm(forms.Form):
    academic_year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))


class CourseSelectionForm(forms.Form):
    course = forms.ChoiceField(choices=COURSE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


PAYMENT_METHOD_CHOICES = [
    ('upi', 'UPI'),
    ('card', 'Debit / Credit Card'),
    ('netbanking', 'Net Banking'),
    ('cash', 'Cash at Counter'),
]


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    transaction_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction / Reference ID'}))
    receipt = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


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