import config
from VK import VK



vk = VK(email=config.vk_login,
            password=config.vk_password)

photo_link = '83292389_409785938'
print(vk.bot_token)
vk.set_like(photo_link=photo_link)
