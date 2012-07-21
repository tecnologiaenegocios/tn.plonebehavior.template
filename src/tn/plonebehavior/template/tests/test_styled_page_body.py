from tn.plonebehavior.template.styled_page_body import StyledPageBody

import stubydoo
import unittest


class TestStyledPageBody(unittest.TestCase):

    def setUp(self):
        self.old_factory = StyledPageBody.contextless_factory

        class ContextlessFactory(object):
            def __init__(self, url, html):
                self.url, self.html = url, html
            def __unicode__(self):
                return u', '.join((self.url, self.html))
        StyledPageBody.contextless_factory = ContextlessFactory

    def tearDown(self):
        StyledPageBody.contextless_factory = self.old_factory

    def test_returns_html_attribute_from_original_context(self):
        context = stubydoo.double(
            body=stubydoo.double(output=u'original HTML'),
            absolute_url=lambda self:u'URL'
        )
        self.assertEquals(unicode(StyledPageBody(context)),
                          u'URL, original HTML')
