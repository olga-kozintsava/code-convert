from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

from base.models import Convert

User = get_user_model()


class RegistrationForm(UserCreationForm):
    username = forms.CharField( min_length=2,
                                max_length=50,
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Username'})
                                )
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Email'}
                             ))
    password1 = forms.CharField(strip=False,
                                widget=forms.PasswordInput(
                                    attrs={'autocomplete': 'new-password',
                                           'placeholder': "Password"})
                                )
    password2 = forms.CharField(widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Confirm password'})
                                )

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        find_username = User.objects.filter(username=username)
        if find_username.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        find_email = User.objects.filter(email=email)
        if find_email.count():
            raise ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Password"}))


class DeleteConvertForm(forms.Form):
    convert_id = forms.IntegerField(required=True)

    def clean_convert_id(self):
        convert_id = self.cleaned_data['convert_id']
        if not Convert.objects.filter(id=convert_id).exists():
            raise forms.ValidationError('Invalid convert ID')
        return convert_id


class InputTextForm(forms.Form):
    text_input = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Input Text'
                   })
    )


class UploadFileForm(forms.Form):
    file = forms.FileField()

