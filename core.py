import vk_api
from vk_api.exceptions import ApiError
from datetime import datetime
from config import access_token



class VkTools:
    def __init__(self, access_token, interface=None):
        self.vkapi = vk_api.VkApi(token=access_token)
        self.interface = interface
    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id, event=None):
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
        result = self.ask_user(result, user_id, self.interface, event=event)
        return result

    def ask_user(self, result, user_id, interface, event=None, asked_params=[], ask_count=3):
        if not result.get('city') and 'city' not in asked_params:
            interface.message_send(user_id=user_id, message='Введите город:')
            city = interface.wait_for_message(user_id=user_id, event=event)
            if city and city.strip():
                result['city'] = city.strip()
                asked_params.append('city')
            else:
                ask_count -= 1
                if ask_count > 0:
                    return self.ask_user(result, user_id, interface, event=event, asked_params=ask_params,
                                         ask_count=ask_count)

        if not result.get('sex') and 'sex' not in asked_params:
            interface.message_send(user_id=user_id, message='Введите пол (1 - женский, 2 - мужской):')
            sex = interface.wait_for_message(user_id=user_id, event=event)
            if sex and sex.isdigit() and int(sex) in (1, 2):
                result['sex'] = int(sex)
                asked_params.append('sex')
            else:
                ask_count -= 1
                if ask_count > 0:
                    return self.ask_user(result, user_id, interface, event=event, asked_params=ask_params,
                                         ask_count=ask_count)

        if not result.get('year') and 'year' not in asked_params:
            interface.message_send(user_id=user_id, message='Введите дату рождения в формате ДД.ММ.ГГГГ:')
            bdate = interface.wait_for_message(user_id=user_id, event=event)
            if bdate and bdate.strip():
                year = self._bdate_toyear(bdate)
                if year:
                    result['year'] = year
                    asked_params.append('year')
                else:
                    ask_count -= 1
                    if ask_count > 0:
                        return self.ask_user(result, user_id, interface, event=event, asked_params=ask_params,
                                             ask_count=ask_count)
            else:
                ask_count -= 1
                if ask_count > 0:
                    return self.ask_user(result, user_id, interface, event=event, asked_params=ask_params,
                                         ask_count=ask_count)

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
    # interface = BotInterface(access_token)
    tools = VkTools(access_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 20)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])

