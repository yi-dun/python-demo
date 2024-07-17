#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
易盾易盾反垃圾云服务音频离线结果获取接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python3.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python audio_callback.py
"""
__author__ = 'yidun-dev'
__date__ = '2019/11/27'
__version__ = '0.2-dev'

import hashlib
import time
import random
import urllib3
from urllib.parse import urlencode
import json
from gmssl import sm3, func


class AudioCallbackAPIDemo(object):
    """音频离线结果获取接口示例代码"""

    API_URL = "http://as.dun.163.com/v4/audio/callback/results"
    VERSION = "v4"  # 点播语音版本v3.2及以上二级细分类结构进行调整

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
        self.http = urllib3.PoolManager()  # 初始化连接池

    def gen_signature(self, params=None):
        """生成签名信息
        Args:
            params (object) 请求参数
        Returns:
            参数签名md5值
        """
        buff = ""
        for k in sorted(params.keys()):
            buff += str(k) + str(params[k])
        buff += self.secret_key
        if "signatureMethod" in params.keys() and params["signatureMethod"] == "SM3":
            return sm3.sm3_hash(func.bytes_to_list(bytes(buff, encoding='utf8')))
        else:
            return hashlib.md5(buff.encode("utf8")).hexdigest()

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
        params["nonce"] = int(random.random() * 100000000)
        # params["signatureMethod"] = "SM3"  # 签名方法，默认MD5，支持SM3
        params["signature"] = self.gen_signature(params)

        try:
            encoded_params = urlencode(params).encode("utf8")
            response = self.http.request(
                'POST',
                self.API_URL,
                body=encoded_params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=urllib3.Timeout(connect=10, read=10)
            )
            content = response.data
            return json.loads(content)
        except Exception as ex:
            print("调用API接口失败:", str(ex))


if __name__ == "__main__":
    """示例代码入口"""
    SECRET_ID = "your_secret_id"  # 产品密钥ID，产品标识
    SECRET_KEY = "your_secret_key"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "your_business_id"  # 业务ID，易盾根据产品业务特点分配
    api = AudioCallbackAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    
    ret = api.check()

    code: int = ret["code"]
    msg: str = ret["msg"]
    if code == 200:
        resultArray: list = ret["result"]
        if resultArray is None or len(resultArray) == 0:
            print("暂时没有结果需要获取, 请稍后重试!")
        else:
            for result in resultArray:
                antispam: dict = result["antispam"]
                if antispam is not None:
                    taskId: str = antispam["taskId"]
                    status: int = antispam["status"]
                    if status == 2:
                        print("CHECK SUCCESS: taskId=%s" % taskId)
                        suggestion: int = antispam["suggestion"]
                        resultType: int = antispam["resultType"]
                        segmentArray: list = antispam["segments"]
                        if segmentArray is None or len(segmentArray) == 0:
                            print("暂无反垃圾检测数据")
                        else:
                            for segment in segmentArray:
                                startTime: int = segment["startTime"]
                                endTime: int = segment["endTime"]
                                content: str = segment["content"]
                                labelArray: list = segment["labels"]
                                for labelInfo in labelArray:
                                    label: int = labelInfo["label"]
                                    level: int = labelInfo["level"]
                                    subLabels: list = labelInfo["subLabels"]
                language: dict = result["language"]
                if language is not None:
                    taskId: str = language["taskId"]
                    dataId: str = language["dataId"]
                    callback: str = language["callback"]
                    detailsArray: list = language["details"]
                    if detailsArray is not None and len(detailsArray) > 0:
                        for detail in detailsArray:
                            typeLan: str = detail["type"]
                            segmentsArray: list = detail["segments"]
                            if segmentsArray is not None and len(segmentsArray) > 0:
                                for segment in segmentsArray:
                                    print("taskId=%s，语种类型=%s，开始时间=%s秒，结束时间=%s秒" % (taskId, typeLan, segment["startTime"], segment["endTime"]))
                asr: dict = result["asr"]
                if asr is not None:
                    taskId: str = asr["taskId"]
                    dataId: str = asr["dataId"]
                    callback: str = asr["callback"]
                    detailsArray: list = asr["details"]
                    if detailsArray is not None and len(detailsArray) > 0:
                        for detail in detailsArray:
                            startTime: int = detail["startTime"]
                            endTime: int = detail["endTime"]
                            content: str = detail["content"]
                            print("taskId=%s，文字翻译结果=%s，开始时间=%s秒，结束时间=%s秒" % (taskId, content, startTime, endTime))
                voice: dict = result["voice"]
                if voice is not None:
                    taskId: str = voice["taskId"]
                    dataId: str = voice["dataId"]
                    callback: str = voice["callback"]
                    detail: dict = voice["detail"]
                    print("taskId=%s，人声属性=%s" % (taskId, detail["mainGender"]))
    else:
        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
