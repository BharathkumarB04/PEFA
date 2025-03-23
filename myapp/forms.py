from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError

class Expenseform(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title','amount','date','uploaded_bill']
        widgets ={
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the title expense'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the amount'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'uploaded_bill': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }

class MonthlyBudgetForm(forms.ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ['category', 'amount', 'year', 'month']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['title', 'goal_amount']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
        }

class UploadExpenseFileForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={"class": "form-control"}))

class SIPInvestmentForm(forms.ModelForm):
    """Form for adding a new SIP investment with styling and validation."""

    purchase_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Purchase Date"
    )

    class Meta:
        model = SIPInvestment
        fields = ['sip_name', 'scheme_code', 'purchase_date', 'invested_amount', 'units_bought']
        widgets = {
            'sip_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SIP Name'}),
            'scheme_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Scheme Code'}),
            'invested_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount (₹)'}),
            'units_bought': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Units Bought'}),
        }
        labels = {
            'sip_name': "SIP Name",
            'scheme_code': "Scheme Code",
            'invested_amount': "Invested Amount",
            'units_bought': "Units Bought",
        }