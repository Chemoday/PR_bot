import platform
import config


def detect_system():
    platform_type = platform.system()
    if platform_type == 'Windows':
        config.os_type = platform_type
    else:
        config.os_type = 'Linux'
