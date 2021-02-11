import sys
from gw_bot.Deploy import Deploy
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell
from osbot_aws.helpers.Lambda_Package import Lambda_Package
from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.utils import Misc
from osbot_utils.utils.Files import Files

sys.path.append('../osbot_browser')

import base64
from syncer import sync
from unittest import TestCase

from osbot_browser.browser.API_Browser                import API_Browser


class test_API_Browser(TestCase):

    def setUp(self):
         self.api = API_Browser(headless = False)

    #@unittest.skip("bug: needs to load markdow page first")
    @sync
    async def test_js_eval(self):
        text = "some_text"
        text_base64 = base64.b64encode(text.encode()).decode()
        assert await self.api.js_eval("btoa('{0}')".format(text))        == text_base64
        assert await self.api.js_eval("atob('{0}')".format(text_base64)) == text

    @sync
    async def test_html(self):
        await self.api.open('https://www.google.com')
        html = await self.api.html()
        assert len(html) > 100

    @sync
    async def test_open(self):
        (headers, status, url, browser) = await self.api.open('https://www.google.com')
        assert headers['x-frame-options'] == 'SAMEORIGIN'
        assert status                     == 200
        assert url                        == 'https://www.google.com/'

    @sync
    async def test_page(self):
        url = 'https://www.google.com/404'
        await self.api.open(url)
        page = await self.api.page()
        assert page.url == url


    @sync
    async def test_screenshot(self):
        await self.api.open('https://news.bbc.co.uk')
        file = await self.api.screenshot()
        assert Files.exists(file)

    def test_open(self):
        page = 'chrome://settings/help'
        self.api.sync__open(page)

class test_API_Browser_in_AWS(Test_Helper):

    def setUp(self):
        super().setUp()
        self.lambda_name = 'osbot_browser.lambdas.dev.browser_test'
        self._lambda = Lambda(self.lambda_name)
        self.api_browser_code = """
from osbot_aws.Dependencies import load_dependencies        
load_dependencies('syncer')        
from osbot_browser.browser.API_Browser import API_Browser        
api_browser = API_Browser()
"""

    def auth_key(self):
        return Lambda_Shell().get_lambda_shell_auth()

    def _invoke_shell_command(self, command, kwargs=None):
        params = {'lambda_shell': {'method_name': command , 'method_kwargs': kwargs , 'auth_key': self.auth_key()}}
        return self._lambda.invoke(params)

    def _invoke_python_code(self, code):
        code = self.api_browser_code + code
        return self._lambda.shell_python_exec(code, self.auth_key())

    def _invoke_python_line(self, line_of_code):
        code = self.api_browser_code + "result = " + line_of_code
        return self._lambda.shell_python_exec(code, self.auth_key())

    def _reset_lambda(self):
        Lambda_Package(self.lambda_name).reset()

    @group_by
    def _lambda_process_list(self):
        def parse_ps_aux(raw_data):

            import re
            regex = re.compile('[\s]+')
            lines = raw_data.split('\n')

            headers = regex.split(lines.pop(0))
            data = []
            for line in lines:
                item = {}
                for index, header in enumerate(headers):
                    values = regex.split(line)
                    item[header] = Misc.array_get(values, index)

                data.append(item)
            return data

        ps_aux = self._invoke_shell_command('list_processes')
        return parse_ps_aux(ps_aux)

    def _lambda_chrome_processes(self):
        return self._lambda_process_list(group_by='COMMAND').get('/tmp/lambdas-dependencies/pyppeteer/headless_shell')

    def _lambda_headless_shell_processes(self):
        return self._lambda_process_list(group_by='COMMAND').get('[headless_shell]')


    # test methods


    def test_update_lambda(self):
        self.result = Deploy().deploy_lambda__browser_dev(self.lambda_name)

    def test_ctor(self):
        assert self._invoke_python_line('api_browser.file_tmp_last_chrome_session')== '/tmp/browser-last_chrome_session.json'
        assert self._invoke_python_line('api_browser.headless'                    ) == True
        assert self._invoke_python_line('api_browser.new_browser'                 ) == False
        assert self._invoke_python_line('api_browser.log_js_errors_to_console'    ) == True


    def test_load_latest_version_of_chrome(self):
        self._reset_lambda()                                                                            # force lambda cold start
        headless_shell = '/tmp/lambdas-dependencies/pyppeteer/headless_shell'
        code_file_exists = f"""
from osbot_utils.utils.Files import file_exists
result = file_exists('{headless_shell}')
        """
        assert self._invoke_python_code(code_file_exists) is False                                      # check that file doesn't exist after cold start
        assert self._invoke_python_line('api_browser.load_latest_version_of_chrome()') is None          # trigger download of dependency
        assert self._invoke_python_code(code_file_exists) is True                                       # check that now it exists

    def test_sync__setup_browser(self):
        self._reset_lambda()
        code = """                 
from osbot_utils.utils.Files import file_contents             
load_dependencies('requests,pyppeteer,websocket-client')

api_browser.sync__setup_browser()
result = api_browser.get_last_chrome_session()
        """
        assert self._invoke_python_code(code).startswith('ws://127.0.0.1:')
        assert len(self._lambda_chrome_processes()) == 1 # there should only be one process

    def test_sync__setup_browser__new_browser__True(self):
        self._reset_lambda()
        code = """                 
from osbot_utils.utils.Files import file_contents             
load_dependencies('requests,pyppeteer,websocket-client')
api_browser.set_new_browser(True)
api_browser.sync__setup_browser()
result = api_browser.new_browser
        """
        self._invoke_python_code(code)
        assert len(self._lambda_chrome_processes()) == 1                # after call to sync__setup_browser, there should be 1 process
        self._invoke_python_code(code)
        assert len(self._lambda_chrome_processes()) == 2  # now there should be 2
        self._invoke_python_code(code)
        assert len(self._lambda_chrome_processes()) == 3  # now there should be 3
        self._reset_lambda()

        #print(self._invoke_shell_command('disk_space'    ))
        #print(self._invoke_shell_command('list_processes'))
        #print(self._invoke_shell_command('memory_usage'  ))
        #print(self._invoke_shell_command('file_contents' , {'path': '/var/runtime/lambda_runtime_client.py'}))

    def test_sync__screenshot(self):
        #self._reset_lambda()
        code = """                 
from osbot_utils.utils.Files import file_contents             
load_dependencies('requests,pyppeteer,websocket-client')

api_browser.sync__setup_browser()
#api_browser.sync__open('https://www.google.com/')
api_browser.sync__open('https://www.whatismybrowser.com/')

result = api_browser.sync__screenshot_base64()
"""
        self.png_data = self._invoke_python_code(code)

        #self.result = self._invoke_shell_command('list_processes')

