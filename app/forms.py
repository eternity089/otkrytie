from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_password_len(password):
    if len(password) < 6:
        raise ValidationError("Длина пароля должна быть не менее 6 символов")

class RegisterUserForm(forms.ModelForm):
    name = forms.CharField(label='Имя', required=True,
                              validators=[RegexValidator(regex=r'^[а-яА-Я- ]+$', message='Допустима только кириллица')],
                              error_messages={
                                  'required' : 'Обязательное поле'
                              },
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Петр'}))
    email = forms.EmailField(label='Адрес электронной почты', required=True,
                             error_messages={
                                 'invalid': 'Неверный формат электронной почты',
                                 'unique': 'Данная почта уже зарегистрирована'
                             },
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder' : 'example@mail.com'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Не менее 6 символов'}),
                               validators=[validate_password_len], required=True,
                               error_messages={
                                    'required': 'Обязательное поле'
                               })
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Не менее 6 символов'}),
                                validators=[validate_password_len], required=True,
                               error_messages={
                                    'required': 'Обязательное поле'
                               })
    phone = forms.CharField(required=True, label='Номер телефона', validators=[RegexValidator(regex=r"^\+?1?\d{8,15}$")], max_length=20,
                            error_messages={
                                'required': 'Обязательное поле',
                                'unique': 'Номер телефона уже зарегистрирован'
                            },
                            widget=forms.TelInput(attrs={'class':'form-control', 'placeholder':'+7 (900) 123-45-67'}))
    def clean(self):
        super().clean()
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError({'password2' : ValidationError('Введенные пароли не совпадают', code='password_mismatch')})
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user
    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'password', 'password2')


class LoginForm(forms.Form):
    email = forms.EmailField(label='Электронная почта', widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'example@mail.com'
    }))
    password = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Не менее 6 символов'
    }))

class OrderForm(forms.ModelForm):
    def clean(self):
        status = self.cleaned_data.get('status')
        reject_reason = self.cleaned_data.get('reject_reason')
        if status == 'canceled' and not reject_reason:
            raise forms.ValidationError({'reject_reason': 'При отказе необходимо указать причину'})