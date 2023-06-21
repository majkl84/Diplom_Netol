import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from config import comunity_token, access_token
from core import VkTools
import data
from data import delete_worksheets_in_db
from message import VkMessenger

engine = create_engine("sqlite:///db.sqlite")
Session = sessionmaker(bind=engine)


class BotInterface():
    def __init__(self, comunity_token, access_token):
        self.messenger = VkMessenger(comunity_token)
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0



    # добавление записи в базу данных
    def add_worksheet_to_db(self, profile_id, worksheet_id):
        data.add_user(profile_id, worksheet_id)

    # проверка наличия анкеты в базе данных
    def check_worksheet_in_db(self, profile_id, worksheet_id):
        result = data.check_user(profile_id, worksheet_id)
        return result

    # удаление записей из базы данных для заданного профиля
    def delete_user_worksheets_in_db(self, profile_id):
        delete_worksheets_in_db(profile_id)

    # создание клавиатуры с двумя кнопками: "Поиск" и "Очистка"
    def create_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Очистка БД', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    # обработка событий / получение сообщений
    def event_handler(self):
        keyboard = self.create_keyboard()  # создаем клавиатуру
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.messenger.message_send(
                        event.user_id, f'Привет друг, {self.params["name"]}',
                        keyboard=keyboard)  # добавлен аргумент keyboard
                elif event.text.lower() == 'поиск':
                    '''Логика для поиска анкет'''
                    self.messenger.message_send(event.user_id, 'Начинаем поиск', keyboard=keyboard)  # добавлен аргумент keyboard
                    if not self.worksheets:
                        self.offset = 0
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                    while self.worksheets:
                        worksheet = self.worksheets.pop()
                        worksheet_id = worksheet["id"]
                        profile_id = event.user_id

                        # проверка анкеты в базе данных
                        if self.check_worksheet_in_db(profile_id, worksheet_id):
                            print(f'Анкета {worksheet_id} уже просмотрена пользователем {profile_id}')
                            continue  # перейти к следующей анкете, если текущая анкета уже есть в базе данных

                        # добавление анкеты в базу данных
                        try:
                            self.add_worksheet_to_db(profile_id, worksheet_id)
                        except IntegrityError:
                            print(
                                f"Ошибка добавления анкеты {worksheet_id} для пользователя {profile_id}: анкета уже есть в базе данных")
                            continue  # перейти к следующей анкете, еслипроизошла ошибка добавления в базу данных
                        else:
                            print(f'Анкета {worksheet_id} добавлена в базу данных для пользователя {profile_id}')
                        photos = self.vk_tools.get_photos(worksheet_id)
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10

                        self.messenger.message_send(
                            event.user_id,
                            f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                            attachment=photo_string,
                            keyboard=keyboard,  # добавлен аргумент keyboard
                        )
                        break  # выйти из цикла while и закончить поиск анкет, если найдена анкета, которой нет в базе данных
                    else:
                        self.messenger.message_send(
                            event.user_id, 'Нет больше анкет', keyboard=keyboard)
                elif event.text.lower() == 'очистка':
                    '''Логика для очистки базы данных'''
                    self.delete_user_worksheets_in_db(event.user_id)
                    self.messenger.message_send(
                        event.user_id, 'База данных очищена', keyboard=keyboard)
                elif event.text.lower() == 'пока':
                    self.messenger.message_send(
                        event.user_id, 'До новых встреч', keyboard=keyboard)
                else:
                    self.messenger.message_send(
                        event.user_id, 'Неизвестная команда', keyboard=keyboard)


if __name__ == '__main__':
    data.Base.metadata.create_all(engine)
    bot_interface = BotInterface(comunity_token, access_token)
    bot_interface.event_handler()
