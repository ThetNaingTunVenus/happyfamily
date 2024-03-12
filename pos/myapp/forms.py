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


class AdminProductEditForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = ['item_name','category','pruchase_price','sell_price','balance_qty','barcode_id']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'barcode_id': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'category': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'pruchase_price': forms.NumberInput(attrs={'class': 'form-control col-md-6'}),
            'sell_price': forms.NumberInput(attrs={'class': 'form-control col-md-6'}),
            'balance_qty': forms.NumberInput(attrs={'class': 'form-control col-md-6', 'readonly':'True'}),

        }

class SupplierEditForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name','phone_number','address']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'address': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
        }

class PurchaseDataDeleteFrom(forms.ModelForm):
    class Meta:
        model = PurchaseList
        fields = ['item_name','purchase_qty']
        widgets = {
            # 'p_date':forms.TextInput(attrs={'class': 'form-control','readonly':'True'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'True'}),
            'purchase_qty': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'True'}),
        }