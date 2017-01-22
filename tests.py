import time
import config
from VK import VK
from Database import Groups, Users, create_db


def delete_group_and_ids():
    Groups.delete().execute()
    Users.delete().execute()

def start_bot():
    create_db()
    vk = VK(email=config.vk_login,
            password=config.vk_password)
    delete_group_and_ids()
    vk.check_for_new_groups_ids()
    vk.parse_groups()
    vk.autolikes_start()


start_bot()


