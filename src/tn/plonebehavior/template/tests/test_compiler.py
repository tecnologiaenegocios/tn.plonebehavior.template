from tn.plonebehavior.template import interfaces
from tn.plonebehavior.template.compiler import StyledPageTemplateCompiler
from tn.plonebehavior.template.compiler import TemplateCompiler
from zope.app.testing import placelesssetup
from zope.keyreference.interfaces import IKeyReference

import zope.component
import zope.interface
import stubydoo
import unittest


class TestTemplateCompiler(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)

        self.document = stubydoo.double()
        self.document.body = u'<p>Test!</p>'
        self.config = stubydoo.double()

        @zope.component.adapter(None)
        @zope.interface.implementer(interfaces.IBodyAttribute)
        def body_attribute(doc):
            return stubydoo.double(body=doc.body)

        zope.component.provideAdapter(body_attribute)

        self.compiler = TemplateCompiler(self.document, self.config)

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


class TestStyledPageCompiler(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp(self)
        self.config = stubydoo.double()

        # This kind of document uses a rich text field, which has an output
        # attribute.
        self.document = stubydoo.double(body=stubydoo.double())
        self.document.body.output = u'<p>Test!</p>'

        self.compiler = StyledPageTemplateCompiler(self.document, self.config)

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
