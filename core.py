from datetime import datetime

import vk_api

from config import acces_token


class VkTools():
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):
        try:
            info = self.api.method('users.get', {'user_id': user_id, 'fields': 'city,bdate,sex,relation,home_town'})
        except vk_api.ApiError as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return None

        info = info[0]
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['city']['id'] if 'city' in info else None
                     }

        print(f"user_info: {user_info}")

        if not user_info['bdate']:
            user_info['bdate'] = input("Введите год рождения: ")

        if not user_info['sex']:
            user_info['sex'] = int(input("Введите пол (1 - женский, 2 - мужской): "))

        if not user_info['city']:
            user_info['city'] = int(input("Введите город: "))

        return user_info

    def serch_users(self, params):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': 0,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(69616967)
    users = bot.serch_users(params)
    print(bot.get_photos(users[2]['id']))