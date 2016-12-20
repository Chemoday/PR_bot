from selenium.webdriver.common.desired_capabilities import DesiredCapabilities






#vk config
vk_login = 'aleksandr.kuhhar@gmail.com'
vk_password = '###############'

#PhantomJS config
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
)

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent
service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any','--load-images=no']
