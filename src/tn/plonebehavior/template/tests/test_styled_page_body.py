from tn.plonebehavior.template.styled_page_body import StyledPageBody

import stubydoo
import unittest


class TestStyledPageBody(unittest.TestCase):
    def test_returns_html_attribute_from_original_context(self):
        context = stubydoo.double(transform_body=lambda self: u'body')
        self.assertEquals(unicode(StyledPageBody(context)), u'body')
