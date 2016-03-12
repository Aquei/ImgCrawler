from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from urlfilters import url_filter

class ImgFinder(HTMLParser):
    """img要素,a要素から、それぞれイメージへのリンクや参照のURLを探す"""

    def __init__(self, base=None):
        """コンストラクタ"""
        self._base = base
        self._urls = set()

        #HTMLParserのコンストラクタを呼ぶ
        super(ImgFinder, self).__init__()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._anchor_search(attrs)

        if tag == "img":
            self._img_search(attrs)
    
    def get_urls(self):
        return self._urls

    def _url_add(self, url):
        url_checked = self._check(url)
        if url_checked:
            self._urls.add(url_checked)


    def _is_abs_url(self, url):
        """渡されたURLが絶対URLか判断する"""
        parsed = urlparse(url)
        return parsed.scheme and parsed.netloc

    def _abs_url(self, url):
        """絶対URLにする"""
       
        if not self._is_abs_url(url):
            #相対URL!
            if self._base is not None and self._is_abs_url(self._base):
                return urljoin(self._base, url)
            else:
                raise ValueError("不正なbaseです", self._base, url)

        return url


    def _anchor_search(self, attrs):
        """<a>のhrefを探す"""
        if not len(attrs):
            #なにもしない
            return None
       
        for attr, val in attrs:
            if attr == 'href':
                return self._url_add(val)

    def _img_search(self, attrs):
        """<img>のsrcかsrcsetを探す"""
        result = None

        if not len(attrs):
            return None
        
        for attr, val in attrs:
            if attr == "src":
                return self._url_add(val)

    def _check(self, url):
        if not url:
            return

        abs_url = self._abs_url(url)
        filtered = url_filter(abs_url)

        return filtered





if __name__ == '__main__':
    x = ImgFinder('https://example.com/')
    html = """
        <!doctype html>
            <html>
                <head>
                    <title>test</title>
                </head>
                <body>
                    <a href="cnt/page.html">page</a>
                    <img src="https://example.com/image.jpg"/>
                    <img src="./aa.png">
                </body>
            </html>"""
    x.feed(html)

    print('発見したURLの集合', x._urls)

