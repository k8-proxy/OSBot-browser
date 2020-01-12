import base64

from osbot_aws.apis.Lambda import Lambda
from pbx_gs_python_utils.utils.Dev import Dev

from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_browser.lambdas.gw.sow import run
from gw_bot.Deploy import Deploy

class test_sow(Test_Helper):
    def setUp(self):
        super().setUp()
        self.lambda_name = 'osbot_browser.lambdas.gw.sow'
        self.aws_lambda  = Lambda(self.lambda_name)
        self.result      = None
        self.png_data    = None

    def tearDown(self):
        super().print(self.result)
        super().save_png(self.png_data, '/tmp/lambda_png_file.png')

    def test_update_lambda(self):
        Deploy().setup().deploy_lambda__browser(self.lambda_name)

    def test__invoke(self):
        self.test_update_lambda()
        payload       = { "web_root": "/" , "headless": False}
        self.png_data = self.aws_lambda.invoke(payload)


    def test_invoke_directly(self):
        payload = { "web_root": "." , "headless": False}
        self.png_data = run(payload, None)

















