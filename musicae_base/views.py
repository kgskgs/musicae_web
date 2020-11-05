from django.shortcuts import render, get_object_or_404
from .models import Page, Contact
from .forms import ContactForm
from musicae_web import settings

from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from operator import __add__, __sub__


def PageView(request, link):
    page = get_object_or_404(Page, link=link)
    context = {
        "content": page.content,
        "title": f"{page.link.text} - Fundamenta Musicae",
        "description": page.description,
        "keywords": page.keywords
    }

    return render(request, 'musicae_base/genericPage.html', context)


ops_text = {
    __add__: _("Добавете {number} към всяка цифра"),
    __sub__: _("Извадете {number} от всяка цифра"),
}

mods_text = {
    1: _("едно"),
    2: _("две"),
    3: _("три"),
}


def contact(request):
    # https://hellowebbooks.com/news/tutorial-setting-up-a-contact-form-with-django/
    form = ContactForm(request.POST or None)

    failClass = "w3-hide"
    successClass = "w3-hide"

    print(f"view: {settings.challenge.mod} {settings.challenge.op}")

    if request.method == 'POST':

        if form.is_valid():
            contact_name = request.POST.get('contact_name', '')
            contact_email = request.POST.get('contact_email', '')
            form_content = request.POST.get('content', '')
            c = Contact()
            c.save(force_insert=True)

            template = get_template('musicae_base/contact_email.txt')
            mail_context = {
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            }
            content = template.render(mail_context)

            email = EmailMessage(
                f"contact form submission #{c.pk}", #
                content,
                #"Fundamenta Musicae",
                to=settings.CONTACT_EMAILS,
                headers={'Reply-To': contact_email}
            )
            # print(email)
            email.send()
            form = ContactForm()
            successClass = "w3-show"
        else:
            form = ContactForm(request.POST)
            failClass = "w3-show"

    else:
        form = ContactForm()

    context = {
        'form': form,
        'capInstruction': ops_text[settings.challenge.op].format(number=mods_text[settings.challenge.mod]),
        'successClass': successClass,
        'failClass': failClass,
    }

    return render(request, 'musicae_base/contact.html', context)
