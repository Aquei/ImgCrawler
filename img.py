from PIL import Image
import io
import hashlib
from pathlib import Path
import utl


class Img():
    def __init__(self, byte_str):
        self.byte_str = byte_str
        self.isImage = True

        try:
            self.get_image()
        except IOError:
            self.isImage = False


    def get_file_like(self):
        """ファイルライクオブジェクトを返す"""
        return io.BytesIO(self.byte_str)

    def get_hash(self, arg='md5'):
        """ハッシュ値を返す"""

        if arg == 'md5':
            m = hashlib.md5()
        else:
            m = hashlib.new('arg')
        
        m.update(self.byte_str)

        return m.hexdigest()

    def get_image(self):
        """PillowのImageを返す"""
        if not self.isImage:
            return

        with Image.open(self.get_file_like()) as im:
            return im

    def is_larger(self, size=(0,0)):
        """(width, height)より大きいかどうか"""
        img = self.get_image()
        img_size = img.size

        if img_size[0] >= size[0] and img_size[1] >= size[1]:
            return True
        else:
            return False

    def get_ext(self):
        """拡張子を取得"""
        normalized = {
                'jpeg': 'jpg',
                'jpeg2000': 'j2p'}

        image = self.get_image()

        if image is not None:
            fmt = image.format.lower()

            if fmt in normalized:
                return normalized[fmt]
            else:
                return fmt

    def get_image_file_size(self):
        """画像のファイルサイズを文字列で返す"""
        return utl.bytes_size_str(self.byte_str)


    def save(self, save_dir):
        """保存する"""
        file_name = self.get_hash() + '.' + self.get_ext()

        p = Path(save_dir)

        if not p.exists():
            #パスが存在しないので作成する
            p.mkdir(parents=True)
        
        save_path = p / file_name

        if save_path.exists():
            print(utl.highlighted(save_path, 'danger') + 'はすでに存在します')
            return
        else:
            #保存
            print(str(save_path) + 'へファイルに保存します')
            save_path.write_bytes(self.byte_str)





