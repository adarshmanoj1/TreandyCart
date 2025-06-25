from django import forms
from .models import User
from .models import Review

class PhoneForm(forms.Form):
    phone = forms.CharField(max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'address']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = User
        fields = ['phone', 'email', 'name', 'address']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
