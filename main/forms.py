from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from .models import *


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input-class', 'placeholder': 'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input-class', 'placeholder': 'Password'}))
    error_messages = {
        'invalid_login': 'Incorrect login or password',
        'inactive': "This is an inactive account",
    }


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "Passwords don't match",

    }

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-input-class',
            'placeholder': 'Username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input-class',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input-class',
            'placeholder': 'Confirm Password',
        })


class MoneyBlockForm(forms.ModelForm):
    class Meta:
        model = MoneyBlock
        fields = ['name', 'balance', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input-class add-expenses-class add-expenses-class-name', 'placeholder': 'Name'}),
            'balance': forms.NumberInput(attrs={'class': 'form-input-class add-expenses-class',
                                                'placeholder': 'Balance',
                                                'min': '-99999999.99',
                                                'max': '99999999.99',
                                                'step': '0.01'
                                                }),
            'currency': forms.Select(attrs={'class': 'form-input-class add-expenses-class'})
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["description", "amount", "money_block"]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-input-class', 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input-class',
                                               'placeholder': 'Amount',
                                               'min': '-99999999.99',
                                               'max': '99999999.99',
                                               'step': '0.01'
                                               }),
            "money_block": forms.HiddenInput(),
        }


class TopUpForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input-class top-up-form-class',
                                        'placeholder': 'Amount',
                                        'min': '-99999999.99',
                                        'max': '99999999.99',
                                        'step': '0.01'
                                        })
    )
    money_block = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'money_block_id'})
    )