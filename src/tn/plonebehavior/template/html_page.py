try:
    from tn.plonehtmlpage import html_page
    HAS_HTML_PAGE = True
except ImportError:
    HAS_HTML_PAGE = False

if HAS_HTML_PAGE:
    from five import grok
    from plone import api
    from Products.statusmessages.interfaces import IStatusMessage
    from tn.plonebehavior.template import _
    from tn.plonebehavior.template import interfaces
    from tn.plonebehavior.template.html import ContextlessHTML

    class HTML(grok.Adapter):
        grok.context(html_page.IHTMLPageSchema)
        grok.implements(interfaces.IHTML)

        contextless_factory = ContextlessHTML

        def __unicode__(self):
            base_url = self.context.absolute_url()
            return unicode(self.contextless_factory(base_url,
                                                    self.context.html))

    class View(html_page.View):
        grok.context(html_page.IHTMLPageSchema)
        grok.layer(interfaces.IBrowserLayer)
        grok.require('zope2.View')

        def update(self):
            super(View, self).update()

            if api.user.is_anonymous():
                # Anonymous users are unlikely to be interested in knowing if
                # the page being viewed can work as a template.
                return

            if interfaces.IPossibleTemplate.providedBy(self.context):
                IStatusMessage(self.request).add(
                    _(u'This item can be used as a template.'),
                    type=u'info',
                )

        def render(self):
            return super(View, self).render()
