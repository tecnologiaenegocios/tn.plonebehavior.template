from stubydoo import double
from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template import NullTemplateConfiguration
from tn.plonebehavior.template.compilation_strategy import StyledPageCompilationStrategy
from tn.plonebehavior.template.compilation_strategy import CompilationStrategy
from zope.app.testing import placelesssetup

import lxml.html
import stubydoo
import unittest
import zope.component
import zope.interface


class TestCompilationStrategy(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.document = stubydoo.double()
        self.document.body = u'<p>Test!</p>'
        self.config = stubydoo.double()

        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTMLBody)
        def body_attribute(doc):
            return stubydoo.double(__unicode__=lambda self:doc.body)

        zope.component.provideAdapter(body_attribute)

        self.compiler = CompilationStrategy(self.document, self.config)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_element_selection(self):
        self.config.html = u"<html><body><div></div></body></html>"
        self.config.xpath = u'/html/body/div'

        result = self.compiler.compile()

        self.assertEquals(result,
                          u'<html><body><div><p>Test!</p></div></body></html>')

    def test_element_replacement(self):
        self.config.html = u"<html><body><div>This should go away</div></body></html>"
        self.config.xpath = u'/html/body/div'

        result = self.compiler.compile()

        self.assertEquals(result,
                          u'<html><body><div><p>Test!</p></div></body></html>')

    def test_element_children_replacement(self):
        self.config.html = u"<html><body><div><a>a</a><br /></div></body></html>"
        self.config.xpath = u'/html/body/div'

        result = self.compiler.compile()

        self.assertEquals(result,
                          u'<html><body><div><p>Test!</p></div></body></html>')

    def test_element_tail_replacement(self):
        self.config.html = u"<html><body><div><a>a</a>Tail</div></body></html>"
        self.config.xpath = u'/html/body/div'

        result = self.compiler.compile()

        self.assertEquals(result,
                          u'<html><body><div><p>Test!</p></div></body></html>')

    def test_attribute_selection_returns_unmodified_tree(self):
        self.config.html = u'<html><body><div dir="ltr"></div></body></html>'
        self.config.xpath = u'/html/body/div/@dir'

        result = self.compiler.compile()

        self.assertEquals(result, self.config.html)

    def test_arbitrary_xpath_returns_unmodified_tree(self):
        self.config.html = u'<html><body><div dir="ltr"></div></body></html>'
        self.config.xpath = u'1+1'

        result = self.compiler.compile()

        self.assertEquals(result, self.config.html)

    def test_none_xpath_returns_unmodified_tree(self):
        self.config.html = u'<html><body><div dir="ltr"></div></body></html>'
        self.config.xpath = None

        result = self.compiler.compile()

        self.assertEquals(result, self.config.html)

    def test_blank_xpath_returns_unmodified_tree(self):
        self.config.html = u'<html><body><div dir="ltr"></div></body></html>'
        self.config.xpath = u''

        result = self.compiler.compile()

        self.assertEquals(result, self.config.html)


class TestCompilationStrategyWithNullConfiguration(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_compilation_with_default_xpath_and_css(self):
        context = double()
        configuration = double(
            xpath=NullTemplateConfiguration.xpath,
            css=NullTemplateConfiguration.css,
            html=u'<html><body></body></html>'
        )

        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTMLBody)
        def body_adapter(context):
            return double(__unicode__=lambda self:u'<p>Hello</p>')
        zope.component.provideAdapter(body_adapter)

        expected_body = u'<body><p>Hello</p></body>'

        strategy = CompilationStrategy(context, configuration)
        result = strategy.compile()
        resulting_body = lxml.html.document_fromstring(result).\
                xpath(u'//body')[0]

        self.assertEquals(
            expected_body,
            lxml.html.tostring(resulting_body)
        )


class BaseTestStyledPageCompilationStrategy(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)
        self.config = stubydoo.double()

        # This kind of document uses a rich text field, which has an output
        # attribute.
        self.document = stubydoo.double(body=stubydoo.double())
        self.document.body = u'<p>Test!</p>'

        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IHTMLBody)
        def html_body(doc):
            return doc.body
        zope.component.provideAdapter(html_body)

        self.compiler = StyledPageCompilationStrategy(self.document, self.config)

        # This 'stubbing' relies on the fact that the function is accessed
        # through module's getattr always, no references kept.
        from tn.plonestyledpage import styled_page
        self.old_getUniqueId = styled_page.getUniqueId
        styled_page.getUniqueId = lambda page: u'foo'

        self.old_getEscapedStyleBlock = styled_page.getEscapedStyleBlock
        styled_page.getEscapedStyleBlock = lambda page: u'<style>%s</style>' % page.styles

        self.document.styles = u'p{color:red}'

    def tearDown(self):
        placelesssetup.tearDown()
        from tn.plonestyledpage import styled_page
        styled_page.getUniqueId = self.old_getUniqueId
        styled_page.getEscapedStyleBlock = self.old_getEscapedStyleBlock


