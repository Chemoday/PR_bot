import platform
import config
import VK

def detect_system():
    platform_type = platform.system()
    if platform_type == 'Windows':
        config.os_type = platform_type
    else:
        config.os_type = 'Linux'

vk_groups_to_parse = [109991106]
