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
    from zope.lifecycleevent import ObjectModifiedEvent
    from zope.event import notify

    import tn.plonebehavior.template as main
    import zope.interface

    IPossibleTemplate = interfaces.IPossibleTemplate

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

            if self._should_be_template():
                if self._can_be_template():
                    # This should be have been done by the
                    # ITemplateConfiguration adapter, but when its fields are
                    # not modified when editing the item, that adapter is not
                    # used at all.  Thus, in order to keep correctness and to
                    # workaround this fact (that the adapter is not used), we
                    # mark the item here and issue a modified event.  This is
                    # not optimal, since GETs should be safe, and we're
                    # probably responding to a GET request here...
                    if not IPossibleTemplate.providedBy(self.context):
                        zope.interface.alsoProvides(self.context,
                                                    IPossibleTemplate)
                        notify(ObjectModifiedEvent(self.context))
                else:
                    # In this situation, we expect that a grok.subscriber
                    # already registered for IPossibleTemplate to already have
                    # removed that marker interface.  We just warn the user.
                    IStatusMessage(self.request).add(
                        _("This item has a selector set for usage as a "
                          "template, but the selector doesn't match a "
                          "single HTML element. If you really wish to use "
                          "this item as a template, edit it and modify "
                          "the selector in the Template configuration "
                          "tab or the HTML code to make them match. "
                          "If instead you wish this item to be a regular "
                          "HTML page, edit it, go to the Template "
                          "configuration tab, and leave the selector field "
                          "in blank."),
                        type=u'warning',
                    )

            if IPossibleTemplate.providedBy(self.context):
                IStatusMessage(self.request).add(
                    _(u'This item can be used as a template.'),
                    type=u'info',
                )

        def render(self):
            return super(View, self).render()

        def _should_be_template(self):
            config = main.ITemplateConfiguration(self.context)
            return not not config.xpath

        def _can_be_template(self):
            config = main.ITemplateConfiguration(self.context)
            return config.xpath and main.html_contains_xpath_single(
                config.html, config.xpath
            )
