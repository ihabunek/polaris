"""
Converts the books from a Polaris CD ROM to single page HTML files from which
ebooks can easily be generated.
"""

import os
import re
import sys

from collections import namedtuple
from subprocess import call

Book = namedtuple("Book", ["slug", "title", "author"])


def list_books(root):
    with open("{}/html/s1.html".format(root), "rb") as f:
        page = f.read().decode("windows-1250")

    pattern = r'<A HREF="(\w+)/naslov.html" target="_top">(.+)</A>'
    matches = re.findall(pattern, page, re.IGNORECASE)

    for slug, name in matches:
        if "," in name:
            title, author = name.split(",")
        else:
            title = name
            author = ""

        yield Book(
            slug.upper(),
            title.strip().title(),
            author.strip(),
        )


def process_page(path):
    with open(path, "rb") as f:
        page = f.read().decode("windows-1250")

    pattern = r'<td>(.+)</td>'
    match = re.search(pattern, page, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    contents = match.group(1)

    # Fix linebreaks
    contents = contents.replace("\r\n", "\n")

    # Fix paragraphs
    contents = contents.replace("<BR>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", "</p><p>")
    contents = contents.replace("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", "")
    contents = contents.replace("<BR>\n</p>", "</p>\n")
    contents = contents.replace("\n</p><p>", "</p>\n<p>")

    # Fix headers with no ending tag
    contents = re.sub(r"<H(\d)>(.+)\n", r"<h\1>\2</h\1>\n", contents, re.IGNORECASE)

    return contents


def process_book(book, root):
    with open("{}/html/{}/menu.html".format(root, book.slug), "rb") as f:
        menu = f.read().decode("windows-1250")

    pattern = r'<A HREF=(p\d+\.html) target=frbody>'
    pages = re.findall(pattern, menu, re.IGNORECASE)

    content = []
    for page in pages:
        path = "{}/html/{}/{}".format(root, book.slug, page)
        content.append(process_page(path))

    return "\n\n\n".join(content)

def wrap_boilerplate(content, title):
    return """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="hr-HR">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>{}</title>
</head>
<body>
{}
</body>
</html>""".format(title, content)

def main(source_dir, target_dir):
    books = list(list_books(source_dir))
    count = len(books)

    for i, book in enumerate(books):
        title = "{} - {}".format(book.author, book.title) if book.author else book.title

        content = process_book(book, source_dir)
        content = wrap_boilerplate(content, title)

        title = title.replace("/", "-")
        title = title.replace(":", " -")
        path = "{}/{}.html".format(target_dir, title)

        with open(path, "w", encoding="utf8") as f:
            f.write(content)

        print("[{}/{}] {}".format(i + 1, count, path))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Expected two arguments: source and target folders")

    source_dir = sys.argv[1].rstrip("/")
    target_dir = sys.argv[2].rstrip("/")

    if not os.path.isdir(source_dir):
        sys.exit("Not a directory: " + source_dir)

    if not os.path.isdir(target_dir):
        sys.exit("Not a directory: " + target_dir)

    main(source_dir, target_dir)
