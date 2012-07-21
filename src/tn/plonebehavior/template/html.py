import lxml.html


class ContextlessHTML(object):
    """HTML independent of context.

    It can be either an HTML fragment or a full page.
    """

    def __init__(self, base_url, html):
        self.base_url = base_url
        self.html = html

    def __unicode__(self):
        tree = lxml.html.fromstring(self.html)
        tree.make_links_absolute(self.base_url)
        return lxml.html.tostring(tree)
