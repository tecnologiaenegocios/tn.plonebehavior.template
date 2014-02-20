try:
    from tn.plonehtmlpage import html_page
    HAS_HTML_PAGE = True
except ImportError:
    HAS_HTML_PAGE = False

if HAS_HTML_PAGE:
    from five import grok
    from tn.plonebehavior.template import _
    from tn.plonebehavior.template import ITemplateConfiguration
    from tn.plonebehavior.template import interfaces
    from tn.plonebehavior.template.html import ContextlessHTML
    from z3c.form import validator

    import collections
    import lxml.cssselect
    import lxml.html
    import zope.interface

    isiterable = lambda o: isinstance(o, collections.Iterable)

    class HTMLPageHTML(grok.Adapter):
        grok.context(html_page.IHTMLPageSchema)
        grok.implements(interfaces.IHTML)

        contextless_factory = ContextlessHTML

        def __unicode__(self):
            base_url = self.context.absolute_url()
            return unicode(self.contextless_factory(base_url,
                                                    self.context.html))

    class CSSSelectorValidator(validator.SimpleFieldValidator):
        def validate(self, value):
            super(CSSSelectorValidator, self).validate(value)

            tree = lxml.html.document_fromstring(self.context.html)
            xpath = lxml.cssselect.CSSSelector(value).path
            selection = tree.xpath(xpath)
            if not isiterable(selection) or len(selection) != 1:
                raise zope.interface.Invalid(_(
                    "Expression doesn't select a single element "
                    "in the HTML page."
                ))

    validator.WidgetValidatorDiscriminators(
        CSSSelectorValidator,
        context=html_page.IHTMLPageSchema,
        field=ITemplateConfiguration['css']
    )

    grok.global_adapter(CSSSelectorValidator)
