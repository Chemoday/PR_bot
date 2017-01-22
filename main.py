import config
from VK import VK
import Database
from Utils import detect_system, vk_groups_to_parse
import time


def start_bot():
    detect_system()
    Database.create_db()
    vk = VK(email=config.vk_login,
            password=config.vk_password)
    vk.check_for_new_groups_ids()
    vk.parse_groups()
    vk.autolikes_start()


start_bot()