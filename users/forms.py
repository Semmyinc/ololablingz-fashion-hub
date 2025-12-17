from django import forms
from .models import Users

class SignUpForm(forms.ModelForm):
    password = forms.CharField(label='', max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), required=True)
    confirm_password = forms.CharField(label='', max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm Password'}), required=True)
    
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        # self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Password does not match')