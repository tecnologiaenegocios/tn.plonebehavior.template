from tn.plonebehavior.template.html_page_html import HTMLPageHTML

import stubydoo
import unittest


class TestHTMLPageHTML(unittest.TestCase):

    def test_returns_html_attribute_from_original_context(self):
        context = stubydoo.double(html=u'original HTML')
        self.assertEquals(unicode(HTMLPageHTML(context)), u'original HTML')
