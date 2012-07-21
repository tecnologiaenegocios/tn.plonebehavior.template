from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.behavior.interfaces import IBehavior
from stubydoo import double
from stubydoo import stub
from tn.plonebehavior.template import AssociatedTemplate
from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template import IHasTemplate
from tn.plonebehavior.template import INullTemplateConfiguration
from tn.plonebehavior.template import ITemplating
from tn.plonebehavior.template import ITemplateConfiguration
from tn.plonebehavior.template import NullTemplate
from tn.plonebehavior.template import NullTemplateConfiguration
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

import lxml.html
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
        @zope.interface.implementer(interfaces.IHTML)
        def html_attribute_adapter(context):
            return u'HTML Code'
        zope.component.provideAdapter(html_attribute_adapter)

        self.assertEquals(self.configuration.html, u'HTML Code')

    def test_cannot_set_html_attribute(self):
        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTML)
        def html_attribute_adapter(context):
            return u'HTML Code'
        zope.component.provideAdapter(html_attribute_adapter)

        def set_attribute():
            self.configuration.html = u'Other HTML Code'

        self.assertRaises(AttributeError, set_attribute)

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
class TestNullTemplateConfiguration(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.metadata = double(language='klingon')

        @zope.component.adapter(None)
        @zope.interface.implementer(ICategorization)
        def metadata(context):
            return self.metadata
        zope.component.provideAdapter(metadata)

        self.context = double(title=u'Content title')
        self.configuration = NullTemplateConfiguration(self.context)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_default_xpath_to_select_the_body_tag(self):
        self.assertEquals(self.configuration.xpath, u'//body')

    def test_default_css_to_select_the_body_tag(self):
        self.assertEquals(self.configuration.css, u'body')

    def test_get_language_from_content_if_set(self):
        tree = lxml.html.document_fromstring(self.configuration.html)
        lang = tree.xpath('/html/@lang')[0]
        self.assertEquals(lang, 'klingon')

    def test_get_language_from_portal_if_content_has_no_language(self):
        self.metadata = None
        portal_state_view = double(default_language=lambda self:'mayan')

        @zope.component.adapter(None, None)
        @zope.interface.implementer(zope.publisher.interfaces.browser.IBrowserView)
        def view(context, request):
            return portal_state_view
        zope.component.provideAdapter(view, name=u'plone_portal_state')

        tree = lxml.html.document_fromstring(self.configuration.html)
        lang = tree.xpath('/html/@lang')[0]
        self.assertEquals(lang, 'mayan')

    def test_title_is_retrieved_from_context(self):
        tree = lxml.html.document_fromstring(self.configuration.html)
        title = tree.xpath('/html/head/title')[0].text
        self.assertEquals(title, self.context.title)


@stubydoo.assert_expectations
class TestTemplateAdapter(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        class CompilationStrategy(object):
            zope.component.adapts(None, ITemplateConfiguration)
            zope.interface.implements(interfaces.ICompilationStrategy)
            def __init__(self, content, config):
                self.context, self.config = content, config
            def compile(self):
                return self.config.html % self.context.body

        class Configuration(object):
            zope.component.adapts(IAttributeAnnotatable)
            zope.interface.implements(ITemplateConfiguration)
            def __init__(self, context):
                self.html = u'html(%s)'

        zope.component.provideAdapter(CompilationStrategy)
        zope.component.provideAdapter(Configuration)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_delegates_to_adapters(self):
        context = double()
        content = double(body=u'body')
        zope.interface.alsoProvides(context, IAttributeAnnotatable)

        template = Template(context)

        self.assertEquals(template.compile(content), u'html(body)')


@stubydoo.assert_expectations
class TestAssociatedTemplateAdapter(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.context = double()
        self.templating_behavior = double()
        template_content = double()
        self.templating_behavior.template_object = template_content
        zope.interface.alsoProvides(template_content, IPossibleTemplate)

        @zope.component.adapter(None)
        @zope.interface.implementer(ITemplating)
        def templating_behavior(context):
            return self.templating_behavior
        zope.component.provideAdapter(templating_behavior)

        template = double()
        @zope.component.adapter(IPossibleTemplate)
        @zope.interface.implementer(interfaces.ITemplate)
        def template_adapter(context):
            return template
        zope.component.provideAdapter(template_adapter)

        self.content = double()
        stub(template, 'compile').with_args(self.content).and_return(u'result')

    def tearDown(self):
        placelesssetup.tearDown()

    def test_context_with_template_set(self):
        self.assertEquals(
            AssociatedTemplate(self.context).compile(self.content),
            u'result'
        )


@stubydoo.assert_expectations
class TestNullTemplateAdapter(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)
        self.compilation_strategy = double()

        @zope.component.adapter(None, INullTemplateConfiguration)
        @zope.interface.implementer(interfaces.ICompilationStrategy)
        def compilation_strategy(content, config):
            self.compilation_strategy.context = content
            self.compilation_strategy.config = config
            return self.compilation_strategy

        zope.component.provideAdapter(compilation_strategy)
        stub(self.compilation_strategy, 'compile').\
                and_return('Compilation results')

    def tearDown(self):
        placelesssetup.tearDown()

    def test_delegates_to_adapters(self):
        template = NullTemplate(double())
        self.assertEquals(template.compile(double()), 'Compilation results')

    def test_passes_the_content_object_to_the_strategy_object(self):
        content = double()
        template = NullTemplate(double())
        template.compile(content)

        self.assertTrue(self.compilation_strategy.context is content)

    def test_passes_the_content_object_to_the_configuration_object(self):
        content = double()
        template = NullTemplate(double())
        template.compile(content)

        self.assertTrue(self.compilation_strategy.config.context is content)


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

    def test_defaults_template_object_to_null_template(self):
        template = self.templating.template_object
        self.assertTrue(isinstance(template, NullTemplate))
        self.assertTrue(template.context is self.context)

    def test_persists_template_in_content_object(self):
        relation = double(to_object='template object')
        self.templating.template = relation
        new_templating = Templating(self.context)
        self.assertTrue(new_templating.template is relation)

    def test_returns_back_the_persisted_template_object(self):
        relation = double(to_object='template object')
        self.templating.template = relation
        new_templating = Templating(self.context)
        self.assertEquals(new_templating.template_object, 'template object')

    def test_marks_the_content_when_template_is_set(self):
        relation = double(to_object='template object')
        self.templating.template = relation
        self.assertTrue(IHasTemplate in providedBy(self.context))

    def test_unmarks_the_content_when_template_is_emptied(self):
        relation = double(to_object='template object')
        self.templating.template = relation
        self.templating.template = None
        self.assertTrue(IHasTemplate not in providedBy(self.context))

    def test_returns_null_template_object_if_template_is_emptied(self):
        relation = double(to_object='template object')
        self.templating.template = relation
        self.templating.template = None

        template = self.templating.template_object
        self.assertTrue(isinstance(template, NullTemplate))
        self.assertTrue(template.context is self.context)

    def test_doesnt_break_if_content_is_unmarked_when_template_is_emptied(self):
        relation = double(to_object='template object')
        self.templating.template = relation
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
        self.view = TemplatedView(self.context, 'a request')

    def tearDown(self):
        placelesssetup.tearDown()

    def test_compiles_template_with_context(self):
        template = double()
        stubydoo.stub(template, 'compile').\
                with_args(self.context).and_return(u'Compilation result')

        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.ITemplate)
        def template_adapter(context):
            return template

        zope.component.provideAdapter(template_adapter)

        self.assertEquals(self.view.render(), u'Compilation result')
