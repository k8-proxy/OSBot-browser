from gw_bot.Deploy import Deploy
from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda import Lambda


class test_Chrome_in_Lambda(Test_Helper):

    def setUp(self):
        super().setUp()
        self.lambda_name = 'osbot_browser.lambdas.dev.lambda_shell'
        self._lambda = Lambda(self.lambda_name)

    def test_update_lambda(self):
        self.result = Deploy().deploy_lambda__browser_dev(self.lambda_name)

    def test_update_and_invoke(self):
        self.test_update_lambda()
        code = """
from osbot_aws.Dependencies import load_dependencies        
load_dependencies('pyppeteer,websocket-client')        
from osbot_browser.chrome.Chrome import Chrome       

#from osbot_utils.decorators.Sync import sync
#@sync
#async def browser(chrome):
#    return await chrome.browser_connect()
#browser =  browser(Chrome())

chrome = Chrome().keep_open()
chrome.sync__setup_browser()
#result = browser.process.pid
     
browser = chrome.sync_browser()
result = browser.process.pid        
"""
        self.result = self._lambda.shell().python_exec(code)

# test running webserver in Lambda
    def test_run_webserver_in_lambda(self):
        #self._lambda.shell().reset()
        #self.test_update_lambda()
        code = """
from osbot_aws.Dependencies import load_dependencies        
load_dependencies('pyppeteer,websocket-client')        
from osbot_browser.chrome.Chrome import Chrome       

chrome = Chrome()

load_dependencies('requests')   
from osbot_browser.browser.Web_Server import Web_Server
from osbot_utils.utils.Misc import bytes_to_base64
        
chrome.sync__setup_browser()
#page = chrome.sync_page()
#web_server = Web_Server()
#web_server.port = 1234
#web_server.start()
#with Web_Server() as web_server:    
#chrome.sync_open(web_server.url())
chrome.sync_open('http://localhost:1234/')
result = bytes_to_base64(chrome.sync_screenshot())
# 
# chrome.sync_open('https://www.google.com')
# bytes = chrome.sync_screenshot()
# import base64
# result =  base64.b64encode(bytes).decode()
# #result = chrome.sync_url()
"""

        self.png_data = self._lambda.shell().python_exec(code)

    def test_invoke_shell_commands(self):
        shell = self.result = self._lambda.shell()
        #self.result = shell.ls('/tmp')
        print('-----')
        print(shell.ps())
        #self.result = shell.memory_usage()
        print(shell.list_processes())



#todo: add chrome logs fetch
#todo: add ngrok support
#todo: news.google.com is not working
#bytes = chrome.sync_open('https://news.google.com')