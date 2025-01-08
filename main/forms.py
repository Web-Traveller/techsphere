# main/forms.py
from django import forms
from django.forms import formset_factory
from .models import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class RegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name',
                                     'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                      'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                         'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                         'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Team Name',
                                         'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email', 'phone', 'branch', 'year', 'college_name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Member Name',
                                         'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Member Email',
                                          'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Member Phone',
                                          'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'branch': forms.TextInput(attrs={'placeholder': 'Member Branch',
                                           'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'year': forms.TextInput(attrs={'placeholder': 'Member Year',
                                        'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'college_name': forms.TextInput(attrs={'placeholder': 'Member College',
                                                'class': 'w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError as e:
                raise forms.ValidationError("Enter a valid email")
        return email


TeamMemberFormSet = formset_factory(TeamMemberForm, extra=3)


class PaymentSubmissionForm(forms.Form):
    payment_screenshot = forms.ImageField(required=True)
    transaction_number = forms.CharField(max_length=200, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Enter transaction number',
               'class': 'w-full px-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500'}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
           'name': forms.TextInput(attrs={'placeholder': 'Your Name','class': 'w-full p-2 border border-gray-700 rounded bg-gray-900 text-white'}),
           'email': forms.EmailInput(attrs={'placeholder': 'Your Email','class': 'w-full p-2 border border-gray-700 rounded bg-gray-900 text-white'}),
           'message': forms.Textarea(attrs={'placeholder': 'Your Message','rows': 4, 'class': 'w-full p-2 border border-gray-700 rounded bg-gray-900 text-white'}),
        }