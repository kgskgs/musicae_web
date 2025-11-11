from django import forms

class BibTeXImportForm(forms.Form):
    bib_file = forms.FileField(
        label="BibTeX File (.bib)",
        help_text="Upload a .bib file to import publications."
    )