# _*_ coding:utf-8 _*_

import requests
import json
import re


class QQMusic:
    def __init__(self, keyword, music_type='M500', search_num=5):
        super(QQMusic, self).__init__()
        self.keyword = keyword
        self.music_type = music_type
        self.search_num = search_num
        self.music_extension = {
            'C400': '.m4a',
            'M500': '.mp3',
            'M800': '.mpe',
            'A000': '.ape',
            'F000': '.flac'
        }  # m4a, mp3普通, mp3高, ape, flac
        self.headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
                    }
        self.search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        self.fcg_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg'
        self.download_url = 'http://dl.stream.qqmusic.qq.com/{}?vkey={}&guid=7133372870&uin=0&fromtag=53'

    def search_by_keyword(self):
        params = {
                 'ct': 24,
                 'qqmusic_ver': 1298,
                 'new_json': 1,
                 'remoteplace': 'txt.yqq.top',
                 't': 0,
                 'aggr': 1,
                 'cr': 1,
                 'catZhida': 1,
                 'lossless': 0,
                 'flag_qc': 0,
                 'p': 1,
                 'n': self.search_num,
                 'w': self.keyword,
                 'g_tk': 5381,
                 'loginUin': 0,
                 'hostUin': 0,
                 'format': 'jsonp',
                 'inCharset': 'utf8',
                 'outCharset': 'utf-8',
                 'notice': 0,
                 'platform': 'yqq',
                 'needNewCode': 0
        }

        res = requests.get(self.search_url, params=params, headers=self.headers).text
        search_result_data = re.match(r'callback.*?({.*})', res).group(1)
        search_result_data_dic = json.loads(search_result_data)
        song_info = search_result_data_dic['data']['song']['list']
        song_list = []
        for song in song_info:
            singer_list = [singer['name'] for singer in song['singer']]
            singer = '/'.join(singer_list)
            song_dic = {'mid': song['mid'],
                        'name': song['name'],
                        'album': song['album']['name'],
                        'singer': singer,
                        'extension': self.music_extension[self.music_type]
                        }
            song_dic['url'] = self.get_download_url(song_dic['mid'])
            song_list.append(song_dic)
        return song_list

    def get_download_url(self, song_mid):
        params = {
            'g_tk': '5381',
            'jsonpCallback': 'MusicJsonCallback8571665793949388',
            'loginUin': '0',
            'hostUin': '0',
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf-8',
            'notice': '0',
            'platform': 'yqq',
            'needNewCode': '0',
            'cid': '205361747',
            'callback': 'MusicJsonCallback8571665793949388',
            'uin': '0',
            'songmid': song_mid,
            'filename': 'C400'+song_mid + '.m4a',
            'guid': '7133372870'
        }
        detail_html = requests.get(self.fcg_url, headers=self.headers, params=params).text
        vkey_disc = re.compile(r'MusicJsonCallback8571665793949388\((.*?)\)').findall(detail_html)[0]
        vkey_disc = json.loads(vkey_disc)

        data = vkey_disc['data']
        items = data.get('items')[0]
        vkey = items.get('vkey')

        file_name = '{}{}{}'.format(self.music_type, song_mid, self.music_extension[self.music_type])
        music_download_url = self.download_url.format(file_name, vkey)
        return music_download_url


if __name__ == '__main__':
    qq = QQMusic('周杰伦', search_num=20)
    for music in qq.search_by_keyword():
        print(music)
