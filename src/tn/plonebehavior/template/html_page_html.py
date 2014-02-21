try:
    from tn.plonehtmlpage import html_page
    HAS_HTML_PAGE = True
except ImportError:
    HAS_HTML_PAGE = False

if HAS_HTML_PAGE:
    from five import grok
    from tn.plonebehavior.template import interfaces
    from tn.plonebehavior.template.html import ContextlessHTML

    class HTMLPageHTML(grok.Adapter):
        grok.context(html_page.IHTMLPageSchema)
        grok.implements(interfaces.IHTML)

        contextless_factory = ContextlessHTML

        def __unicode__(self):
            base_url = self.context.absolute_url()
            return unicode(self.contextless_factory(base_url,
                                                    self.context.html))
