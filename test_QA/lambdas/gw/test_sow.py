from osbot_aws.apis.Lambda import Lambda
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

    def test_invoke_directly(self):
        issue_id = 'SOW-121'
        payload = {"headless": False, "issue_id": issue_id}
        self.png_data = run(payload, None)






    def test__invoke_in_lambda(self):
        self.test_update_lambda()
        issue_id = 'SOW-121'
        payload = { "issue_id" : issue_id }
        self.png_data = self.aws_lambda.invoke(payload)



























