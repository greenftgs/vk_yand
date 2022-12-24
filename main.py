import json
import requests
import time

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


access_token = '3af827103af827103a....'
user_id = '493676177'
vk = VK(access_token, user_id)
print(vk.users_info())

token_vk = access_token
start_time = time.time()


def take_token():
    with open('../../Desktop/toke.txt', 'r') as file:
        return file.readline()


vk_api_token = ""
yandex_api_token = take_token()
vk_id = '493676177'
progressBar = [1, 2, 3, 4, 5, 6, 7, 8]


class PhotoUpload:
    def __init__(self, yandex_token: str, vk_token: str, vkId: str):
        self.version_vk = '5.52'
        self.yandex_token = yandex_token
        self.vk_token = vk_token
        self.vkId = vkId
        self.dir_path = ''

    def getUserInfo(self):
        resp = requests.get('https://api.vk.com/method/users.get',
                            params={'access_token': self.vk_token, 'user_id': self.vkId, 'v': self.version_vk})
        return resp.json()

    def getUserPhotos(self):
        resp = requests.get('https://api.vk.com/method/photos.get',
                            params={'access_token': self.vk_token, 'user_id': self.vkId, 'extended': 1,
                                    'album_id': 'profile', 'v': self.version_vk, 'photo_sizes': 1})
        print("Получение фотографий --- %s seconds ---" % (time.time() - start_time))
        resp = resp.json()
        result = resp['response']
        return result

    def sortUserPhotos(self, photos):
        sorted_photos = []
        if 'items' in photos:
            for elements in photos['items']:
                el = {'height': 0, 'width': 0}
                for photo in elements['sizes']:
                    if el['height'] * el['width'] < photo['height'] * photo['width']:
                        el = photo
                        el['name'] = elements['likes']['count']
                sorted_photos.append(el)
        sorted_photos = sorted(sorted_photos, key=lambda k: k['width'] * k['height'], reverse=True)
        print("Сортировка фотографий --- %s seconds ---" % (time.time() - start_time))
        return sorted_photos

    def createYandexDir(self):
        if len(self.dir_path) > 0:
            resp = requests.put('https://cloud-api.yandex.net/v1/disk/resources/',
                                params={'path': self.dir_path},
                                headers={'Authorization': f'OAuth {self.yandex_token}'})
            return resp.json()
        else:
            return 'Не указан путь'

    def uploadYandex(self, file_path: str, photos, count=5):
        result = []
        for photo in zip(range(count), photos):

            resp = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                 params={'path': self.dir_path + str(photo[1]['name']),
                                         'url': photo[1]['src']},
                                 headers={'Authorization': f'OAuth {self.yandex_token}'})
            if 'href' in resp.json():
                result.append({"file_name": photo[1]['name'], "size": photo[1]['type']})
            print("Загрузка фотографии "+str(photo[1]['name'])+" --- %s seconds ---" % (time.time() - start_time))
        return result

    def createJsonFile(self, data):
        f = open('result.json', 'w', encoding="utf-8")
        print("Созадние json файла --- %s seconds ---" % (time.time() - start_time))
        json.dump(data, f)

photoUploader = PhotoUpload(yandex_api_token, vk_api_token, vk_id)
photos = photoUploader.getUserPhotos()
photos = photoUploader.sortUserPhotos(photos)
photoUploader.dir_path = '/124/'
photoUploader.createYandexDir()
jsonPhotos = photoUploader.uploadYandex(photoUploader.dir_path, photos, 2)
photoUploader.createJsonFile(jsonPhotos)