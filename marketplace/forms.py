"""
YOVO Marketplace Forms
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Item, ItemImage, Profile, Message


# ─── Register ──────────────────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.email      = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# ─── Login ─────────────────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username', 'class': 'form-input'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password', 'class': 'form-input'
        })


# ─── Item ──────────────────────────────────────────────────────────────────────
class ItemForm(forms.ModelForm):
    extra_images = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-input'}),
        label='Extra Photos'
    )

    class Meta:
        model  = Item
        fields = [
            'title', 'description', 'price', 'category', 'subcategory',
            'gender', 'location', 'condition', 'image', 'bill',
        ]
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Item title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe your item...'}),
            'price':       forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'min': '0', 'step': '0.01'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'subcategory': forms.Select(attrs={'class': 'form-input'}),
            'gender':      forms.Select(attrs={'class': 'form-input'}),
            'location':    forms.Select(attrs={'class': 'form-input'}),
            'condition':   forms.Select(attrs={'class': 'form-input'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'bill':        forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

    def save_extra_images(self, item):
        files = self.files.getlist('extra_images')
        for i, f in enumerate(files):
            ItemImage.objects.create(item=item, image=f, order=i)


# ─── Profile ───────────────────────────────────────────────────────────────────
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )

    class Meta:
        model  = Profile
        fields = ['bio', 'avatar', 'location', 'phone', 'address']
        widgets = {
            'bio':      forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Tell buyers a bit about yourself...'}),
            'avatar':   forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your city'}),
            'phone':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'address':  forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Delivery address'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial  = self.user_instance.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data.get('first_name', '')
            self.user_instance.last_name  = self.cleaned_data.get('last_name', '')
            self.user_instance.save()
        if commit:
            profile.save()
        return profile


# ─── Message ───────────────────────────────────────────────────────────────────
class MessageForm(forms.ModelForm):
    class Meta:
        model  = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Type your message...'
            })
        }