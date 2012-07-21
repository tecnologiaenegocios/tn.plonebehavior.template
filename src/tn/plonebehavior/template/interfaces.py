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


class ICompilationStrategy(zope.interface.Interface):
    """A template compiler
    """

    def compile():
        """Return the compilation result.
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
