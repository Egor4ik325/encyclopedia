import re


def md_to_html(md):
    """
    Converte string from Markdown to HTML
    :param md: Markdown string
    :returns: HTML string
    """
    # Split string lines
    lines = re.split(r'\n', md)

    def line_to_html(line):
        """
        Converte line from Markdown to HTML.
        Match inline elements (bold, italic, link) and 
        line elements (heading, paragraph, list).
        """
        # Return empty line
        if not line:
            return line

        # Match bold (to the first closing '**')
        bold = re.compile(r'\*{2}(.+?)\*{2}')
        bolds = bold.findall(line)
        for b in bolds:
            line = bold.sub(f'<b>{b}</b>', line, 1)

        # Match italic
        italic = re.compile(r'\*(.+?)\*')
        italics = italic.findall(line)
        for i in italics:
            line = italic.sub(f'<i>{i}</i>', line, 1)

        # Match links
        link = re.compile(r'\[(.+?)\]\((.+?)\)')
        links = link.findall(line)
        for l in links:
            line = link.sub(f'<a href="{l[1]}">{l[0]}</a>', line, 1)

        # Match headings
        heading = re.compile(r'(#+)\s+')
        head = heading.match(line)
        if head:
            # Heading level (number of '#')
            hl = len(head.group(1))
            # Get text after #+
            heading_text = re.search(r'[^#+\s+].+', line).group()
            line = f'<h{hl}>{heading_text}</h{hl}>'
            return line

        # Match lists
        l = re.compile(r'\s*(-|\*|\d+.)\s+')
        lst = l.match(line)
        if lst:
            # Text after -\s
            list_text = line[lst.end():]
            list_type = 'ul' if lst.group(1) in '-*' else 'ol'
            line = f'<{list_type} style="margin-bottom: 0;"><li>{list_text}</li></{list_type}>'
            return line

        # Math paragraphs
        if line:
            line = f'<p>{line}</p>'
            return line

        return line

    html = '\n'.join([line_to_html(line) for line in lines])
    return html


if __name__ == '__main__':
    print(md_to_html("""# Hello
## World
My name is **Egor**, I'm a *student*.
Yes, it will be processed with regex.

I like:
- programming (any kinds)
- problem solving (usually programming or math or life)
- and self-development"""))
