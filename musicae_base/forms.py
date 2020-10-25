from django import forms
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField


class ContactForm(forms.Form):

    errs = {
        "required": _("Това поле е задължително"),
        "invalid": _("Въведете валиден имейл адрес")
    }

    attrs = {
        'class': 'w3-input w3-border w3-mobile'
    }

    contact_name = forms.CharField(label=_("Име:"), required=True,
                                   error_messages=errs, widget=forms.TextInput(attrs=attrs))
    contact_email = forms.EmailField(label=_("Имейл:"), required=True,
                                     error_messages=errs, widget=forms.TextInput(attrs=attrs))
    content = forms.CharField(label=_("Съобщение:"), required=True, error_messages=errs,
                              widget=forms.Textarea(attrs=attrs),
                              )
    captcha = CaptchaField(label=_(""), error_messages={"invalid" : _("Отговорът е грешен! Опитайте отново.")})

    # def __init__(self, *args, **kwargs):
    #     super(ContactForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         #print(visible)

    #         visible.field.widget.attrs['class'] =
