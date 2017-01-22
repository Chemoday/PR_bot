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
        expire_dt = datetime.datetime.now().timestamp() + 86400 #86400 - one day token
        try:
            row = Keys.get(Keys.bot_login == bot_login)
            print("Auth key got succesfully")
        except peewee.DoesNotExist:
            row = None

        if row:
            try:
                q = Keys.update(vk_token=token,
                                vk_token_expire_dt=expire_dt).where(Keys.bot_login == bot_login)
                q.execute()
                print("Key was updated successfully")
                return
            except:
                print("Error on updating key")
                return
        else:
            try:
                row = Keys(bot_login=bot_login, vk_token=token,
                           vk_token_expire_dt=expire_dt)
                row.save(force_insert=False)
                print("Token saved")
                return
            except peewee.IntegrityError:
                row = None
                print("Error on save new user")
class Groups(BaseModel):
    group_id = peewee.IntegerField(primary_key=True, unique=True)
    offset = peewee.IntegerField(default=0)
    total_users = peewee.IntegerField(default=0)
    useful_users = peewee.IntegerField(default=0)
    fully_parsed = peewee.BooleanField(default=False)
    domain = peewee.TextField(default='VK')

    #TODO add group name

    def __repr__(self):
        output = 'Group id: {0} | Domain:{1}'.format(self.group_id, self.domain)
        return output


    @staticmethod
    def update_group_info(group_id, offset, total_users, useful_users, fully_parsed=False):
        try:
            q = Groups.update(offset=offset, total_users=total_users,
                              useful_users=useful_users, fully_parsed=fully_parsed).where(Groups.group_id == group_id)
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
        #Use only for initialize group info, for non exist groups
        #If group is exist - use update method
        try:
            row = Groups(group_id=group_id)
            row.save(force_insert=True)
            print("Group: {0} is saved".format(group_id))
        except peewee.IntegrityError:
            print("Group id:{0} not saved".format(group_id))


    @staticmethod
    def get_group_list():
        """
        Retrieving all groups from db with ascending order by offset
        :return:
        """
        groups_list = Groups.select().order_by(Groups.offset.asc())
        return groups_list

    @staticmethod
    def get_groups_ids_list():
        groups_ids = []
        groups_data = Groups.select()

        if not groups_data:
            return groups_ids

        for group in groups_data:
            groups_ids.append(group.group_id)
        return groups_ids

class Users(BaseModel):
    vk_user_id = peewee.IntegerField(null=True, default=None, unique=True)
    vk_group_id = peewee.IntegerField(null=True, default=None)
    vk_likes_count = peewee.IntegerField(default=0)
    created_dt = peewee.DateField(default=datetime.datetime.now())

    def __repr__(self):
        output = "vk_id:{0} | vk_group_id:{1} | create_dt : {2}".format(self.vk_user_id, self.vk_group_id,
                                                                        self.created_dt)
        return output

    @staticmethod
    def get_fresh_vk_users():
        #Return oldest users with 0 likes | 100 max
        #Type Users class
        max_users = 100
        users_list = Users.select().where((Users.vk_user_id is not None) & (Users.vk_likes_count == 0)).order_by(
            Users.created_dt.asc()).limit(max_users)
        return users_list


    @staticmethod
    def save_users(members_list):
        #TODO save for various networks
        #Add for bunch save if needed
        for user in members_list:
            try:
                print(user)
                row = Users(vk_user_id=user.vk_id, vk_group_id=user.vk_group_id)
                row.save()
            except peewee.IntegrityError:
                print("Error on save {0}".format(user))
                print("Possible is argument not unique or alredy exist in db")


    @staticmethod
    def update_likes_count(user_id, domain="vk"):
        try:
            q = Users.update(vk_likes_count=Users.vk_likes_count + 1).where(Users.vk_user_id == user_id)
            q.execute()
        except:
            print("Error on updating likes| Uid = {0}".format(user_id))


class Statistics(BaseModel):
    vk_likes_success = peewee.IntegerField(default=0)
    vk_likes_fails = peewee.IntegerField(default=0)

    @staticmethod
    def update_likes_vk(status):
        #status='success'
        #q = Groups.update(offset=offset, total_users=total_users,
        #                      useful_users=useful_users, fully_parsed=fully_parsed).where(Groups.group_id == group_id)
        try:
            if status == 'success':
                q = Statistics.update(vk_likes_success=Statistics.vk_likes_success + 1).where(
                    Statistics.id == 1)
                q.execute()
            else:
                q = Statistics.update(vk_likes_fails=Statistics.vk_likes_fails + 1).where(
                    Statistics.id == 1)
                q.execute()
        except peewee.IntegrityError:
            print("Error on updating Statistics | likes_vk")



def create_db():
    if not Keys.table_exists():
        Keys.create_table()
        print("Keys table is created")

    if not Groups.table_exists():
        Groups.create_table()
        print("Groups table is created")

    if not Users.table_exists():
        Users.create_table()
        print("Users table is created")

    if not Statistics.table_exists():
        Statistics.create_table()
        Statistics().save()
        print("Statistics table was created")

