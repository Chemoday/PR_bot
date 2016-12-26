import config
from VK import VK
import Database
from Utils import detect_system



def start_bot():
    detect_system()
    Database.create_db()
    vk = VK(email=config.vk_login,
            password=config.vk_password)
    Database.Groups.set_group_info(config.groups_to_parse)
    vk.parse_group_members(group_id=109991106)


start_bot()