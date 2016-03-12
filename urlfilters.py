import utl
import re
from urllib.parse import urlparse, urljoin




def load_blacklist(path=None):
    """ブラックリストをタプルで返す関数を返す"""

    blacklist = []

    def get_blacklist():
        nonlocal blacklist
        if blacklist:
            return blacklist
    
        file_path = path
        if file_path is None:
            file_path = utl.default_config_path('blacklist.txt')


        f = utl.load_file_fallback(file_path)

        blacklist = utl.txt2tuple(f)

        return blacklist
    

    return get_blacklist






def load_ext(path=None):
    ext = []
    def get_ext():
        nonlocal ext
        
        path2 = path
        #二回目以降はキャッシュを返す
        if ext:
            return ext

        if path is None:
            path2  = utl.default_config_path('ext.txt')

        ext_list = []

        f = utl.load_file_fallback(path2)
        ext = utl.txt2tuple(f)

        return ext

    return get_ext

        


def get_scheme(url):
    scheme = urlparse(url).scheme

    if scheme:
        return scheme


def pre_proc(url):
    """特定のURLパターンでダウンロードするためのURLに変更する"""

    url = url.strip()
    scheme = get_scheme(url)

    #imgurのページ
    result = re.match('^https?://imgur\.com/(?P<imgur_id>[a-zA-Z0-9]+)$', url)
    if result:
        imgur_id = result.group('imgur_id')

        return scheme + '://imgur.com/download/' + imgur_id + '/'

    #imgurのアルバムページ
    result = re.match('^https?://imgur\.com/a/(?P<imgur_id>[a-zA-Z0-9]+)$', url)
    if result:
        imgur_id  = result.group('imgur_id')

        return scheme + '://s.imgur.com/a/' + imgur_id + '/zip'


    #livedoorブログ
    result = re.match('https?://livedoor\.blogimg\.jp/.*/(?P<file_name>[a-z0-9]+)-s\.(?P<ext>.{3,4})$', url)
    if result:
        file_name = result.group('file_name')
        ext = result.group('ext')

        filename = file_name + '.' + ext

        return urljoin(url, filename)


blacklist = load_blacklist()()
ext = load_ext()()


def url_filter(url, blacklist=blacklist, ext=ext):
    url = url.strip()
    scheme = get_scheme(url).lower()

    if not 'http' in scheme:
        print(url, 'is invalid url')
        return

    #ブラックリストチェック
    for black in blacklist:
        if black in url:
            return

    #最初にimgurなどのurlをチェックする
    result = pre_proc(url)
    if result:
        return result
   
    #指定された拡張子で終わるか調べる
    file_path = urlparse(url).path
    if file_path.endswith(ext):
        return url











