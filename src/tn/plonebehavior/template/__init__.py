from five import grok
from Products.CMFCore.utils import getToolByName
from Products.Five import browser
from persistent.dict import PersistentDict
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.directives import form
from plone.formwidget.contenttree.source import ObjPathSourceBinder
from plone.supermodel import model
from tn.plonebehavior.template import interfaces
from z3c.form import validator
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory

import collections
import lxml.cssselect
import lxml.html
import z3c.relationfield
import zope.component
import zope.globalrequest
import zope.interface
import zope.schema


_ = MessageFactory('tn.plonebehavior.template')
isiterable = lambda o: isinstance(o, collections.Iterable)
template_configuration_key = 'tn.plonebehavior.template.TemplateConfiguration'
templating_key = 'tn.plonebehavior.template.Templating'


def _validate_css_selector(css_selector):
    try:
        lxml.cssselect.CSSSelector(css_selector)
    except AssertionError:
        raise zope.interface.Invalid(_(u'The CSS expression is invalid.'))
    return True


class ITemplateConfiguration(model.Schema):

    form.omitted('html')
    html = zope.schema.SourceText(title=_(u'HTML'), readonly=True)

    form.fieldset(
        'template-configuration',
        label=_(u'Template configuration'),
        fields=['css'],
    )
    css = zope.schema.TextLine(
        title=_(u'CSS selector'),
        description=_(u'The CSS expression which selects the element where '
                      u'the content will go to.'),
        constraint=_validate_css_selector,
        required=False
    )

    form.omitted('xpath')
    xpath = zope.schema.TextLine(
        title=_(u'XPath selector'),
        description=_(u'The XPath expression which selects the element where '
                      u'the content will go to.  A CSS expression will '
                      u'override this.'),
        required=False
    )


zope.interface.alsoProvides(ITemplateConfiguration, form.IFormFieldProvider)


def _validate_xpath_selector_within_html(html, xpath):
    tree = lxml.html.document_fromstring(html)
    selection = tree.xpath(xpath)
    if not isiterable(selection) or len(selection) != 1:
        return False
    return True


class CSSSelectorValidator(validator.StrictSimpleFieldValidator):
    def validate(self, value):
        super(CSSSelectorValidator, self).validate(value)

        if not value:
            return

        html = interfaces.IHTML(self.context, None)
        if html is None:
            return

        xpath = lxml.cssselect.CSSSelector(value).path
        if not _validate_xpath_selector_within_html(unicode(html), xpath):
            raise zope.interface.Invalid(_(
                "Expression doesn't select a single element "
                "in the HTML page."
            ))


validator.WidgetValidatorDiscriminators(
    CSSSelectorValidator,
    field=ITemplateConfiguration['css']
)

grok.global_adapter(CSSSelectorValidator)


class INullTemplateConfiguration(ITemplateConfiguration):
    """A template configuration for null templates.
    """


class TemplateConfiguration(object):
    """Store template configuration attributes.
    """
    grok.implements(ITemplateConfiguration)
    grok.adapts(IAttributeAnnotatable)

    def __init__(self, context):
        self.context = context

    @property
    def html(self):
        return unicode(interfaces.IHTML(self.context))

    @property
    def xpath(self):
        return self.annotations().get('xpath')

    @xpath.setter
    def xpath(self, value):
        if value and _validate_xpath_selector_within_html(self.html, value):
            zope.interface.alsoProvides(self.context,
                                        interfaces.IPossibleTemplate)
        else:
            zope.interface.noLongerProvides(self.context,
                                            interfaces.IPossibleTemplate)
        self.annotations()['xpath'] = value

    @property
    def css(self):
        return self.annotations().get('css')

    @css.setter
    def css(self, value):
        if value:
            xpath = lxml.cssselect.CSSSelector(value).path
            self.xpath = xpath
        else:
            self.xpath = None
        self.annotations()['css'] = value

    def annotations(self):
        annotations = IAnnotations(self.context)
        if template_configuration_key not in annotations:
            annotations[template_configuration_key] = PersistentDict()
        return annotations[template_configuration_key]