class test_workflows_API_Browser(TestCase):

    def setUp(self):
        self.api = API_Browser(headless = False)
        self.png_file = '/tmp/tmp-jira-screenshot.png'

    def test_open_jira_slack(self):
        #url = 'https://os-summit.slack.com/messages/DJ8UA0RFT/'
        url = 'https://os-summit.slack.com/messages/CK475UCJY/'
        self.api.sync__open(url)
        email = 'asd@asd.asd'
        password = "bbb"
        js_code = """$('#email').val('{0}')
                     $('#password').val('{1}')
                     $('#signin_btn').click()
                  """.format(email, password)

        self.api.sync__js_execute(js_code)

        #await self.api.screenshot(file_screenshot=self.png_file)

    @sync
    async def test_open_jira_page(self):
        from osbot_aws.apis.Secrets import Secrets
        self.api = API_Browser(headless=False)

        login_needed = False
        self.secrets_id = 'GS_BOT_GS_JIRA'

        (server, username, password) = Secrets(self.secrets_id).value_from_json_string().values()

        if login_needed:
            #Dev.pprint(server, username, password)
            await self.api.open(server + '/login.jsp')
            page = await self.api.page()
            await page.type('#login-form-username', username)
            await page.type('#login-form-password', password)
            await page.click('#login-form-submit')

        #await self.api.open(server + '/browse/GSP-95')
        #page = await self.api.page()
        #await self.api.js_execute("$('#show-more-links-link').click()")
        #from time import sleep
        #sleep(1)
        await self.api.page_size(2000,3000)

        await self.api.screenshot(file_screenshot='/tmp/tmp-jira-screenshot.png', full_page=True)



class Test_API_Browser___with_browser_not_closing(TestCase):

    def setUp(self):
        self.api = API_Browser(headless=True)

    @sync
    async def test_html(self):
        await self.api.open('https://www.google.co.uk')
        content = await self.api.html()
        assert "Google" in content.html()