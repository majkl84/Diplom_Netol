import vk

class VKChat:
    def __init__(self, access_token, peer_id):
        self.session = vk.Session(access_token=access_token)
        self.api = vk.API(self.session)
        self.peer_id = peer_id

    def send_message(self, message):
        self.api.messages.send(
            peer_id=self.peer_id,
            message=message
        )

    def send_photo(self, photo_url):
        upload_url = self.api.photos.getMessagesUploadServer(peer_id=self.peer_id)['upload_url']
        photo_data = self.api.http.get(photo_url).content
        response = self.api.http.post(upload_url, files={'photo': ('photo.png', photo_data)})
        photo_info = self.api.photos.saveMessagesPhoto(**response.json())[0]
        attachment = f'photo{photo_info["owner_id"]}_{photo_info["id"]}'
        self.api.messages.send(
            peer_id=self.peer_id,
            attachment=attachment
        )