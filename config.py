from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



os_type = "Windows"


#vk config
vk_login = 'aleksandr.kuhhar@gmail.com'
vk_password = '######################'
vk_profile_link = 'http://vk.com/id'
vk_like_api = 'https://api.vk.com/method/likes.add?'
vk_token_url = "http://api.vkontakte.ru/oauth/authorize?client_id=4984258" \
               "&scope=wall&redirect_uri=http://api.vk.com/blank.html" \
               "&display=page&response_type=token"

#PhantomJS config
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
)

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent
service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any','--load-images=no']
