import time
import vk_api
from vk_api.utils import get_random_id


class VkMessenger():
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

    def wait_for_message(self, user_id, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.vk.method('messages.getLongPollServer', {})
            server, key, ts = response['server'], response['key'], response['ts']
            lp_response = self._get_longpoll_messages(server, key, ts, timeout)
            for event in lp_response['updates']:
                if isinstance(event, dict) and event.get('type') == 'message_new' and event['object'].get(
                        'user_id') == user_id:
                    print(
                        f"Received message '{event['object']['text']}' from user {user_id}")  # временный print-оператор
                    return event['object']
            print(f"No message received from user {user_id}")  # временный print-оператор
        return None

    def _get_longpoll_messages(self, server, key, ts, timeout):
        url = f"https://{server}?act=a_check&key={key}&ts={ts}&wait={timeout}"
        response = self.vk.http.get(url)
        return response.json()