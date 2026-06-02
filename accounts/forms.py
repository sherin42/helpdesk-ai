from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter full name'
        })
    )

    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter age'
        })
    )

    gender = forms.ChoiceField(
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],

        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter location'
        })
    )

    class Meta:

        model = User

        fields = [
            'name',
            'username',
            'email',
            'age',
            'gender',
            'location',
            'password1',
            'password2'
        ]

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose username'
            }),

        }

    password1 = forms.CharField(

        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })

    )

    password2 = forms.CharField(

        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    )

class StaffCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password', 'department']

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'autocomplete': 'new-password'
            }),

            'department': forms.Select(attrs={
                'class': 'form-select'
            }),

        }

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'name',
            'username',
            'email',
            'role',
            'department',
            'age',
            'gender',
            'location'
        ]

class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            'name',
            'email',
            'username',
            'age',
            'gender',
            'location',
            'department'
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'age': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'department': forms.Select(attrs={
                'class': 'form-select'
            }),

        }

class StaffProfileForm(ProfileUpdateForm):

    class Meta(ProfileUpdateForm.Meta):

        model = User

        fields = [
            'name',
            'email',
            'username',
            'department',
        ]


class UserProfileForm(ProfileUpdateForm):

    class Meta(ProfileUpdateForm.Meta):

        model = User

        fields = [
            'name',
            'email',
            'username',
            'age',
            'gender',
            'location',
        ]