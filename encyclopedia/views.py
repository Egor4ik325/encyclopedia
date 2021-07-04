from django.shortcuts import render, reverse
from django.http.response import HttpResponseRedirect

from . import util


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