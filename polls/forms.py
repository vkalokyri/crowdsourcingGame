
from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'style':"margin-top:35px; height:35px; width:30%; font-size:20px;"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style':"height:35px; width:30%; font-size:20px;"}))
    class Meta():
        model = User
        fields = ('username','password')
