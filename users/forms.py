from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import Group, Permission
import re
from events.forms import StyledFormMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email']
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for field_name in ["username","password1","password2"]:
            self.fields[field_name].help_text = None


class CustomRegisterForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email=email).exists()

        if email_exists:
            raise forms.ValidationError("Email already exists")

        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []

        if len(password) < 8:
            errors.append('Password must contain at least 8 characters')
        elif not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one Capital letter")
        elif not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one small letter")
        elif not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        elif not re.search(r'[@!#$%^&=+]', password):
            errors.append("Password must contain at least one of (@!#$%^&=+) special characters")

        if errors:
            raise forms.ValidationError(errors)
        
        return password
    
    # Non field error
    def clean(self):  
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password didn't match")

        return cleaned_data
    
# Login
class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

class CustomUserChangeForm(StyledFormMixin, UserChangeForm):
        date_joined = forms.DateTimeField(
            label="Date Joined",
            required=False,
            disabled=True,
            widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
        )
        password = None
        role = forms.ModelChoiceField(
            queryset=Group.objects.only("name"),
            # empty_label="Select a Role",
            required=True,
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        class Meta:
            model = User() 
            fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')

            widgets = {
                'username': forms.TextInput,
                'first_name': forms.TextInput,
                'last_name': forms.TextInput,
                'email': forms.EmailInput,
                'is_active': forms.CheckboxInput,
                'is_staff': forms.CheckboxInput,
                'is_superuser': forms.CheckboxInput,
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.groups.exists():
                self.fields['role'].initial = self.instance.groups.first()

        def save(self, commit=True):
            user = super().save(commit=False)
            role = self.cleaned_data.get('role')
            if commit:
                user.save()
                user.groups.set([role])

            return user


class CreateGroupForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related("content_type").all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission'
    )
    
    class Meta:
        model = Group
        fields = ['name', 'permissions']

# Profile form
class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'profile_image']

# Password change and reset forms
class CustomPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass
