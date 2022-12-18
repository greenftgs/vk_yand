import json
import requests
import time
from tqdm import tqdm

class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

access_token = '3af827103af827103af827100139e9caaa33af83af827105966de84b3ba2c00248c5e70'
user_id = '493676177'
vk = VK(access_token, user_id)
print(vk.users_info())

token_vk = access_token

def take_token():
    with open('../../Desktop/toke.txt', 'r') as file:
        return file.readline()

token_yd = take_token()

#
# class YaUploader:
#     files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
#     upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
#
#     def __init__(self, token: str):
#         self.token = token
#
#     @property
#     def headers(self):
#         return {
#             'Content_Type': 'application/json',
#             'Authorization': f'OAuth {self.token}'
#         }
#
#     def get_upload_link(self, file_path: str):
#         params = {'path': file_path, 'overwrite': 'true'}
#         response = requests.get(self.upload_url, params=params, headers=self.headers)
#         return response.json()
#
#     def upload(self, file_path):
#         href = self.get_upload_link(file_path).get('href')
#         if not href:
#             return print(f'Ошибка загрузки: {self.get_upload_link(file_path)["message"]}')
#
#         with open(file_path, 'rb') as file:
#             try:
#                 response = requests.put(href, data=file)
#                 if response.status_code == 201:
#                     print('Загрузка файла проведена успешно')
#             except (FileNotFoundError, Exception, KeyError):
#                 print(f'Ошибка загрузки: , {self.get_upload_link(file_path)["message"]}')
#
#
# ya_client = YaUploader(take_token())
# ya_client.upload('pdf.pdf')


class ApiBasic:
    """Родительский класс с общей функцией отправлять запросы"""
    def _send_request(self, method, path, **kwargs):
        if method == 'get':
            response = requests.get(url=path, **kwargs).json()
        elif method == 'post':
            response = requests.post(url=path, **kwargs).json()
        elif method == 'put':
            response = requests.put(url=path, **kwargs).json()
        return response


class VkUser(ApiBasic):
    url = 'https://api.vk.com/method/'

    def __init__(self, token):
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    # Получаем информацию о пользователе
    def get_info(self, user_id):
        info_url = self.url + 'users.get'
        info_params = {
            'user_id': user_id,
        }
        res = self._send_request('get', info_url, params={**self.params, **info_params})
        return res

    # Получаем словарь фотографий,где
    # ключ - порядковый номер
    # значения - ссылка, количество лайков, размер, дата, имя фотографии (количество лайков с датой при необходимости)
    def get_photo(self, user_id):
        photo_url = self.url + 'photos.get'
        photo_params = {
            'extended': 1,
            'photo_sizes': 1,
            'album_id': 'profile',
            'owner_id': user_id
        }
        res = self._send_request('get', photo_url, params={**self.params, **photo_params})
        info_about_photo = {}
        id = 0
        all_likes = []
        for item in res['response']['items']:
            likes = item['likes']['count']
            all_likes.append(likes)
        for item in res['response']['items']:
            id += 1
            likes = item['likes']['count']
            photo = item['sizes'][-1]['url']
            date = item['date']
            for sizes in item['sizes']:
                size = sizes['type']
                info_about_photo[id] = [photo, likes, size, date]
        id = 0
        for like in all_likes:
            id += 1
            if all_likes.count(like) == 1:
                photo_name = like
                info_about_photo[id].append(photo_name)
            else:
                photo_name = f'{like}_{info_about_photo.get(id)[3]}'
                info_about_photo[id].append(photo_name)
        return info_about_photo


class YandexUser(ApiBasic):
    host = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    # Создаем папку где будут храниться фотографии
    def get_folder(self, name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        params = {
            'path': name
        }
        res = self._send_request('put', url, params=params, headers=headers)
        return res

    # Загружаем фотографии по ссылке из профиля vk.com в созданную папку
    def download_by_link(self, link, photo_name):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': f"{name}/{photo_name}", 'url': link}
        res = self._send_request('post', upload_url, params=params, headers=headers)
        return res


if __name__ == '__main__':
    id_user_vk = input('Введите ID пользоввателя vk.com: ')
    if id_user_vk.isdigit() is True:
        user = VkUser(token_vk)
        for item in user.get_info(id_user_vk)['response']:
            name = f"Фото профиля vk.com {item['first_name']} {item['last_name']} (id {item['id']})"
            print(name)
        all_photos = user.get_photo(id_user_vk)
        yandex = YandexUser(token_yd)
        yandex.get_folder(name)
        photos_list = []
        for keys, values in tqdm(all_photos.items()):
            yandex.download_by_link(values[0], values[4])
            photo_vk = {'file_name': f"{values[4]}.jpg", 'size': f"{values[2]}"}
            photos_list.append(photo_vk)
            time.sleep(1)
        print(f'{len(all_photos.items())} фотографий успешно загружены на Яндекс.Диск')
        with open('photo_vk.json', 'w') as f:
            json.dump(photos_list, f, ensure_ascii=False, indent=2)
    else:
        print('ID пользователя введен неверно')