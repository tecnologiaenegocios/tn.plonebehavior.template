from tn.plonebehavior.template.html_attribute import HTMLPageHTMLAttribute

import stubydoo
import unittest


class TestHTMLPageHTMLAttribute(unittest.TestCase):

    def test_returns_html_attribute_from_original_context(self):
        context = stubydoo.double(html=u'original HTML')
        self.assertEquals(HTMLPageHTMLAttribute(context).html, u'original HTML')
