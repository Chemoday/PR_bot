import datetime
import peewee

db = peewee.SqliteDatabase('main.db')
db.connect()

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Keys(BaseModel):
    bot_login = peewee.TextField(default="")
    vk_token = peewee.TextField(default="", null=True)
    vk_token_expire_dt = peewee.IntegerField(null=True)

class Auth_module(object):
    def get_vk_token(self, bot_login):
        try:
            keys = Keys.get(Keys.bot_login == bot_login)
            return keys
        except Keys.DoesNotExist:
            print('Error no key in db')
            return None
    @staticmethod
    def set_vk_token(bot_login, token):
        expire_dt = datetime.datetime.now().timestamp() + 86400
        try:
            row = Keys.get(Keys.bot_login == bot_login)
            print("Auth key got succesfully")
        except:
            try:

                row = Keys(bot_login=bot_login, vk_token=token,
                           vk_token_expire_dt=expire_dt)
                row.save(force_insert=False)
                print("Token saved")
                return
            except peewee.IntegrityError:
                row = None
                print("Error on save new user")

        if not row:
            try:
                q = Keys.update(vk_token=token,
                                vk_token_expire_dt=expire_dt).where(Keys.bot_login == bot_login)
                q.execute()
                print("Key was updated successfully")
                return
            except:
                return








def create_db():
    if not Keys.table_exists():
        Keys.create_table()



