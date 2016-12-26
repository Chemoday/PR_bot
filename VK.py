import time
import datetime
from selenium import webdriver
from Database import Keys, Groups, Users
import requests
from bs4 import BeautifulSoup
import json
import config
from Users import User



class VK(object):

    def __init__(self, email, password):
        self.bot_email = email
        self.bot_password = Keys.get_bot_pass(email)
        #self.bot_password = password Change on more secure method
        self.bot_token = self.get_token()

    def __repr__(self):
        output = "Email: {email} | Token: {token}".format(email=self.bot_email, token=self.bot_token)
        return output

    def check_token(self, token):
        #Check bot token status, that token is exist and not expired
        now = datetime.datetime.now().timestamp()
        if token.vk_token_expire_dt > now:
            print("Token is active")
            return True
        else:
            print("Token expired")
            return False

    def get_token(self):
        #Get bot token from database
        token = Keys.get_vk_token(email=self.bot_email)
        if token:
            if self.check_token(token):
                return token

        return self.create_token()

    def create_token(self):
        #Create bot token
        try:
            if config.os_type == "Windows":
                driver = webdriver.PhantomJS(executable_path='C:/Program Files (x86)/phantomjs/bin/phantomjs.exe',
                                             service_args=config.service_args,
                                             desired_capabilities=config.dcap)

            else:
                driver = webdriver.PhantomJS(service_args=config.service_args,
                                             desired_capabilities=config.dcap)

        except AttributeError:
            print("Problem with phantomJS, possible path is missed")
            return None

        driver.get(config.vk_token_url)

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
            Keys.set_vk_token(bot_login=self.bot_email, token=token)
        except:
            print("Problem with token page, something is missed")
            return

        return token

    def set_group_info(self, group_id):
        group_info = Groups.get_group_info(group_id=group_id)
        if not group_info:
            Groups.set_group_info(group_id=group_id)
            group_info = Groups.get_group_info(group_id=group_id)

        #do smth with users
        #update Groups - user_id, offset, total_users
        Groups.update_group_info(group_id=group_info.group_id,
                                 offset=group_info.offset + 1000,
                                 total_users=0) #TODO add data from json

    @staticmethod
    def get_profile_photo_link(user_id):
        html_source = requests.get(config.vk_profile_link + str(user_id)).text
        html = BeautifulSoup(html_source, 'html.parser')

        try:
            photo_link_raw = html.find('div', class_='owner_panel profile_panel').find('a')['href'].split('?') #Find url of profile pic and return it.
            photo_link = photo_link_raw[0].replace('/photo', "")
            print('Getting profile photo link for user:{0}'.format(user_id))
            return photo_link
        except TypeError:
            print('Profile_photo_link parsing error| user_id: {0}'.format(user_id))
            return None

    def parse_group_members(self, group_id):

        group_info = Groups.get_group_info(group_id=group_id)
        url_params = 'group_id={id}&sort=id_desc&&fields=sex,last_seen&offset={offset}&count=1000'.format(
            id=group_id, offset=group_info.offset
        )
        url = config.vk_group_members_api + url_params
        r = requests.get(url)
        group_data = json.loads(r.text)
        members_list_unsorted = group_data["response"]["users"]
        group_members_total = group_data["response"]["count"]
        vk_id_list = self._check_group_members(member_list_unsorted=members_list_unsorted)
        members_list = []
        for vk_id in vk_id_list:
            user = User(vk_id=vk_id, vk_group_id=group_id)
            members_list.append(user)
        Users.save_users(members_list)



    def _check_group_members(self, member_list_unsorted):
        vk_id_list = []
        month_ago = datetime.datetime.now().timestamp() - 2592000 # 2592000 - One month in seconds, average
        for member in member_list_unsorted:
            member_sex = member["sex"]
            member_last_seen = member["last_seen"]["time"]
            if member_sex == config.vk_male_sex and member_last_seen > month_ago:
                vk_id_list.append(member["uid"])
        return vk_id_list



    def autolikes_start(self):
        #Get user_list from Database

        user_id_list = [6256891, 355428889, 18393105]
        for user in user_id_list:
            photo_link = VK.get_profile_photo_link(user)
            if not photo_link:
                continue #next user_id if no photo_link
            self.set_like(photo_link=photo_link, content_type= 'photo')
            time.sleep(2)

    def set_like(self, photo_link, content_type):
        photo_link = photo_link.split('_')
        owner_id = photo_link[0]
        item_id = photo_link[1]
        print(self.bot_token)
        url = config.vk_like_api + 'type={t}&owner_id={o}&item_id{i}&access_key={k}'.format(
            t=content_type, o=owner_id, i=item_id, k=self.bot_token)
        r = requests.get(url)
        print(r.text)
        print('Liked: vk.com/{0}'.format(photo_link))
        #TODO add url handler
