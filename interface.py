from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class BotInterface:
    def __init__(self, comunity_token, acces_token):
        self.interface = VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.current_user_index = 0  # номер текущей анкеты для поиска

    def message_send(self, user_id, message, keyboard=None, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'keyboard': keyboard,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               })

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        while True:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    command = event.text.lower()

                    if command == 'привет':
                        self.params = self.api.get_profile_info(event.user_id)
                        keyboard = VkKeyboard(one_time=True)  # создаем клавиатуру, которая будет скрыта после использования
                        keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
                        self.message_send(event.user_id, f'Здравствуй, {self.params["name"]}! Что вы хотите сделать?', keyboard=keyboard.get_keyboard())
                    elif command == 'поиск':
                        users = self.api.serch_users(self.params)

                        if self.current_user_index >= len(users):
                            self.current_user_index = 0  # если все анкеты просмотрены, начинаем заново

                        user = users[self.current_user_index]
                        self.current_user_index += 1  # увеличиваем номер текущей анкеты

                        photos_user = self.api.get_photos(user['id'])

                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break
                        keyboard = VkKeyboard(one_time=True)  # создаем клавиатуру, которая будет скрыта после использования
                        keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
                        self.message_send(event.user_id,
                                          f'Встречайте {user["name"]}',
                                          attachment=attachment,
                                          keyboard=keyboard.get_keyboard())
                    elif command == 'дальше':
                        users = self.api.serch_users(self.params)

                        if self.current_user_index >= len(users):
                            self.current_user_index = 0  # если все анкеты просмотрены, начинаем заново

                        user = users[self.current_user_index]
                        self.current_user_index += 1  # увеличиваем номер текущей анкеты

                        photos_user = self.api.get_photos(user['id'])

                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break
                        keyboard = VkKeyboard(one_time=True)  # создаем клавиатуру, которая будет скрыта после использования
                        keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
                        self.message_send(event.user_id,
                                          f'Встречайте {user["name"]}',
                                          attachment=attachment,
                                          keyboard=keyboard.get_keyboard())
                    elif command == 'пока':
                        self.message_send(event.user_id, 'Пока!')
                    else:
                        keyboard = VkKeyboard(one_time=True)  # создаем клавиатуру, которая будет скрыта после использования
                        keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()