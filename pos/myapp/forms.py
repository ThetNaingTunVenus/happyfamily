from django import forms
from .models import *


class ULoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class GetBarCode(forms.Form):
    id = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control col-md-4'}))

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'mobile', 'shipping_address','discount','delivery_fee','delivery_system','payment',]
        widgets = {
            'ordered_by': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control'}),
            'delivery_fee': forms.NumberInput(attrs={'class':'form-control col-md-6'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control col-md-4'}),
            'payment': forms.Select(attrs={'class': 'form-control col-md-6'}),
            'delivery_system': forms.Select(attrs={'class': 'form-control col-md-6'}),
            # 'deli_payment':forms.BooleanField(),

            # 'id':forms.Textarea

        }
