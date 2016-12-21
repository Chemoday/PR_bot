import platform
import config


def detect_system():
    platform_type = platform.system()
    if platform_type == 'Windows':
        config.system_type = platform_type
    else:
        config.system_type = 'Linux'
