import time
import requests
import re
from bs4 import BeautifulSoup

from selenium import webdriver

from Database import Keys
import config
class FB(object):

    def __init__(self, email):
        self.bot_email = email
        print(email)
        #self.bot_password = Keys.get_bot_FB_pass(bot_FB_login=email)

        self.bot_password = 'xxxxxxx'


    def __repr__(self):
        output = "Email: {email} | Token: {token}".format(email=self.bot_email, token=self.bot_token)
        return output

    def parse_group_members(self,fb_group_id):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images":2}
        driver = webdriver.Chrome(chrome_options=chromeOptions,
                                  executable_path='C:\selenium_drivers\chromedriver.exe')
        group_url = 'https://www.facebook.com/groups/{0}/members/'.format(fb_group_id)
        driver.get(group_url)
        time.sleep(2)

        login_input = driver.find_element_by_name('email')
        login_input.send_keys(self.bot_email)
        password_input = driver.find_element_by_name('pass')
        password_input.send_keys(self.bot_password)
        submit = driver.find_element_by_name('login')
        submit.click()
        #You will be redirected to page after login.
        time.sleep(2)
        html_source = driver.page_source
        FB._parse_group_members(html_source=html_source)
        driver.quit()

    @staticmethod
    def _parse_group_members(html_source):
        html = BeautifulSoup(html_source, 'html.parser')
        user_names_list_raw = html.findAll(re.compile("^'/ajax/hovercard/user.php?'"))
        for row in user_names_list_raw:
            print(row)


