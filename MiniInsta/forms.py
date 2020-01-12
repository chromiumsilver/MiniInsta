from django.db import models
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import InstaUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = InstaUser
        fields = ('username', 'email', 'profile_pic')