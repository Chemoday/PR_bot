import config
from VK import VK
from FB import FB
import Database
from Utils import detect_system, vk_groups_to_parse
import time


def start_VK_bot():
    detect_system()
    Database.create_db()
    vk = VK(email=config.vk_login)
    vk.check_for_new_groups_ids()
    vk.parse_groups()
    vk.autolikes_start()



def start_FB_bot():
    detect_system()
    Database.create_db()
    fb = FB(email='spotlight.test2@gmail.com')
    fb.parse_group_members(fb_group_id='1852514221682645')

start_FB_bot()