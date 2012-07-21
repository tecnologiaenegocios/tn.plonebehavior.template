try:
    from tn.plonestyledpage import styled_page
    HAS_STYLED_PAGE = True
except ImportError:
    HAS_STYLED_PAGE = False

if HAS_STYLED_PAGE:
    from five import grok
    from tn.plonebehavior.template import interfaces
    from tn.plonebehavior.template.html import ContextlessHTML

    class StyledPageBody(grok.Adapter):
        grok.context(styled_page.IStyledPageSchema)
        grok.implements(interfaces.IHTMLBody)

        contextless_factory = ContextlessHTML

        def __unicode__(self):
            base_url = self.context.absolute_url()
            return unicode(self.contextless_factory(base_url,
                                                    self.context.body.output))