class TestStyledPageCompilationStrategy(BaseTestStyledPageCompilationStrategy):

    def test_element_selection(self):
        self.config.html = u"<html><head></head><body></body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<body><div id="foo"><p>Test!</p></div></body>' in result)

    def test_element_replacement(self):
        self.config.html = u"<html><head></head><body>This should go away</body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<body><div id="foo"><p>Test!</p></div></body>' in result)

    def test_element_children_replacement(self):
        self.config.html = u"<html><head></head><body><a>a</a><br /></body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<body><div id="foo"><p>Test!</p></div></body>' in result)

    def test_element_tail_replacement(self):
        self.config.html = u"<html><head></head><body><a>a</a>Tail</body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<body><div id="foo"><p>Test!</p></div></body>' in result)

    def test_styles_are_added_into_head(self):
        self.config.html = u"<html><head></head><body></body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)

    def test_original_head_content_is_kept_before_styles(self):
        self.config.html = u'<html><head><title>Bar</title><style>p{color:green}</style></head><body></body></html>'
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<head><title>Bar</title><style>p{color:green}</style><style>p{color:red}</style></head>' in result)

    def test_head_is_created_if_not_present(self):
        self.config.html = u"<html><body></body></html>"
        self.config.xpath = u'/html/body'

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)

    def test_attribute_selection_returns_unmodified_body(self):
        self.config.html = u'<html><head></head><body dir="ltr"></body></html>'
        self.config.xpath = u'/html/body/@dir'

        result = self.compiler.compile()

        self.assertTrue(u'</head><body dir="ltr"></body></html>' in result)

    def test_attribute_selection_still_adds_styles(self):
        self.config.html = u'<html><head></head><body dir="ltr"></body></html>'
        self.config.xpath = u'/html/body/@dir'

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)

    def test_arbitrary_xpath_returns_unmodified_body(self):
        self.config.html = u'<html><head></head><body dir="ltr"></body></html>'
        self.config.xpath = u'1+1'

        result = self.compiler.compile()

        self.assertTrue(u'</head><body dir="ltr"></body></html>' in result)

    def test_arbitrary_xpath_still_adds_styles(self):
        self.config.html = u'<html><head></head><body><div dir="ltr"></div></body></html>'
        self.config.xpath = u'1+1'

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)

    def test_none_xpath_returns_unmodified_body(self):
        self.config.html = u'<html><head></head><body dir="ltr"></body></html>'
        self.config.xpath = None

        result = self.compiler.compile()

        self.assertTrue(u'</head><body dir="ltr"></body></html>' in result)

    def test_none_xpath_still_adds_styles(self):
        self.config.html = u'<html><head></head><body><div dir="ltr"></div></body></html>'
        self.config.xpath = None

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)

    def test_blank_xpath_returns_unmodified_body(self):
        self.config.html = u'<html><head></head><body dir="ltr"></body></html>'
        self.config.xpath = u''

        result = self.compiler.compile()

        self.assertTrue(u'</head><body dir="ltr"></body></html>' in result)

    def test_blank_xpath_still_adds_styles(self):
        self.config.html = u'<html><head></head><body><div dir="ltr"></div></body></html>'
        self.config.xpath = u''

        result = self.compiler.compile()

        self.assertTrue(u'<head><style>p{color:red}</style></head>' in result)


class TestStyledPageCompilationStrategyWithNullConfiguration(
    BaseTestStyledPageCompilationStrategy
):

    def setUp(self):
        super(TestStyledPageCompilationStrategyWithNullConfiguration,
              self).setUp()
        self.config = double(
            xpath=NullTemplateConfiguration.xpath,
            css=NullTemplateConfiguration.css,
            html=u'<html><body></body></html>'
        )
        self.compiler = StyledPageCompilationStrategy(self.document, self.config)

    def test_compilation_with_default_xpath_and_css(self):
        expected_body = u'<body><div id="foo">%s</div></body>' % self.document.body

        result = self.compiler.compile()
        resulting_body = lxml.html.document_fromstring(result).\
                xpath(u'//body')[0]

        self.assertEquals(
            expected_body,
            lxml.html.tostring(resulting_body)
        )
