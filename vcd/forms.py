from django import forms


class LoginForm(forms.Form):
    org = forms.CharField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    

class SearchForm(forms.Form):
    search = forms.CharField()