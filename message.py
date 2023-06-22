import time
import vk_api
from vk_api.longpoll import VkEventType
from vk_api.utils import get_random_id

LONGPOLL_TIMEOUT = 5


class VkMessenger():
    """Класс для отправки сообщений через VK Long Poll API"""

    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)

    def message_send(self, user_id, message, attachment=None, keyboard=None):
        self.vk.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id(),
            'keyboard': keyboard,
        })

    def wait_for_message(self, user_id):
        start_time = time.time()
        while time.time() - start_time < LONGPOLL_TIMEOUT:
            longpoll_server_url = self.get_longpoll_server_url()
            messages = self.get_new_messages(longpoll_server_url, LONGPOLL_TIMEOUT)
            for event in messages['updates']:
                if isinstance(event, VkEventType) and event.type == 'message_new' and event.user_id == user_id:
                    message_event = {
                        'type': 'message_new',
                        'object': {
                            'user_id': event.user_id,
                            'text': event.text
                        }
                    }
                    return message_event

    def get_longpoll_server_url(self):
        response = self.vk.method('messages.getLongPollServer', {})
        return f"https://{response['server']}?act=a_check&key={response['key']}&ts={response['ts']}&wait={LONGPOLL_TIMEOUT}"

    def get_new_messages(self, longpoll_server_url, timeout):
        response = self.vk.http.get(longpoll_server_url, timeout=timeout)
        return response.json()
