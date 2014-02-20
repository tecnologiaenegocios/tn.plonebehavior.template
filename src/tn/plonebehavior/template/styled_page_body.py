try:
    from tn.plonestyledpage import styled_page
    HAS_STYLED_PAGE = True
except ImportError:
    HAS_STYLED_PAGE = False

if HAS_STYLED_PAGE:
    from five import grok
    from tn.plonebehavior.template import interfaces

    class StyledPageBody(grok.Adapter):
        grok.context(styled_page.IStyledPageSchema)
        grok.implements(interfaces.IHTMLBody)

        def __unicode__(self):
            return self.context.transform_body()
