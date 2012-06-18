from five import grok
from persistent.dict import PersistentDict
from plone.directives import form
from plone.formwidget.contenttree.source import ObjPathSourceBinder
from Products.CMFCore.interfaces import IContentish
from z3c.relationfield.interfaces import IHasRelations
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
from zope.globalrequest import getRequest

import z3c.relationfield
import zope.component
import zope.interface
import zope.schema


_ = MessageFactory('tn.plonebehavior.template')

from tn.plonebehavior.template import interfaces


default_xpath_selector = u"//*[@id='template-content']"
template_configuration_key = 'tn.plonebehavior.template.TemplateConfiguration'
apply = lambda f: f()


class ITemplateConfiguration(form.Schema):

    form.omitted('html')
    html = zope.schema.SourceText(title=_(u'HTML'))

    xpath = zope.schema.TextLine(
        title=_(u'XPath selector'),
        description=_(u'The XPath expression which selects the element where '
                      u'the content will go to.'),
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
            return self.annotations().get('xpath', None)
        def set(self, value):
            self.annotations()['xpath'] = value
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


class ITemplatingMarker(IHasRelations):
    """Marker interface for content objects which can have a template
    associated (that is, for which ITemplating behavior is active).

    This extends IHasRelations to also tell z3c.relationfield that the
    associated template must be cataloged.
    """
    # Since z3c.relationfield will do an attribute lookup to get the relations
    # to index in its catalog, this field is declared by this interface,
    # although it being just a marker provided by the object on which the
    # behavior ITemplating is assigned, which in turn populates and manages
    # this field.
    _templating_template = z3c.relationfield.RelationChoice(
        source=possibleTemplates,
        required=False,
    )


class IHasTemplate(zope.interface.Interface):
    """Marker interface for content objects which actually have a template
    associated.
    """


class Templating(object):
    """Store a template in a content object.
    """
    grok.implements(ITemplating)
    grok.adapts(IContentish)

    def __init__(self, context):
        self.context = context

    # Instead of storing the template in an annotation, we set an attribute in
    # the content object, because this is the way z3c.relationfield will look
    # for something to index in its catalog.
    @apply
    def template():
        def get(self):
            return getattr(self.context, '_templating_template', None)
        def set(self, value):
            if value:
                zope.interface.alsoProvides(self.context, IHasTemplate)
            else:
                zope.interface.noLongerProvides(self.context, IHasTemplate)
            self.context._templating_template = value
        return property(get, set)


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


class NullTemplate(object):
    """A template which just returns normal item visualization.
    """
    grok.implements(interfaces.ITemplate)

    def compile(self, context):
        return zope.component.getMultiAdapter((context, getRequest()),
                                              name=u'view')()


def getTemplate(context):
    possible_template = ITemplating(context).template

    if possible_template is not None:
        possible_template = possible_template.to_object
    else:
        possible_template = NullTemplate()

    return interfaces.ITemplate(possible_template)


class TemplatedView(grok.View):
    grok.context(ITemplatingMarker)
    grok.name('templated-view')
    grok.require('zope2.View')

    def render(self):
        return getTemplate(self.context).compile(self.context)
