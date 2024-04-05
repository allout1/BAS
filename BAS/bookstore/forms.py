from django import forms
from .models import Buyer

class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['name', 'email', 'phone_no']