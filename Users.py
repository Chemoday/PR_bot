

class User(object):

    def __init__(self, vk_id=None, vk_group_id=None):
        self.vk_id = vk_id
        self.vk_group_id = vk_group_id
        #Add for several networks

    def __repr__(self):
        #Add more args if needed
        output = "VK_ID:{vk_id}| VK_group_id:{vk_group_id}".format(vk_id=self.vk_id,vk_group_id=self.vk_group_id)
        return output
