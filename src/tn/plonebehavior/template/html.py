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
        absolutize_links(tree, self.base_url)
        return lxml.html.tostring(tree)


def absolutize_links(tree, base_href):
    def _keep_anchors(link):
        if link.startswith(base_href + '#'):
            # Make internal anchors be just internal anchors.
            return '#'.join([''] + link.split('#')[1:])
        return link
    tree.rewrite_links(_keep_anchors, base_href=base_href)
