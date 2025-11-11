from django.shortcuts import render, get_object_or_404
from .models import Contact
from .forms import ContactForm
from musicae_web import settings

from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from operator import __add__, __sub__


def PageView(request, link):
    """
    If Page.link is a ForeignKey to UrlItem(target=...), we should filter by link__target.
    If Page.link is a CharField, this still works (change link__target to link).
    """
    try:
        # Most likely case (given you use page.link.text in the template):
        page = get_object_or_404(
            Page.objects.select_related("link"),
            link__target=link,  # <-- match incoming slug to UrlItem.target
        )
    except Exception:
        # Fallback if Page.link is actually a CharField (not a FK):
        page = get_object_or_404(Page, link=link)

    context = {
        "content": page.content,
        # You referenced page.link.text, so keep that when it's a FK; fall back gracefully otherwise.
        "title": f"{getattr(getattr(page, 'link', None), 'text', getattr(page, 'link', ''))} - Fundamenta Musicae",
        "description": page.description,
        "keywords": page.keywords,
    }
    return render(request, "musicae_base/genericPage.html", context)


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
    form = ContactForm(request.POST or None)

    failClass = "w3-hide"
    successClass = "w3-hide"

    if request.method == 'POST':
        if form.is_valid():
            contact_name = form.cleaned_data["contact_name"].strip()
            contact_email = form.cleaned_data["contact_email"].strip()
            form_content = form.cleaned_data["content"].strip()

            # persist if you need a PK in the subject
            c = Contact.objects.create()

            content = get_template('musicae_base/contact_email.txt').render({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            })

            # from_email defaults to settings.DEFAULT_FROM_EMAIL if omitted
            email = EmailMessage(
                subject=f"contact form submission #{c.pk}",
                body=content,
                to=settings.CONTACT_EMAILS,
                reply_to=[contact_email],          # <-- real Reply-To header
                headers={"X-Contact-Form": "musicae"},
            )

            try:
                email.send(fail_silently=False)
                # Post/Redirect/Get to avoid resubmits + show success banner
                request.session["contact_success"] = True
                return redirect(f"{reverse('contact')}#contact")
            except SMTPException:
                failClass = "w3-show"
        else:
            failClass = "w3-show"

    # GET: show success if we just redirected after a successful send
    if request.session.pop("contact_success", False):
        successClass = "w3-show"

    return render(request, 'musicae_base/contact.html', {
        'form': form,
        'capInstruction': ops_text[settings.challenge.op].format(number=mods_text[settings.challenge.mod]),
        'successClass': successClass,
        'failClass': failClass,
    })