import time
import datetime
from selenium import webdriver
from Database import Keys, Groups, Users, Statistics
import requests
from bs4 import BeautifulSoup
import json
import config
from Users import User
import Utils



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
                return token.vk_token

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

        except:
            print("Problem in login and password input screen")
            return

        try:
            #TODO add ip check
            #App permission window is displayed if token requested on new ip address
            submit = driver.find_element_by_class_name("flat_button fl_r button_indent")
            submit.click()
        except:
            print("App permission window is missed")

        try:
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
            print("Problem in parsing token url")
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
            print('Profile_photo_link parsing error | user_id: {0}'.format(user_id))
            return None

    @staticmethod
    def parse_group_members(group_id):
        print("group_id:{0}".format(group_id))
        group_info = Groups.get_group_info(group_id=group_id)
        if (group_info.total_users != 0) & ((group_info.total_users - group_info.offset) < config.vk_parse_amount):
            print("{0} - {1}".format(group_info.total_users, group_info.offset))
            parse_amount = group_info.total_users - group_info.offset
        else:
            parse_amount = 1000
        print("parse amount: ", parse_amount)
        url_params = 'group_id={id}&sort=id_desc&&fields=sex,last_seen&offset={offset}&count={count}'.format(
            id=group_id, offset=group_info.offset, count=parse_amount
        )
        url = config.vk_group_members_api + url_params
        r = requests.get(url)
        group_data = json.loads(r.text)
        members_list_unsorted = group_data["response"]["users"]
        members_total = group_data["response"]["count"]
        vk_id_list = VK._check_group_members(member_list_unsorted=members_list_unsorted)
        members_list = []
        for vk_id in vk_id_list:
            user = User(vk_id=vk_id, vk_group_id=group_id)
            members_list.append(user)
        Users.save_users(members_list)

        offset = group_info.offset + parse_amount
        fully_parsed = False

        if offset >= group_info.total_users:
            offset = group_info.total_users
            fully_parsed = True

        Groups.update_group_info(group_id=group_id, offset=offset,
                                 total_users=members_total, useful_users=group_info.useful_users + len(members_list),
                                 fully_parsed=fully_parsed
                                 )

    @staticmethod
    def parse_groups():
        """
        :return:
         Must be running in parallel process
         to fill Groups table with users
        """
        group_list = Groups.get_group_list()
        for group in group_list:
            print(group)
            VK.parse_group_members(group_id=group.group_id)
            time.sleep(1)

    @staticmethod
    def _check_group_members(member_list_unsorted):
        """
        :param
        :return:
        Checking group members on specific  state
        #Sex, last_seen
        """

        vk_id_list = []
        month_ago = datetime.datetime.now().timestamp() - 2592000 # 2592000 - One month in seconds, average
        for member in member_list_unsorted:
            member_sex = member["sex"]
            member_last_seen = member["last_seen"]["time"]
            if ( member_sex in config.vk_sex_type) and member_last_seen > month_ago:
                vk_id_list.append(member["uid"])
        return vk_id_list



    def autolikes_start(self):
        """
        :return:
        Getting users from db
        Parsing users main photo link
        Set like on main photo
        """
        users_id_list = Users.get_fresh_vk_users()
        print("Got {0} fresh users from server".format(len(users_id_list)))
        for user in users_id_list:
            photo_link = VK.get_profile_photo_link(user.vk_user_id)
            if not photo_link:
                print("User: {0} - VK photo not found".format(user.vk_user_id))
                continue #next user_id if no photo_link
            VK.set_like(photo_link=photo_link, content_type='photo', token=self.bot_token)
            time.sleep(2)

    @staticmethod
    def set_like(photo_link,token, content_type='photo'):
        #TODO change to staticmethod, add token to argument
        photo_link = photo_link.split('_')
        owner_id = photo_link[0]
        item_id = photo_link[1]
        url = config.vk_like_api + 'type={t}&owner_id={o}&item_id={i}&access_token={tk}&v=5.62'.format(
            t=content_type, o=owner_id, i=item_id, tk=token)
        r = requests.get(url)
        response = r.text
        print(response)
        if VK.__check_response_on_errors(response):
            Statistics.update_likes_vk(status='failed')
            return

        print('Liked: vk.com/id{0}'.format(photo_link[0]))
        Users.update_likes_count(user_id=owner_id, domain="vk")
        Statistics.update_likes_vk(status='success')

    @staticmethod
    def __check_response_on_errors(response):
        response = json.loads(response)
        if "error" in response.keys():
            print("Error: {0}".format(response['error']['error_msg']))
            return False
        return True

    @staticmethod
    def check_for_new_groups_ids():
        newly_added = 0
        group_ids = Groups.get_groups_ids_list()
        for group_id in Utils.vk_groups_to_parse:
            if group_id in group_ids:
                continue
            else:
                Groups.set_group_info(group_id=group_id)
                newly_added+=1
        if newly_added > 0:
            print("Added {0} new groups".format(newly_added))
        return
