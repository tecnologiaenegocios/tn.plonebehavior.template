from tn.plonebehavior.template.html import ContextlessHTML

import lxml.html
import unittest


class TestContextlessHTML(unittest.TestCase):

    def setUp(self):
        self.host_url = 'http://example.com:666/'
        self.folder_url = self.host_url + 'folder/'
        self.item_url = self.folder_url + 'item'

    def test_output_with_url_ending_in_a_folder(self):
        self.context_url = self.folder_url
        self.make_assertion()

    def test_output_with_url_ending_in_an_item(self):
        self.context_url = self.item_url
        self.make_assertion()

    def make_assertion(self):
        html = lxml.html.tostring(lxml.html.fromstring(u'''<html>
            <head>
                <script src="http://otherhost.com/javascript.js"></script>
                <script src="/javascripts/app.js"></script>
                <link href="/styles/app.css" />
                <style>/*<![CDATA[*/
                    @import url('styles/additional.css');
                /*]]>*/</style>
                <style>/*<![CDATA[*/
                    body { background-image: url(image.png); }
                /*]]>*/</style>
            </head>
            <body>
                <img src="path/image.png" />
                <a href="./page.html">Page</a>
                <a href="page.html">Page</a>
                <a href="mailto:bob@example.com">Send me spam!</a>
                <a href="javascript:alert('Hacked!');">Hack me!</a>
                <a href="#anchor">Anchor</a>
                <a href="path/file.pdf">File</a>
                <a href="../file.pdf">File</a>
                <div style="background-image: url('image.png');">
                    Content
                </div>
            </body>
        </html>'''))
        expected_output = lxml.html.tostring(lxml.html.fromstring(u'''<html>
            <head>
                <script src="http://otherhost.com/javascript.js"></script>
                <script src="%(host_url)sjavascripts/app.js"></script>
                <link href="%(host_url)sstyles/app.css" />
                <style>/*<![CDATA[*/
                    @import url('%(folder_url)sstyles/additional.css');
                /*]]>*/</style>
                <style>/*<![CDATA[*/
                    body { background-image: url(%(folder_url)simage.png); }
                /*]]>*/</style>
            </head>
            <body>
                <img src="%(folder_url)spath/image.png" />
                <a href="%(folder_url)spage.html">Page</a>
                <a href="%(folder_url)spage.html">Page</a>
                <a href="mailto:bob@example.com">Send me spam!</a>
                <a href="javascript:alert('Hacked!');">Hack me!</a>
                <a href="%(full_url)s#anchor">Anchor</a>
                <a href="%(folder_url)spath/file.pdf">File</a>
                <a href="%(host_url)sfile.pdf">File</a>
                <div style="background-image: url('%(folder_url)simage.png');">
                    Content
                </div>
            </body>
        </html>''' % dict(folder_url=self.folder_url,
                          full_url=self.context_url,
                          host_url=self.host_url)))

        contextless_html = ContextlessHTML(self.context_url, html)
        self.assertEquals(unicode(contextless_html), expected_output)
