from django.shortcuts import render

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
