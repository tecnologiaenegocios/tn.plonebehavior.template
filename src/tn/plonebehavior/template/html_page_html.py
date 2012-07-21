from five import grok
from tn.plonebehavior.template import interfaces

try:
    from tn.plonehtmlpage import html_page
    html_page # pyflakes
    HAS_HTML_PAGE = True
except ImportError:
    HAS_HTML_PAGE = False

if HAS_HTML_PAGE:
    class HTMLPageHTML(grok.Adapter):
        grok.context(html_page.IHTMLPageSchema)
        grok.implements(interfaces.IHTML)
        def __unicode__(self):
            return self.context.html
