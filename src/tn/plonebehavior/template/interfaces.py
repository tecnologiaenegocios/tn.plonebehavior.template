from tn.plonebehavior.template import _

import zope.interface


class IPossibleTemplate(zope.interface.Interface):
    """Marker interface for objects which can be a template for another.
    """


class ITemplate(zope.interface.Interface):
    """A template for another content.
    """

    def compile(content):
        """Return the mix between this template and the content's HTML.
        """


class ITemplateCompiler(zope.interface.Interface):
    """A template compiler
    """

    def compile():
        """Return the compilation result.
        """


class IHTMLAttribute(zope.interface.Interface):
    """Something that has a HTML attribute.
    """
    html = zope.schema.SourceText(title=_(u'HTML'))


class IBodyAttribute(zope.interface.Interface):
    """Something that has only stuff that normally goes into a <body> tag.
    """
    body = zope.schema.SourceText(title=_(u'Body'))


class IRenderer(zope.interface.Interface):
    """Render a content.

    This is intended to be used as an adapter for the content object in
    "structure" expressions in view templates.
    """

    def render():
        """Perform rendering.

        If the content has a template, use it.  Otherwise, just return a
        significant HTML representation of the content.
        """
