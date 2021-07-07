from django.shortcuts import render, redirect, reverse
from django.http.response import HttpResponseRedirect
from django.forms import Form, CharField, Textarea
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import util
from random import choice


# Steps validation (ValidationError):
# - field.clean(): - for field.cleaned_data
#    - field.to_python() - conversion to python object
#    - field.validate() - field-specific validation
#    - field.run_validators() - run custom validators
# - form.clean_field()
# - from.clean() - multiple field validation


def validate_already_exists(value):
    """
    Validate entry doesn't exist yet.
    """
    if util.get_entry(value):
        raise ValidationError(
            _("Entry with title \"%(title)s\" already exists."),
            params={'title': value}
        )


class CreateEntryForm(Form):
    title = CharField(max_length=30, validators=[validate_already_exists])
    content = CharField(max_length=1000, widget=Textarea)


class EditEntryForm(Form):
    title = CharField(max_length=30)
    old_title = CharField(max_length=30)
    content = CharField(max_length=1000, widget=Textarea)

    def clean(self):
        """
        Form specific multiple-field validation.
        """
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        old_title = cleaned_data.get('old_title', None)

        # Validation: if already exists and isn't previous
        if util.get_entry(title) and title != old_title:
            # Assign error to the title field
            self.add_error('title', ValidationError(
                _("Entry with title \"%(title)s\" already exists."),
                params={'title': title}
            ))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry_content = util.get_entry(title)
    if not entry_content:
        entry_content = "Sorry, this encyclopedia page doesn't exist."

    context = {'title': title, 'entry': entry_content}
    return render(request, "encyclopedia/entry.html", context)


def search(request):
    """
    Search for the entries simmilar to the passed query string argument.
    """
    # Retrieve query string 'q' from URL parameters
    title = request.GET.get('q')
    entry_names = util.list_entries()

    # Search for specific name
    for entry_name in entry_names:
        if entry_name == title:
            return HttpResponseRedirect(reverse('entry', args=[title]))

    # Search for substring in name
    entries = []
    for entry_name in entry_names:
        if entry_name.lower().find(title) != -1:
            entries.append(entry_name)

    # Respond with list of substring entries or empty
    context = {'search_text': title, 'entries': entries}
    return render(request, "encyclopedia/search.html", context)


def new(request):
    """
    Create new entry.
    """
    if request.method == 'POST':
        # request.GET = QuerySet (model)
        title = request.POST.get('title')
        content = request.POST.get('content')

        # Validate form data
        form_object = CreateEntryForm(
            data={'title': title, 'content': content})
        if not form_object.is_valid():
            # Send errors and entered data to template
            context = {'data': form_object.data, 'errors': form_object.errors}
            return render(request, 'encyclopedia/new.html', context)

        # Save entry
        util.save_entry(title, content)
        return redirect(reverse('entry', args=[title]))

    return render(request, 'encyclopedia/new.html')


def edit(request, title):
    """
    Respond with form for editing topic in URL.
    """
    if request.method == 'POST':
        # request.GET = QuerySet (model)
        new_title = request.POST.get('title')
        content = request.POST.get('content')

        # Validate form data
        form_object = EditEntryForm(
            data={'title': new_title, 'old_title': title,  'content': content})
        if not form_object.is_valid():
            # Send errors and entered data to template
            context = {'data': form_object.data, 'errors': form_object.errors}
            return render(request, 'encyclopedia/edit.html', context)

        # Delete previous entry
        util.delete_entry(title)
        # Save new entry
        util.save_entry(new_title, content)
        return redirect(reverse('entry', args=[new_title]))

    content = util.get_entry(title)
    context = {'data': {'title': title, 'content': content}}
    return render(request, 'encyclopedia/edit.html', context)


def random(request):
    entries = util.list_entries()
    entry = choice(entries)
    return HttpResponseRedirect(reverse('entry', args=[entry]))
