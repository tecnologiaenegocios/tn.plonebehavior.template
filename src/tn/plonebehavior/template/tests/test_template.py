from plone.behavior.interfaces import IBehavior
from plone.behavior.interfaces import IBehaviorAssignable
from Products.CMFDefault.Document import Document
from stubydoo import double
from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template import ITemplating
from tn.plonebehavior.template import ITemplatingMarker
from tn.plonebehavior.template import ITemplateConfiguration
from tn.plonebehavior.template import Templating
from tn.plonebehavior.template import TemplateConfiguration
from tn.plonebehavior.template import Template
from tn.plonebehavior.template import TemplatedView
from tn.plonebehavior.template.tests import base
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.testing import placelesssetup

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

    def test_xpath_defaults_to_none(self):
        self.assertTrue(self.configuration.xpath is None)

    def test_persists_xpath(self):
        self.configuration.xpath = u'A XPath expression'

        other_configuration = TemplateConfiguration(self.context)
        self.assertEquals(other_configuration.xpath, u'A XPath expression')


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
        self.templating = Templating(self.context)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_defaults_template_to_none(self):
        self.assertTrue(self.templating.template is None)

    def test_persists_template_in_content_object_as_an_attribute(self):
        self.templating.template = 'A new template'
        self.assertEquals(self.context._templating_template, 'A new template')


class TestTemplateConfigurationBehaviorRegistration(base.TestCase):

    def afterSetUp(self):
        super(TestTemplateConfigurationBehaviorRegistration, self).afterSetUp()

        self.context = Document('document')
        zope.interface.alsoProvides(self.context, IAttributeAnnotatable)
        self.behavior_assignable_factory = None

        # This will enable the behavior for our document.
        class BehaviorAssignable(object):
            zope.component.adapts(Document)
            zope.interface.implements(IBehaviorAssignable)
            def __init__(self, context):
                self.context = context
            def supports(self, behavior_interface):
                return behavior_interface is ITemplateConfiguration
            def enumerate_behaviors(self):
                yield zope.component.queryUtility(
                    IBehavior, name=ITemplateConfiguration.__identifier__
                )

        zope.component.provideAdapter(BehaviorAssignable)
        self.behavior_assignable_factory = BehaviorAssignable

    def beforeTearDown(self):
        zope.component.getGlobalSiteManager().\
                unregisterAdapter(self.behavior_assignable_factory)

    def test_behavior_is_registered(self):
        self.assertTrue(zope.component.queryUtility(
            IBehavior,
            name=ITemplateConfiguration.__identifier__
        ) is not None)

    def test_behavior_has_correct_marker(self):
        behavior = zope.component.queryUtility(
            IBehavior,
            name=ITemplateConfiguration.__identifier__
        )
        if behavior is None:
            self.fail('behavior not registered')
        else:
            self.assertTrue(behavior.marker is interfaces.IPossibleTemplate)

    def test_behavior_is_usable(self):
        adapted = ITemplateConfiguration(self.context, None)
        self.assertTrue(adapted is not None)


@stubydoo.assert_expectations
class TestTemplatingMarkerHasRelations(unittest.TestCase):
    def runTest(self):
        from z3c.relationfield.interfaces import IHasRelations
        self.assertTrue(IHasRelations in ITemplatingMarker.__iro__)


class TestTemplatingBehaviorRegistration(base.TestCase):

    def afterSetUp(self):
        super(TestTemplatingBehaviorRegistration, self).afterSetUp()

        self.context = Document('document')
        self.behavior_assignable_factory = None

        # This will enable the behavior for our document.
        class BehaviorAssignable(object):
            zope.component.adapts(Document)
            zope.interface.implements(IBehaviorAssignable)
            def __init__(self, context):
                self.context = context
            def supports(self, behavior_interface):
                return behavior_interface is ITemplating
            def enumerate_behaviors(self):
                yield zope.component.queryUtility(IBehavior,
                                                  name=ITemplating.__identifier__)

        zope.component.provideAdapter(BehaviorAssignable)
        self.behavior_assignable_factory = BehaviorAssignable

    def beforeTearDown(self):
        zope.component.getGlobalSiteManager().\
                unregisterAdapter(self.behavior_assignable_factory)

    def test_behavior_is_registered(self):
        self.assertTrue(zope.component.queryUtility(
            IBehavior,
            name=ITemplating.__identifier__
        ) is not None)

    def test_behavior_has_correct_marker(self):
        behavior = zope.component.queryUtility(
            IBehavior,
            name=ITemplating.__identifier__
        )
        if behavior is None:
            self.fail('behavior not registered')
        else:
            self.assertTrue(behavior.marker is ITemplatingMarker)

    def test_behavior_is_usable(self):
        adapted = ITemplating(self.context, None)
        self.assertTrue(adapted is not None)


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

        zope.interface.alsoProvides(template_content,
                                    interfaces.IPossibleTemplate)

        template = double()
        stubydoo.stub(template, 'compile').\
                with_args(self.context).and_return(u'Compilation result')

        @zope.component.adapter(interfaces.IPossibleTemplate)
        @zope.interface.implementer(interfaces.ITemplate)
        def template_adapter(context):
            return template

        zope.component.provideAdapter(template_adapter)

        self.assertEquals(self.view.render(), u'Compilation result')


    def test_context_without_template(self):
        self.templating_behavior.template = None

        @zope.component.adapter(None, None)
        @zope.interface.implementer(zope.publisher.interfaces.browser.IBrowserView)
        def default_view(context, request):
            return double(__call__=lambda x: u'Default view')

        zope.component.provideAdapter(default_view, name=u'view')

        self.assertEquals(self.view.render(), u'Default view')
