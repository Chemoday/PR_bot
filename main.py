import config
from VK import VK
from Database import create_db


create_db()
vk = VK(email= config.vk_login,
        password= config.vk_password)
vk.create_token()
