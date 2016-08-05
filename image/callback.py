#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""易盾图片离线检测结果获取接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python2.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python image_check_callback_demo.py
"""
__author__ = 'yidun-dev'
__date__ = '2016/3/10'
__version__ = '0.1-dev'

import hashlib
import time
import random
import urllib
import urllib2
import json

class ImageCheckCallbackAPIDemo(object):
    """易盾图片离线检测结果获取接口示例代码"""
    API_URL = "https://api.aq.163.com/v2/image/callback/results"
    VERSION = "v2"

    def __init__(self, secret_id, secret_key, business_id):
        """
        Args:
            secret_id (str) 产品密钥ID，产品标识
            secret_key (str) 产品私有密钥，服务端生成签名信息使用
            business_id (str) 业务ID，易盾根据产品业务特点分配
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.business_id = business_id

    def gen_signature(self, params=None):
        """生成签名信息
        Args:
            params (object) 请求参数
        Returns:
            参数签名md5值
        """
        buff = ""
        for k in sorted(params.keys()):
            buff += str(k)+ str(params[k])
        buff += self.secret_key
        return hashlib.md5(buff).hexdigest()

    def check(self):
        """请求易盾接口
        Returns:
            请求结果，json格式
        """
        params = {}
        params["secretId"] = self.secret_id
        params["businessId"] = self.business_id
        params["version"] = self.VERSION
        params["timestamp"] = int(time.time() * 1000)
        params["nonce"] = int(random.random()*100000000)
        params["signature"] = self.gen_signature(params)

        try:
            params = urllib.urlencode(params)
            request = urllib2.Request(self.API_URL, params)
            content = urllib2.urlopen(request, timeout=10).read()
            # print content
            # content = "{\"code\":200,\"msg\":\"ok\",\"timestamp\":1453793733515,\"nonce\":1524585,\"signature\":\"630afd9e389e68418bb10bc6d6522330\",\"result\":[{\"image\":\"http://img1.cache.netease.com/xxx1.jpg\",\"labels\":[]},{\"image\":\"http://img1.cache.netease.com/xxx2.jpg\",\"labels\":[{\"label\":100,\"level\":2,\"rate\":0.99},{\"label\":200,\"level\":1,\"rate\":0.5}]},{\"image\":\"http://img1.cache.netease.com/xxx3.jpg\",\"labels\":[{\"label\":200,\"level\":1,\"rate\":0.5}]}]}";
            return json.loads(content)
        except Exception, ex:
            print "调用API接口失败:", str(ex)

if __name__ == "__main__":
    """示例代码入口"""
    SECRET_ID = "your_secret_id" # 产品密钥ID，产品标识
    SECRET_KEY = "your_secret_key" # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "your_business_id" # 业务ID，易盾根据产品业务特点分配
    image_check_callback_api = ImageCheckCallbackAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)

    ret = image_check_callback_api.check()

    # print json.dumps(ret)
    if ret["code"] == 200:
        results = ret["result"]
        for result in results:
            name = result["name"]
            print name
            for label in result["labels"]:
                print "---- label=%s, level=%s, rate=%s" % (label["label"], label["level"], label["rate"])
    else:
        print "ERROR: ret.code=%s, ret.msg=%s" % (ret["code"], ret["msg"])
