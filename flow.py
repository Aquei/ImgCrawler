import feedparser
import utl
from PIL import Image
import io
import zipfile
import time
from img import Img
from imgfinder import ImgFinder

def feed_parse(feed):
    """設定ファイルにあるフィードを取得、パース"""
    if not 'url' in feed:
        print(utl.highlighted('this feed has no feed url, bye', 'danger'))
        return

    if not 'name' in feed:
        print(utl.highlighted('this feed has no feed name, bye', 'danger'))
        return

    if not 'lastUpdate' in feed:
        print(utl.highlighted('this feed has no lastUpdate, seems 0', 'warn'))
        feed['lastUpdate'] = 0

    data = utl.file_get(feed['url'])
    if not data:
        print(utl.highlighted('リクエストに失敗したのでスキップします', 'warn'))
        return

    feed = feedparser.parse(data.text)

    return feed

def feed_worker(feed, feed_data=None, min_time=utl.epoch2time(0)):
    """パースされたフィードを解析"""
    if not len(feed.entries):
        print(utl.highlighted('this feed has no entry', 'danger'))
        return
    
    urls = set()
    
    for entry in feed.entries:
        #min_timeより古い記事はスキップ
        if 'updated_parsed' in entry:
            issued = entry.updated_parsed
        elif 'published_parsed' in entry:
            issued = entry.published_parsed
        else:
            issued = time.gmtime(0)


        if time.mktime(min_time) >= time.mktime(issued):
            continue

        contents = entry.content
        for content in contents:
            if 'base' in content and content.base:
                base = content.base
            elif feed_data and 'url' in feed_data:
                base = feed_data['url']
            else:
                print(feed_data)


            img_search = ImgFinder(base)
            img_search.feed(content.value)
            new_urls = img_search.get_urls()
            if len(new_urls):
                urls.update(new_urls)


    if 'title' in feed.feed:
        feed_title = feed.feed.title
    else:
        feed_title = 'Feed'

    if urls:
        msg = utl.highlighted(len(urls), 'info') + ' URLs found on ' + utl.highlighted(feed_title, 'info')
        print(msg)

    else:
        msg = utl.highlighted('no URL', 'danger') + ' found on' + utl.highlighted(feed_title, 'info')

    return urls



def extract_image_zip(file_like):
    if not zipfile.is_zipfile(file_like):
        return None

    print('zipファイルから画像を抽出します')
    
    images = []

    with zipfile.ZipFile(file_like) as myzip:
        for path in myzip.namelist():
            #/で終わるパスはディレクトリである
            if path.endswith('/'):
                continue
            with myzip.open(path) as myfile:
                images.append(myfile.read())


    return images








def file_checker(url, min_width=0, min_height=0):
    """URL先が画像ファイルで指定された大きさ以上なら画像データを返す"""
    
    def image_prc(bin_str):
        image = Img(bin_str)
        
        #画像でないデータなら無視
        if not image.isImage:
            return
        
        #指定されたサイズより小さければ無視
        if not image.is_larger((int(min_width), int(min_height))):
            return

        return image

    #リストでImgが入る
    images = []

    req = utl.file_get(url)
    mime_zip = 'application/zip', 'multipart/x-zip', 'application/x-zip-compressed', 'application/x-zip'
  
    #リクエストがエラーならreturn
    if not req:
        return

    image = image_prc(req.content)
    if image:
        images.append(image)

    else:

        #zipファイルの場合
        content_type = req.headers.get('content-type').lower()
        if content_type in mime_zip:
            #zip_entriesはzip内エントリーのbytesが入ったリスト or None
            zip_entries = extract_image_zip(io.BytesIO(req.content))
            if zip_entries is None:
                return

            #entryはbytes
            for entry in zip_entries:
                result = image_prc(entry)
                #zipファイルのエントリーが画像であることを確かめる
                if result:
                    images.append(result)

    return images





