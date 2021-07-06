from django.shortcuts import render, redirect, reverse
from django.http.response import HttpResponseRedirect
from django.forms import Form, CharField, Textarea
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import util


def validate_already_exists(value):
    """
    Validate entry doesn't exist yet.
    """
    if util.get_entry(value):
        raise ValidationError(
            _("Entry with title \"%(title)s\" already exists."),
            params={'title': value}
        )


class EntryForm(Form):
    title = CharField(max_length=30, validators=[validate_already_exists])
    # TextField = CharField with <textarea> widget
    content = CharField(max_length=1000, widget=Textarea)


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
        form_object = EntryForm(data={'title': title, 'content': content})
        if not form_object.is_valid():
            # Send errors and entered data to template
            context = {'data': form_object.data, 'errors': form_object.errors}
            return render(request, 'encyclopedia/new.html', context)

        # Save entry
        util.save_entry(title, content)
        return redirect(reverse('entry', args=[title]))

    return render(request, 'encyclopedia/new.html')
