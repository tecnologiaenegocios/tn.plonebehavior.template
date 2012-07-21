from five import grok
from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template import ITemplateConfiguration
try:
    from tn.plonestyledpage import styled_page
    styled_page # pyflakes
    HAS_STYLED_PAGE = True
except ImportError:
    HAS_STYLED_PAGE = False

import collections
import lxml.builder
import lxml.html


isiterable = lambda o: isinstance(o, collections.Iterable)


class CompilationStrategy(grok.MultiAdapter):
    grok.adapts(None, ITemplateConfiguration)
    grok.implements(interfaces.ICompilationStrategy)

    def __init__(self, context, template_configuration):
        self.context = context
        self.config = template_configuration

    def compile(self):
        return lxml.html.tostring(self.make_tree_with_content())

    def make_tree_with_content(self):
        tree = lxml.html.document_fromstring(self.config.html)
        if not self.config.xpath:
            return tree
        selection = tree.xpath(self.config.xpath)
        if isiterable(selection):
            for thing in selection:
                if isinstance(thing, lxml.html.HtmlElement):
                    thing.text = u''
                    for child in thing.getchildren():
                        thing.remove(child)
                    thing.extend(self.get_content())
        return tree

    def get_content(self):
        return lxml.html.fragments_fromstring(
            unicode(interfaces.IHTMLBody(self.context))
        )


if HAS_STYLED_PAGE:
    class StyledPageCompilationStrategy(CompilationStrategy):
        grok.adapts(styled_page.IStyledPageSchema, ITemplateConfiguration)
        grok.implements(interfaces.ICompilationStrategy)

        def compile(self):
            tree = self.make_tree_with_content()

            # Add styles.
            styles = styled_page.getEscapedStyleBlock(self.context)
            head = tree.xpath('/html/head')
            if not head:
                tree.insert(0, lxml.builder.E.head())
                head = [tree.head]
            head[0].extend(lxml.html.fragments_fromstring(styles))

            return lxml.html.tostring(tree)

        def get_content(self):
            id = styled_page.getUniqueId(self.context)
            return lxml.html.fragments_fromstring(
                u'<div id="%s">%s</div>' % (id, self.context.body.output)
            )
