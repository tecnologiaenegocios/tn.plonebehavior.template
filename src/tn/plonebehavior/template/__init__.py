from five import grok
from Products.CMFCore.utils import getToolByName
from Products.Five import browser
from persistent.dict import PersistentDict
from plone.directives import form
from plone.formwidget.contenttree.source import ObjPathSourceBinder
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory

import lxml.cssselect
import z3c.relationfield
import zope.component
import zope.interface
import zope.schema


_ = MessageFactory('tn.plonebehavior.template')

from tn.plonebehavior.template import interfaces


default_css_selector = u"#template-content"
default_xpath_selector = lxml.cssselect.CSSSelector(default_css_selector).path
template_configuration_key = 'tn.plonebehavior.template.TemplateConfiguration'
templating_key = 'tn.plonebehavior.template.Templating'
apply = lambda f: f()


class ITemplateConfiguration(form.Schema):

    form.omitted('html')
    html = zope.schema.SourceText(title=_(u'HTML'))

    form.fieldset(
        'template-configuration',
        label=_(u'Template configuration'),
        fields=['css',],
    )
    css = zope.schema.TextLine(
        title=_(u'CSS selector'),
        description=_(u'The CSS expression which selects the element where '
                      u'the content will go to.'),
        default=default_css_selector,
        required=False
    )

    form.omitted('xpath')
    xpath = zope.schema.TextLine(
        title=_(u'XPath selector'),
        description=_(u'The XPath expression which selects the element where '
                      u'the content will go to.  A CSS expression will '
                      u'override this.'),
        default=default_xpath_selector,
        required=False
    )


zope.interface.alsoProvides(ITemplateConfiguration, form.IFormFieldProvider)


class TemplateConfiguration(object):
    """Store template configuration attributes.
    """
    grok.implements(ITemplateConfiguration)
    grok.adapts(IAttributeAnnotatable)

    def __init__(self, context):
        self.context = context

    @apply
    def html():
        def get(self):
            return interfaces.IHTMLAttribute(self.context).html
        def set(self, value):
            # Do nothing, since this field is computed.
            return
        return property(get, set)

    @apply
    def xpath():
        def get(self):
            return self.annotations().get('xpath', default_xpath_selector)
        def set(self, value):
            if value:
                zope.interface.alsoProvides(self.context,
                                            interfaces.IPossibleTemplate)
            else:
                zope.interface.noLongerProvides(self.context,
                                                interfaces.IPossibleTemplate)
            self.annotations()['xpath'] = value
        return property(get, set)

    @apply
    def css():
        def get(self):
            return self.annotations().get('css', default_css_selector)
        def set(self, value):
            if value:
                xpath = lxml.cssselect.CSSSelector(value).path
                self.xpath = xpath
            else:
                self.xpath = None
            self.annotations()['css'] = value
        return property(get, set)

    def annotations(self):
        annotations = IAnnotations(self.context)
        if template_configuration_key not in annotations:
            annotations[template_configuration_key] = PersistentDict()
        return annotations[template_configuration_key]


possibleTemplates = ObjPathSourceBinder(dict(
    object_provides=interfaces.IPossibleTemplate.__identifier__
))


class ITemplating(form.Schema):

    template = z3c.relationfield.RelationChoice(
        title=_(u'Template'),
        description=_(u'The content item which will be the template for this '
                      u'one'),
        source=possibleTemplates,
        required=False
    )


zope.interface.alsoProvides(ITemplating, form.IFormFieldProvider)


class ITemplatingMarker(zope.interface.Interface):
    """BBB - kept here for compatibility.

    Marker interface for content objects which can have a template
    associated (that is, for which ITemplating behavior is active).

    This extends IHasRelations to also tell z3c.relationfield that the
    associated template must be cataloged.
    """


class IHasTemplate(zope.interface.Interface):
    """Marker interface for content objects which actually have a template
    associated.
    """


class Templating(object):
    """Store a template in a content object.
    """
    grok.implements(ITemplating)
    grok.adapts(IAttributeAnnotatable)

    def __init__(self, context):
        self.context = context

    # Instead of storing the template in an annotation, we set an attribute in
    # the content object, because this is the way z3c.relationfield will look
    # for something to index in its catalog.
    @apply
    def template():
        def get(self):
            return self.annotations().get('template')
        def set(self, value):
            if value:
                zope.interface.alsoProvides(self.context, IHasTemplate)
            else:
                zope.interface.noLongerProvides(self.context, IHasTemplate)
            self.annotations()['template'] = value
        return property(get, set)

    def annotations(self):
        annotations = IAnnotations(self.context)
        if templating_key not in annotations:
            annotations[templating_key] = PersistentDict()
        return annotations[templating_key]


class Template(grok.Adapter):
    """A template.
    """
    grok.context(interfaces.IPossibleTemplate)
    grok.implements(interfaces.ITemplate)

    def compile(self, content):
        return zope.component.getMultiAdapter(
            (content, ITemplateConfiguration(self.context)),
            interfaces.ITemplateCompiler
        ).compile()


class MissingTemplateError(StandardError):
    pass


def getTemplate(context):
    """Get the template of the given content object.

    The content object must have the ITemplating behavior active.
    Return None if no template is found.
    """
    possible_template = ITemplating(context).template

    if possible_template is None:
        return None

    possible_template = possible_template.to_object

    return interfaces.ITemplate(possible_template)


class TemplatedView(grok.View):
    grok.context(IHasTemplate)
    grok.name('templated-view')
    grok.require('zope2.View')

    def render(self):
        template = getTemplate(self.context)
        if template is not None:
            return template.compile(self.context)
        raise MissingTemplateError(u'Cannot find a template in this context.')


# This view is not automatically registered.
class DefaultView(browser.BrowserView):
    index = browser.pagetemplatefile.ViewPageTemplateFile('template.pt')

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        base_resources_path = portal_url + '/++resource++tn.plonebehavior.template/'

        self.frame_id = u'frame-%s' % self.context.__name__
        self.javascript_url = base_resources_path + 'template.js'
        self.stylesheet_url = base_resources_path + 'template.css'

        return self.index()
