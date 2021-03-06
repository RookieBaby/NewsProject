# -*- coding:utf-8 -*-
from decimal import *
from urllib.parse import urljoin

from fdfs_client.client import *
import requests
from hashlib import md5
from retrying import retry
class File_mod(object):
    def __init__(self, image_url, content, response_url):
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"}

        self.client = Fdfs_client('/etc/fdfs/client.conf')
        self.image_url = image_url
        self.content = content
        self.url = response_url
        self.response_url = response_url
    def detail_file(self):
        """
        处理文章,替换文章中的image_url
        :return:
        """
        full_name = self.Download_image()
        self.detail_FileLength(full_name)
        New_url = self.detail_fdfs_file(full_name)
        contents = self.content.replace(self.image_url, New_url)
        self.Delete_image(full_name)
        return contents

    def Download_image(self):
        """
        下载图片
        :return:
        """
        if self.image_url.startswith('//'):
            image_after = urljoin(self.response_url, self.image_url)

            response = requests.get(image_after, headers=self.headers).content
            file_name = md5(response).hexdigest()
            file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'jpg')
            full_name = os.getcwd() + "/" + file_name + '.jpg'
            self.save_file(file, response)
            return full_name
        else:
            response = requests.get(self.image_url, headers=self.headers).content
            file_name = md5(response).hexdigest()
            file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'jpg')
            full_name = os.getcwd() + "/" + file_name + '.jpg'
            self.save_file(file, response)
            return full_name

    @retry(stop_max_attempt_number=7)
    def Download_video(self):
        """
        下载图片或者视频
        :return:
        """
        try:
            response = requests.get(self.image_url, headers=self.headers).content
            if response:
                file_name = md5(response).hexdigest()
                file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'mp4')
                full_name = os.getcwd() + "/" + file_name + '.mp4'
                self.save_file(file, response)
                return full_name

        except requests.exceptions.ConnectionError:
            print('请求失败')
            return None
            # except UnicodeDecodeError:
            #     pass
        except requests.exceptions.MissingSchema:
            print('请求失败')
            return None


    def save_file(self,file, response):
        """
        保存图片到本地
        :param file:
        :param response:
        :return:
        """
        if not os.path.exists(file):
            with open(file, "wb") as f:
                f.write(response)
                f.close()
    def detail_FileLength(self, full_name):
        """
        处理filelength
        :param full_name:
        :return:
        """
        a = str(os.path.getsize(full_name) / 1024)
        # b = Decimal(a).quantize(Decimal('0.00'))
        b = round(float(a), 2)
        return b

    def detail_fdfs_file(self, full_name):
        """
        处理图片为文件服务器格式
        :param full_name:
        :return:
        """
        ret = self.client.upload_by_filename(full_name)
        new_url = str(ret['Remote file_id'], encoding="utf8")
        return new_url

    def Delete_image(self, full_name):
        """
        删除已经下载的图片
        :param full_name:
        :return:
        """
        os.remove(full_name)

    def Delete_video(self, full_name):
        """
        删除已经下载的图片
        :param full_name:
        :return:
        """
        os.remove(full_name)
