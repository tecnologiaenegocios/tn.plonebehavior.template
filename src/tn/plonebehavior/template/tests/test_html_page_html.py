from tn.plonebehavior.template.html_page_html import HTMLPageHTML

import stubydoo
import unittest


class TestHTMLPageHTML(unittest.TestCase):

    def setUp(self):
        self.old_factory = HTMLPageHTML.contextless_factory

        class ContextlessFactory(object):
            def __init__(self, url, html):
                self.url, self.html = url, html
            def __unicode__(self):
                return u', '.join((self.url, self.html))
        HTMLPageHTML.contextless_factory = ContextlessFactory

    def tearDown(self):
        HTMLPageHTML.contextless_factory = self.old_factory

    def test_returns_html_attribute_from_original_context(self):
        context = stubydoo.double(html=u'original HTML',
                                  absolute_url=lambda self:u'URL')
        self.assertEquals(unicode(HTMLPageHTML(context)),
                          u'URL, original HTML')
