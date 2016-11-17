


def getHTML_hrefanchor(s):
    id = '_'.join(s.split())
    return '''<a href="#{}">{}</a>'''.format(id, s)

