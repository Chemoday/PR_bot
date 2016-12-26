import datetime
import peewee

db = peewee.SqliteDatabase('main.db')
db.connect()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Keys(BaseModel):
    bot_login = peewee.TextField(default="")
    bot_password = peewee.TextField(default="")
    vk_token = peewee.TextField(default="", null=True)
    vk_token_expire_dt = peewee.IntegerField(null=True)

    def __repr__(self):
        output = "{0} | {1} | {2}".format(self.bot_login, self.vk_token, self.vk_token_expire_dt)
        return output

    @staticmethod
    def get_bot_pass(email):
        bot_pass = Keys.get(Keys.bot_login == email)
        return bot_pass.bot_password

    @staticmethod
    def get_vk_token(email):
        try:
            keys = Keys.get(Keys.bot_login == email)
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
                print("Error on updating key")
                return

class Groups(BaseModel):
    group_id = peewee.IntegerField(primary_key=True, unique=True)
    offset = peewee.IntegerField(default=0)
    total_users = peewee.IntegerField(default=0)
    useful_users = peewee.IntegerField(default=0)
    fully_parsed = peewee.BooleanField(default=False)
    #TODO add group name

    def __repr__(self):
        output = 'Group id: {0}'.format(self.group_id)
        return output


    @staticmethod
    def update_group_info(group_id, offset, total_users):
        try:
            q = Groups.update(offset=offset, total_users=total_users).where(Groups.group_id == group_id)
            q.execute()
        except:
            print("Error on updating groups info")


    @staticmethod
    def get_group_info(group_id):
        try:
            group_data = Groups.get(Groups.group_id == group_id)
            return group_data
        except Groups.DoesNotExist:
            return None

    @staticmethod
    def set_group_info(group_id):
        try:
            row = Groups(group_id=group_id)
            row.save(force_insert=True)
            print("Group is saved")
            print(row)
        except peewee.IntegrityError:
            print("Group id:{0} not saved".format(group_id))




def create_db():
    if not Keys.table_exists():
        Keys.create_table()
        print("Keys table is created")

    if not Groups.table_exists():
        Groups.create_table()
        print("Groups table is created")



