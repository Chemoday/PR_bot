import config
from VK import VK
from Database import create_db
from Utils import detect_system



def start_bot():
    detect_system()
    create_db()
    vk = VK(email=config.vk_login,
            password=config.vk_password)
    vk.create_token()


start_bot()