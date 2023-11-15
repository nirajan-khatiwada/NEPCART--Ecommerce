from django import forms

from django import forms

class RegisterForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}),
                               required=True
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    phone_number = forms.CharField(
        min_length=10,
        max_length=10,
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'max_length':'Phone Number Cant Be Greater Than 10'}
    )
    password = forms.CharField(
        min_length=8,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        error_messages={'min_length':'Password should atleast contain 8 character'}
    )


class ActivateForm(forms.Form):
    token=forms.CharField(max_length=100)

class LoginForm(forms.Form):
    phone_number = forms.CharField(
        min_length=10,
        max_length=10,
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter PhoneNumber'}),
        required=True,
        error_messages={'max_length':'Phone Number Cant Be Greater Than 10'}
    )


    password = forms.CharField(
        min_length=8,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}),
        required=True,
        error_messages={'min_length':'Password should atleast contain 8 character'}
    )



class ForgotPass(forms.Form):
     phone_number = forms.CharField(
        min_length=10,
        max_length=10,
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter PhoneNumber'}),
        required=True,
        error_messages={'max_length':'Phone Number Cant Be Greater Than 10'}
    ) 
     
class ResetPass(forms.Form):
    password = forms.CharField(
        min_length=8,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter Password'}),
        required=True,
        error_messages={'min_length':'Password should atleast contain 8 character'}
    )
    cpassword = forms.CharField(
        min_length=8,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Confirm Password'}),
        required=True,
        error_messages={'min_length':'Password should atleast contain 8 character'}
    )
