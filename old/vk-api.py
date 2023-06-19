import vk

class VKAPI:
    def __init__(self, access_token):
        self.session = vk.Session(access_token=access_token)
        self.api = vk.API(self.session)

    def get_users(self, city_id, age_from, age_to, sex, status):
        users = self.api.users.search(
            count=1000,
            city=city_id,
            age_from=age_from,
            age_to=age_to,
            sex=sex,
            status=status,
            fields='photo_max,has_photo'
        )
        return users

    def get_user_photos(self, user_id):
        photos = self.api.photos.get(
            owner_id=user_id,
            album_id='profile',
            rev=1,
            extended=1,
            count=3
        )
        return photos


def utils():
    return None


def longpoll():
    return None