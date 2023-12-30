from django import forms
from django.core import validators
from django.contrib.auth.models import Group
from shopapp.models import Product, Order

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
