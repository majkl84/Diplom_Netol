import vk_api
from vk_api import VkApi
from vk_api.exceptions import ApiError
from pprint import pprint
from datetime import datetime
from vk_api.longpoll import VkLongPoll
from config import access_token, comunity_token



class VkTools:
    def __init__(self, access_token):
        self.vk = VkApi(token=access_token)
        self.longpoll = VkLongPoll(self.vk, wait=20)
        self.vkapi = VkApi(token=access_token)


    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id):
        try:
            info, = self.vkapi.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,sex,relation,bdate'
                                       }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
        'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': self._bdate_toyear(info.get('bdate')),
                  'relation': info.get('relation')
                  }
        result = self.ask_user(user_id, result)  # передаем user_id в метод ask_user
        return result

    def ask_user(self, user_id, result):
        if 'city' not in result or not result['city']:
            self.messenger.message_send(user_id, 'Введите город:')
            city = self.messenger.wait_for_message(user_id)
            print(city)  # временный print-оператор
            if city:
                result['city'] = city['text']

        if 'sex' not in result or not result['sex']:
            self.messenger.message_send(user_id, 'Введите пол (1 - женский, 2 - мужской):')
            sex = self.messenger.wait_for_message(user_id)
            print(sex)  # временный print-оператор
            if sex:
                result['sex'] = int(sex['text'])

        if 'year' not in result or not result['year']:
            self.messenger.message_send(user_id, 'Введите дату рождения в формате ДД.ММ.ГГГГ:')
            bdate = self.messenger.wait_for_message(user_id)
            print(bdate)  # временный print-оператор
            if bdate:
                result['year'] = self._bdate_toyear(bdate['text'])
        return result

    def search_worksheet(self, params, offset):
        try:
            users = self.vkapi.method('users.search',
                                      {
                                          'count': 50,
                                          'offset': offset,
                                          'hometown': params['city'],
                                          'sex': 1 if params['sex'] == 2 else 2,
                                          'has_photo': True,
                                          'age_from': params['year'] - 3,
                                          'age_to': params['year'] + 1,
                                          'relation': [1, 6],
                                      }
                                      )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                   'id': item['id']
                   } for item in users['items'] if item['is_closed'] is False
                  ]
        return result

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]
        result = sorted(result, key=lambda x: x['likes'], reverse=True)
        return result[:3]


if __name__ == '__main__':
    user_id = 69616967
    tools = VkTools(access_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 20)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])

    pprint(worksheets)
