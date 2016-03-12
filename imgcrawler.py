import utl
from imgfinder import ImgFinder
from datetime import datetime
from pprint import pprint
import flow
from pathlib import Path

def welcome():
    """起動時のこんにちはメッセージ"""
    now = datetime.now()
    msg = now.strftime("%x %X")
    print('Image Crawler', utl.highlighted(msg, 'info'))

    

def main():
    """メイン関数"""
    welcome()

    conf = utl.load_config()
    config = conf["config"]
    feeds = conf["feeds"]
    

    count = 0
    for feed in feeds:
        #パースに失敗したら次のフィードへ
        parsed_feed = flow.feed_parse(feed)
        if not parsed_feed:
            continue
        
        #画像のURLを探す
        if 'lastUpdate' in feed:
            last_update = feed['lastUpdate']
        else:
            last_update = 0
        min_time = utl.epoch2time(last_update)
        #resultはファイルのURLのセット
        result = flow.feed_worker(parsed_feed, feed_data=feed, min_time=min_time)
        if not result:
            continue

        for url in result:
            #image_listはNoneかImgのリスト
            image_list = flow.file_checker(url, min_width=config['min_width'], min_height=config['min_height'])

            if image_list:
                for im in image_list:
                    save_dir = Path(config.get('path') or Path.cwd()) / (feed.get('name') or 'unknown')
                    im.save(save_dir)

        #このフィードのタイムスタンプをアップデート
        feed['lastUpdate'] = utl.epoch_now()

        #設定ファイルをアップデート
        utl.save_config(conf)



            
        









if __name__ == '__main__':
    main()
