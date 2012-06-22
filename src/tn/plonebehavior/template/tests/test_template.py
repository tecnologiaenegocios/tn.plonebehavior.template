from plone.behavior.interfaces import IBehavior
from plone.behavior.interfaces import IBehaviorAssignable
from Products.CMFDefault.Document import Document
from stubydoo import double
from tn.plonebehavior.template import getTemplate
from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template import IHasTemplate
from tn.plonebehavior.template import ITemplating
from tn.plonebehavior.template import ITemplateConfiguration
from tn.plonebehavior.template import MissingTemplateError
from tn.plonebehavior.template import Templating
from tn.plonebehavior.template import TemplateConfiguration
from tn.plonebehavior.template import Template
from tn.plonebehavior.template import TemplatedView
from tn.plonebehavior.template.interfaces import IPossibleTemplate
from tn.plonebehavior.template.tests import base
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.testing import placelesssetup
from zope.interface import providedBy

import stubydoo
import unittest
import zope.component
import zope.interface
import zope.publisher.interfaces.browser


@stubydoo.assert_expectations
class TestTemplateConfiguration(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.context = double()
        zope.interface.alsoProvides(self.context, IAttributeAnnotatable)
        self.configuration = TemplateConfiguration(self.context)

        @zope.component.adapter(IAttributeAnnotatable)
        @zope.interface.implementer(IAnnotations)
        def annotations_adapter(context):
            if hasattr(context, '_annotations'):
                return context._annotations
            context._annotations = {}
            return context._annotations
        zope.component.provideAdapter(annotations_adapter)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_use_adapter_for_html_attribute(self):
        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTMLAttribute)
        def html_attribute_adapter(context):
            return double(html=u'HTML Code')
        zope.component.provideAdapter(html_attribute_adapter)

        self.assertEquals(self.configuration.html, u'HTML Code')

    def test_cannot_set_html_attribute(self):
        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTMLAttribute)
        def html_attribute_adapter(context):
            return double(html=u'HTML Code')
        zope.component.provideAdapter(html_attribute_adapter)
        self.configuration.html = u'Other HTML Code'

        self.assertEquals(self.configuration.html, u'HTML Code')

    def test_xpath_has_a_default_value(self):
        self.assertEquals(self.configuration.xpath,
                          u"descendant-or-self::*[@id = 'template-content']")

    def test_persists_xpath(self):
        self.configuration.xpath = u'A XPath expression'

        other_configuration = TemplateConfiguration(self.context)
        self.assertEquals(other_configuration.xpath, u'A XPath expression')


    def test_css_has_a_default_value(self):
        self.assertEquals(self.configuration.css, u'#template-content')

    def test_persists_css(self):
        self.configuration.css = u'#other-id'

        other_configuration = TemplateConfiguration(self.context)
        self.assertEquals(other_configuration.css, u'#other-id')

    def test_css_sets_xpath(self):
        self.configuration.css = u'#other-id'

        other_configuration = TemplateConfiguration(self.context)
        self.assertEquals(other_configuration.xpath,
                          u"descendant-or-self::*[@id = 'other-id']")

    def test_marks_the_content_when_xpath_is_set(self):
        self.configuration.xpath = 'a Xpath expression'
        self.assertTrue(IPossibleTemplate in providedBy(self.context))

    def test_unmarks_the_content_when_xpath_is_emptied(self):
        self.configuration.xpath = 'a XPath expression'
        self.configuration.xpath = None
        self.assertTrue(IPossibleTemplate not in providedBy(self.context))

    def test_doesnt_break_if_content_is_unmarked_when_xpath_is_emptied(self):
        self.configuration.xpath = 'a XPath expression'
        zope.interface.noLongerProvides(self.context, IPossibleTemplate)
        self.configuration.xpath = None
        self.assertTrue(IPossibleTemplate not in providedBy(self.context))

    def test_marks_the_content_when_css_is_set(self):
        self.configuration.css = 'a CSS expression'
        self.assertTrue(IPossibleTemplate in providedBy(self.context))

    def test_unmarks_the_content_when_css_is_emptied(self):
        self.configuration.css = 'a CSS expression'
        self.configuration.css = None
        self.assertTrue(IPossibleTemplate not in providedBy(self.context))

    def test_doesnt_break_if_content_is_unmarked_when_css_is_emptied(self):
        self.configuration.css = 'a CSS expression'
        zope.interface.noLongerProvides(self.context, IPossibleTemplate)
        self.configuration.css = None
        self.assertTrue(IPossibleTemplate not in providedBy(self.context))


