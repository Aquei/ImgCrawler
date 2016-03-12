import json
import os.path
import termcolor
import colorama
import pprint
import requests
import time
from urllib.parse import urlparse
import sys
from decimal import Decimal
import math
import pathlib

#colorma init
colorama.init()

def default_config_path(filename='config.json'):
    """デフォルトとなる設定ファイルのパスを返す"""
    abspath = os.path.abspath(__file__)
    return os.path.abspath(os.path.dirname(abspath) + '/' + filename)







def txt2tuple(text_list):
    data = []
    for line in text_list:
        line2 = line.strip()
        if not '#' in line2:
            data.append(line2)

    return tuple(data)


def load_file_fallback(path, is_bytes = False):
    """もしパスが見つからない場合は.exampleも探す"""

    if is_bytes:
        mode = 'rb'
    else:
        mode = 'r'

    p = pathlib.Path(path)

    if not p.is_file():
        p = p.with_suffix('.example')

        if not p.is_file():
            raise ValueError('cant read file')

    
    with open(str(p), mode, encoding='utf-8') as f:
        return list(f)
        



def load_config(path=default_config_path()):
    """設定ファイルを読み込む"""

    json_s = load_file_fallback(path)


    config = json.loads(''.join(str(x) for x in json_s))
    colored_text = highlighted(path, 'success')
    print('設定ファイルを読み込みました', colored_text)
        
    pp = pprint.PrettyPrinter()
    pp.pprint(config['config'])

    return config


def save_config(data, path=default_config_path()):
    """設定ファイルにデータを保存する"""

    #falseyな値が渡されたらエラーを投げる
    if not data:
        raise ValueError('no Data to save')

    #jsonとして保存
    with open(path, 'w') as f:
        json.dump(data, f)
    
    msg = '設定ファイルに保存しました ' + highlighted(path, 'success')
    print(msg)


def highlighted(text, preset='danger'):
    """文字列に色を与える"""

    color_preset = {
            'success': {
                'color': 'white',
                'background_color': 'on_blue'
            },
            'danger': {
                'color': 'white',
                'background_color': 'on_red'
            },
            'warn': {
                'color': 'white',
                'background_color': 'on_yellow'
            },
            'info': {
                'color': 'white',
                'background_color': 'on_green'
            }
    }

    if not preset in color_preset:
        preset = 'info'
        msg = highlighted('指定されたプリセットが存在しないので', 'danger') + highlighted('info','info') + highlighted('にプリセットをセットしました', 'danger')
        print(msg)
    
    return termcolor.colored(text, color_preset[preset]['color'], color_preset[preset]['background_color'])


def file_get(url, params={}, headers={}):
    """HTTP GETのラッパー"""

    if not 'user-agent' in headers:
        headers['user-agent'] = 'ImgCrawler/1.0.0'

    print("ダウンロード開始:", highlighted(url, 'info'))

    #リクエスト開始時間
    start = time.time()
    try:
        req = requests.get(url, params=params, headers=headers)
    except ConnectionError as e:
        #接続に関するエラー
        parsed = urlparse(url)
        msg = highlighted(parsed["netloc"], 'info')
        msg += highlighted('との接続でエラーが発生しました', 'danger')
        print(msg, file=sys.stderr)

        return None

    except:
        msg = highlighted(url, 'info')
        msg += highlighted('のリクエストでエラーが発生しました', 'danger')
        msg += ' おそらくスキップされます…'
        print(msg, file=sys.stderr)

        return None

    if req.status_code == requests.codes.ok:
        #問題なし
        end = time.time()
        msg = []
        msg.append(req.headers.get('content-type'))
        msg.append(bytes_size_str(req.content))
        msg.append(quantize(end - start, 2) + '秒')

        if req.url != url:
            msg.append('url: ' + req.url)

        #情報をログに残しておく
        print(highlighted('ダウンロード完了', 'success') + '(' + ' '.join(msg) + ')')

    else:
        return False

    return req



def bytes_size_str(bytes_):
    d = 'kmgt'
    size = len(bytes_)

    for i, s in enumerate(d):
        q = 1024**(i+1)
        q2 = 1024**(i+2)

        if size >= q and q2 < size:
            return quantize(size / q, 2) + (s + 'b').upper()

    return str(size) + 'B'






def quantize(num, digit=2):

    d = '1'*int(digit)

    return str(Decimal(num).quantize(Decimal('.' + d)))


def epoch2time(epoch):
    """エポックを9 tupleにする"""
    return time.localtime(epoch)


def epoch_now():
    """エポックからの秒数を返す（整数)"""
    return math.floor(time.time())
        


if __name__ == '__main__':
    config = load_config()
    save_config(config)
