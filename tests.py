import time
import config
from VK import VK
from Database import Groups, create_db

# create_db()
vk = VK(email=config.vk_login,
            password=config.vk_password)


VK.check_for_new_groups_ids()
group_list = Groups.get_group_list()
for group in group_list:
    vk.parse_group_members(group_id=group.group_id)
    time.sleep(1)