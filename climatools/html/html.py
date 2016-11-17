


def getHTML_hrefanchor(s):
    id = '_'.join(s.split())
    return '''<a href="#{}">{}</a>'''.format(id, s)



def getHTML_idanchor(s):
    id = '_'.join(s.split())
    return '''<a id="{}"></a>'''.format(id)
