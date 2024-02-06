from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    user_image = forms.ImageField(label='User Image', required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'user_image')



class CustomUserChangeForm(UserChangeForm):
    user_image = forms.ImageField(label='User Image', required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'user_image')

