import requests
import json
from Crypto.Cipher import AES
import base64
import binascii
import os


class Cracker:
    def __init__(self):
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e41762\
9ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97\
ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'
        self.pubKey = '010001'

    def encrypted_request(self, text):
        text = json.dumps(text)
        sec_key = self.create_secret_key(16)
        enc_text = self.aes_encrypt(self.aes_encrypt(text, self.nonce), sec_key.decode('utf-8'))
        enc_sec_key = self.rsa_encrypt(sec_key, self.pubKey, self.modulus)
        data = {'params': enc_text, 'encSecKey': enc_sec_key}
        return data

    @staticmethod
    def aes_encrypt(text, sec_key):
        pad = 16 - len(text) % 16
        text = text + chr(pad) * pad
        encryptor = AES.new(sec_key.encode('utf-8'), AES.MODE_CBC, b'0102030405060708')
        cipher_text = encryptor.encrypt(text.encode('utf-8'))
        cipher_text = base64.b64encode(cipher_text).decode('utf-8')
        return cipher_text

    @staticmethod
    def rsa_encrypt(text, public_key, p_modulus):
        text = text[::-1]
        rs = pow(int(binascii.hexlify(text), 16), int(public_key, 16), int(p_modulus, 16))
        return format(rs, 'x').zfill(256)

    @staticmethod
    def create_secret_key(size):
        return binascii.hexlify(os.urandom(size))[:16]


class WangYiYun:
    def __init__(self, keyword, search_num=5):
        super(WangYiYun, self).__init__()
        self.keyword = keyword
        self.search_num = search_num
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/65.0.3325.32 Safari/537.36'
        }
        self.search_url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        self.player_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        self.cracker = Cracker()
        self.search_session = requests.Session()
        self.search_session.headers.update(self.headers)

    def post_request(self, url, params):
        data = self.cracker.encrypted_request(params)
        response = self.search_session.post(url, data=data, timeout=30)
        result = response.json()
        if result['code'] != 200:
            print('Return {} when try to post {} => {}'.format(result, params, url))
        else:
            return result

    def get_song_url(self, song_id, bit_rate=320000):
        csrf = ''
        params = {'ids': [song_id], 'br': bit_rate, 'csrf_token': csrf}
        result = self.post_request(self.player_url, params)
        song_url = result['data'][0]['url']
        return song_url

    def search_by_keyword(self, search_type=1):
        params1 = {
            's': self.keyword,
            'type': search_type,
            'offset': 0,
            'sub': 'false',
            'limit': self.search_num
        }
        res = self.post_request(self.search_url, params1)
        song_list = []
        if res is not None:
            if res['result']['songCount'] < 1:
                return song_list
            else:
                songs = res['result']['songs']
                for song in songs:
                    song_dic = {'mid': song['id'],
                                'name': song['name'],
                                'album': song['al']['name'],
                                'singer': song['ar'][0]['name'],
                                'extension': '.mp3'
                                }

                    song_id = song['id']
                    song_download_url = self.get_song_url(song_id)
                    song_dic['url'] = song_download_url
                    song_list.append(song_dic)
                return song_list
        else:
            return song_list


if __name__ == '__main__':
    wangyiyun = WangYiYun('张国荣', search_num=10)
    for music in wangyiyun.search_by_keyword():
        print(music)