@stubydoo.assert_expectations
class TestTemplateAdapter(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        class Compiler(object):
            zope.component.adapts(None, ITemplateConfiguration)
            zope.interface.implements(interfaces.ITemplateCompiler)
            def __init__(self, context, config):
                self.context, self.config = context, config
            def compile(self):
                return self.config.html % self.context.body

        class Configuration(object):
            zope.component.adapts(IAttributeAnnotatable)
            zope.interface.implements(ITemplateConfiguration)
            def __init__(self, context):
                self.html = u'html(%s)'

        zope.component.provideAdapter(Compiler)
        zope.component.provideAdapter(Configuration)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_delegates_to_adapters(self):
        context = double()
        zope.interface.alsoProvides(context, IAttributeAnnotatable)

        content = double(body=u'body')

        template = Template(context)

        self.assertEquals(template.compile(content), u'html(body)')


@stubydoo.assert_expectations
class TestTemplating(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)
        self.context = double()

        zope.interface.alsoProvides(self.context, IAttributeAnnotatable)
        @zope.component.adapter(IAttributeAnnotatable)
        @zope.interface.implementer(IAnnotations)
        def annotations_adapter(context):
            if hasattr(context, '_annotations'):
                return context._annotations
            context._annotations = {}
            return context._annotations
        zope.component.provideAdapter(annotations_adapter)

        self.templating = Templating(self.context)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_defaults_template_to_none(self):
        self.assertTrue(self.templating.template is None)

    def test_persists_template_in_content_object(self):
        self.templating.template = 'A new template'
        new_templating = Templating(self.context)
        self.assertEquals(new_templating.template, 'A new template')

    def test_marks_the_content_when_template_is_set(self):
        self.templating.template = 'A new template'
        self.assertTrue(IHasTemplate in providedBy(self.context))

    def test_unmarks_the_content_when_template_is_emptied(self):
        self.templating.template = 'A new template'
        self.templating.template = None
        self.assertTrue(IHasTemplate not in providedBy(self.context))

    def test_doesnt_break_if_content_is_unmarked_when_template_is_emptied(self):
        self.templating.template = 'A new template'
        zope.interface.noLongerProvides(self.context, IHasTemplate)
        self.templating.template = None
        self.assertTrue(IHasTemplate not in providedBy(self.context))


class TestTemplateConfigurationBehaviorRegistration(base.TestCase):

    def test_behavior_is_registered(self):
        self.assertTrue(zope.component.queryUtility(
            IBehavior,
            name=ITemplateConfiguration.__identifier__
        ) is not None)


class TestTemplatingBehaviorRegistration(base.TestCase):

    def test_behavior_is_registered(self):
        self.assertTrue(zope.component.queryUtility(
            IBehavior,
            name=ITemplating.__identifier__
        ) is not None)


@stubydoo.assert_expectations
class TestTemplatedViewRendering(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.context = double()
        self.templating_behavior = double(template=None)

        @zope.component.adapter(None)
        @zope.interface.implementer(ITemplating)
        def templating_behavior(context):
            return self.templating_behavior

        zope.component.provideAdapter(templating_behavior)
        self.view = TemplatedView(self.context, 'a request')

    def tearDown(self):
        placelesssetup.tearDown()

    def test_context_with_template_set(self):
        template_content = double()
        template_relation = double(to_object=template_content)

        self.templating_behavior.template = template_relation

        zope.interface.alsoProvides(template_content, IPossibleTemplate)

        template = double()
        stubydoo.stub(template, 'compile').\
                with_args(self.context).and_return(u'Compilation result')

        @zope.component.adapter(IPossibleTemplate)
        @zope.interface.implementer(interfaces.ITemplate)
        def template_adapter(context):
            return template

        zope.component.provideAdapter(template_adapter)

        self.assertEquals(self.view.render(), u'Compilation result')

    def test_context_without_template(self):
        self.templating_behavior.template = None

        self.assertRaises(
            MissingTemplateError,
            self.view.render,
        )


@stubydoo.assert_expectations
class TestGetTemplateFunction(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.context = double()
        self.templating_behavior = double(template=None)

        @zope.component.adapter(None)
        @zope.interface.implementer(ITemplating)
        def templating_behavior(context):
            return self.templating_behavior

        zope.component.provideAdapter(templating_behavior)
        self.view = TemplatedView(self.context, 'a request')

    def tearDown(self):
        placelesssetup.tearDown()

    def test_context_with_template_set(self):
        template_content = double()
        template_relation = double(to_object=template_content)

        zope.interface.alsoProvides(template_content, IPossibleTemplate)

        self.templating_behavior.template = template_relation

        template = double()
        @zope.component.adapter(IPossibleTemplate)
        @zope.interface.implementer(interfaces.ITemplate)
        def template_adapter(context):
            return template

        zope.component.provideAdapter(template_adapter)

        self.assertTrue(getTemplate(self.context) is template)

    def test_context_without_template(self):
        self.templating_behavior.template = None
        self.assertTrue(getTemplate(self.context) is None)