possibleTemplates = ObjPathSourceBinder(**dict(
    object_provides=interfaces.IPossibleTemplate.__identifier__
))


class NullTemplateConfiguration(object):
    """A null template configuration.

    This addresses the case of the content not having an associated
    template.  A NullTemplate object is used then, and this is the
    configuration used for such a template.
    """
    grok.implements(INullTemplateConfiguration)

    xpath = u'//body'
    css = u'body'

    def __init__(self, context):
        self.context = context

    @property
    def html(self):
        return u"%(doctype)s\n<html %(html_attrs)s>%(head)s%(body)s</html>" % {
            'doctype': u'<!DOCTYPE html>',
            'html_attrs': u'lang="%s"' % self.get_language(),
            'head': self.get_head(),
            'body': u'<body></body>'
        }

    def get_language(self):
        metadata = ICategorization(self.context, None)
        if metadata and metadata.language:
            return metadata.language
        return self.get_language_from_portal()

    def get_language_from_portal(self):
        request = zope.globalrequest.getRequest()
        portal_state = zope.component.getMultiAdapter(
            (self.context, request),
            name="plone_portal_state"
        )
        return portal_state.default_language()

    def get_head(self):
        return u"<head><title>%s</title></head>" % self.context.title


class ITemplating(model.Schema):

    template = z3c.relationfield.RelationChoice(
        title=_(u'Template'),
        description=_(u'The content item which will be the template for this '
                      u'one'),
        source=possibleTemplates,
        required=False
    )

    template_object = zope.interface.Attribute(
        u'The underlying template object of the template relation'
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

    @property
    def template(self):
        return self.annotations().get('template')

    @template.setter
    def template(self, value):
        if value:
            zope.interface.alsoProvides(self.context, IHasTemplate)
        else:
            zope.interface.noLongerProvides(self.context, IHasTemplate)
        self.annotations()['template'] = value

    @property
    def template_object(self):
        possible_template = self.template
        if possible_template is not None:
            return possible_template.to_object
        return NullTemplate(self.context)

    def annotations(self):
        annotations = IAnnotations(self.context)
        if templating_key not in annotations:
            annotations[templating_key] = PersistentDict()
        return annotations[templating_key]


class Template(grok.Adapter):
    """A template.

    This object extracts configuration from a possible template and
    delegates to a compilation strategy.
    """
    grok.context(interfaces.IPossibleTemplate)
    grok.implements(interfaces.ITemplate)

    def compile(self, content):
        return zope.component.getMultiAdapter(
            (content, ITemplateConfiguration(self.context)),
            interfaces.ICompilationStrategy
        ).compile()


class AssociatedTemplate(grok.Adapter):
    """An associated template.

    This object extracts a template from its context and delegates the
    compilation task to it.

    The context must have the ITemplating behavior active.
    """
    grok.context(IHasTemplate)
    grok.implements(interfaces.ITemplate)

    def compile(self, content):
        template = self.get_template()
        return template.compile(content)

    def get_template(self):
        possible_template = ITemplating(self.context).template_object
        return interfaces.ITemplate(possible_template)


class NullTemplate(object):
    """A null template.

    This kind of template just displays the content's body.  Delegates
    to a compilation strategy multi adapting the content and self.
    """
    def __init__(self, context):
        self.context = context

    def compile(self, content):
        return zope.component.getMultiAdapter(
            (content, NullTemplateConfiguration(content)),
            interfaces.ICompilationStrategy
        ).compile()


class TemplatedView(grok.View):
    grok.context(IHasTemplate)
    grok.name('templated-view')
    grok.require('zope2.View')

    def render(self):
        template = interfaces.ITemplate(self.context)
        return template.compile(self.context)


# This view is not automatically registered.
class DefaultView(browser.BrowserView):
    index = browser.pagetemplatefile.ViewPageTemplateFile('template.pt')

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        base_resources_path = (
            portal_url + '/++resource++tn.plonebehavior.template/'
        )

        self.frame_id = u'frame-%s' % self.context.__name__
        self.javascript_url = base_resources_path + 'template.js'
        self.stylesheet_url = base_resources_path + 'template.css'

        return self.index()
