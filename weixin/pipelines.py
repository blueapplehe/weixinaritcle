# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from weixin.items import *
import sys
import os
import requests
from scrapy_splash import SplashRequest
import urllib.request
import random
import hashlib
from pymongo import MongoClient
import time
from scrapy.conf import settings
import shutil
class WeixinPipeline():
    def process_item(self, item, spider):
        return item
        
          
class MongoDBPipeline():
    def process_item(self, item, spider):
        conn = MongoClient('127.0.0.1', 27017)
        db = conn.baidu
        weixin = db.weixin
        search_word=item['search_word']
        title=item["title"]
        js_name=item["js_name"]
        publish_time=item["publish_time"]
        content=item["content"]

        if title !="":
            isFind=weixin.find_one({"title":title})
            if isFind is None:
                weixin.insert_one({"search_word":search_word,"title":title,"js_name":js_name,\
                "publish_time":publish_time,"content":content})
                print("插入数据："+title)
            else:
                print("已经存在，不进行数据插入:"+title)
            return item
        else:
            print("title为空"+title)

class DownloadImagePipeline(ImagesPipeline):
    def get_media_requests(self,item,info):
        image_urls=item["image_urls"]
        for image_url in image_urls:
            yield scrapy.Request(url=image_url,meta={'is_image': True})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            #raise DropItem("Item contains no images")
            return item
        IMAGES_STORE=settings.get('IMAGES_STORE')
        img_paths=[]
        i=1
        for image_path in image_paths:
            target_path="/data/weixinimages"
            name_dir=target_path+"/"+item["title"]
            if not os.path.exists(name_dir):
                os.mkdir(name_dir)
            origin_file=IMAGES_STORE+"/"+image_path
            filename = os.path.basename(origin_file)
            ext=filename.split(".")[1]
            ext=ext.lower()
            if ext!="jpg" and ext!="png" and ext!="jpeg":
                return item 
            target_file=name_dir+"/"+str(i)+"."+ext
            i=i+1
            shutil.copyfile(origin_file,target_file)
            img_paths.append(target_file)
        item["images_paths"]=img_paths
        return item
    