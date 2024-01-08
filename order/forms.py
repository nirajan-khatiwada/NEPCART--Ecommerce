from django import forms

class OrderForm(forms.Form):
    country = forms.CharField(max_length=50, required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    state = forms.CharField(max_length=50, required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    address_line_1 = forms.CharField(max_length=50, required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(max_length=50, required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
