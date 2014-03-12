import zope.interface


class IPossibleTemplate(zope.interface.Interface):
    """Marker interface for objects which can be a template for another.

    If something claims to provide this interface, it must be possible
    to adapt it to ITemplate.
    """


class ITemplate(zope.interface.Interface):
    """A template for another content.
    """

    def compile(content):
        """Return the mix between this template and the content's HTML.
        """


class INullTemplate(ITemplate):
    """A template which just outputs its inner content.

    This can be used as a special case fallback when a content item has no
    template associated with it or the template is not found or invalid, but a
    valid template is expected.
    """


class ICompilationStrategy(zope.interface.Interface):
    """A template compiler
    """

    def compile():
        """Return the compilation result.
        """


class ICompilation(zope.interface.Interface):
    """An object that wraps the result of compiling the object's template.
    """

    template = zope.interface.Attribute(u"The template used for compilation.")

    def __unicode__():
        """The compilation result as a unicode string.
        """


class IHTML(zope.interface.Interface):
    """Something that represents a full-page HTML.
    """

    def __unicode__():
        """The HTML as a unicode string.
        """


class IHTMLBody(zope.interface.Interface):
    """Something that has only stuff that normally goes into a <body> tag.
    """

    def __unicode__():
        """The inner content of the body tag as a unicode string.
        """


class IBrowserLayer(zope.interface.Interface):
    """A layer specific to this product.
    """
