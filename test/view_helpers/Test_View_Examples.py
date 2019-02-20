import os
from unittest import TestCase

from browser.Render_Page import Render_Page
from src.view_helpers.View_Examples import View_Examples
from utils.Dev import Dev
from utils.Misc import Misc
from utils.Zip_Folder import Zip_Folder


class Test_View_Examples(TestCase):
    def setUp(self):
        self.view_examples = View_Examples('/tmp/test_screenshot_html.png')
        self.clip          = {'x': 1, 'y': 1, 'width': 520, 'height': 50}

    def test_hello_world_content(self):
        result = self.view_examples.hello_world__html()
        assert '<h1>Hello World.....</h1>' in result.html()

    def test_hello_world    (self): self.view_examples.set_clip(self.clip).hello_world()
    def test_bootstrap_cdn  (self): self.view_examples.set_clip(self.clip).bootstrap_cdn()
    def test_folder_root    (self): self.view_examples.folder_root()

    def test_visjs_simnple  (self): self.view_examples.render_file_from_zip('/examples/vis-js.html')

    def test_render_file_from_zip(self): self.view_examples.render_file_from_zip('/examples/hello-world.html')