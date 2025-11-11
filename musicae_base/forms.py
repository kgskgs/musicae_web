from django import forms
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField


class ContactForm(forms.Form):
    contact_name = forms.CharField(max_length=200, label=_("Вашето име"))
    contact_email = forms.EmailField(label=_("Имейл"))
    content = forms.CharField(widget=forms.Textarea, label=_("Съобщение"))
    # Optional: a non-blocking captcha field your template shows
    captcha = forms.CharField(required=False, label=_("Потвърждение"))
