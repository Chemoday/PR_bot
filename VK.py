import time
from selenium import  webdriver
from Database import Auth_module

import config

class VK(object):

    def __init__(self, email, password):
        self.bot_email = email
        self.bot_password = password
        token = self.get_token()
        self.bot_token = token

    def check_token(self):
        #Check bot token status, that token is exist and not expired
        pass

    def get_token(self):
        #Get bot token from database

        pass

    def create_token(self):
        #Create bot token
        try:
            if config.system_type == "Windows":
                driver = webdriver.PhantomJS(executable_path='C:/Program Files (x86)/phantomjs/bin/phantomjs.exe',
                                             service_args=config.service_args,
                                             desired_capabilities=config.dcap)
                driver.get(config.vk_token_url)
            else:
                driver = webdriver.PhantomJS(service_args=config.service_args,
                                             desired_capabilities=config.dcap)

                driver.get(config.vk_token_url)
        except AttributeError:
            print("Problem with phantomJS, possible path is missed")
            return

        try:
            user_input = driver.find_element_by_name("email")
            user_input.send_keys(self.bot_email)
            password_input = driver.find_element_by_name("pass")
            password_input.send_keys(self.bot_password)

            submit = driver.find_element_by_id("install_allow")
            submit.click()
            time.sleep(2)
            current_url = driver.current_url
            #TODO add fail proof parsing
            access_list = (current_url.split("#"))[1].split("&")
            token = (access_list[0].split("="))[1]  # access_token
            driver.close()
            driver.quit()
            print("Got token, sending to server")
            print(token)
        except:
            print("Problem with token page, something is missed")
            return

        Auth_module.set_vk_token(bot_login=self.bot_email, token=token)