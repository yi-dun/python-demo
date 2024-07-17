#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""易
盾直播音频结果获取接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python3.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python liveaudio_callback.py
"""
__author__ = 'yidun-dev'
__date__ = '2020/01/06'
__version__ = '0.2-dev'

import hashlib
import time
import random
import urllib3
from urllib.parse import urlencode
import json
from gmssl import sm3, func


class LiveAudioCallbackAPIDemo(object):
    """直播音频检测结果获取接口示例代码"""

    API_URL = "http://as.dun.163.com/v4/liveaudio/callback/results"
    VERSION = "v4"  # 直播语音版本v2.1及以上二级细分类结构进行调整

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
        params["nonce"] = int(random.random()*100000000)
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

    def parse_machine(self, evidences, taskId):
        """机审信息"""
        print("=== 机审信息 ===")
        asr_status: int = evidences["asrStatus"]
        start_time: int = evidences["startTime"]
        end_time: int = evidences["endTime"]
        if asr_status == 4:
            asr_result: int = evidences["asrResult"]
            print("检测失败: taskId=%s, asrResult=%s" % (taskId, asr_result))
        else:
            action: int = evidences["action"]
            segment_array: list = evidences["segments"]
            if action == 0:
                print("taskId=%s，结果：通过，时间区间【%s-%s】，证据信息如下：%s" % (taskId, start_time, end_time, segment_array))
            elif action == 1 or action == 2:
                for segment_item in segment_array:
                    label: int = segment_item["label"]
                    level: int = segment_item["level"]
                    sub_labels: list = segment_item["subLabels"]
                print("taskId=%s，结果：%s，时间区间【%s-%s】，证据信息如下：%s" % (taskId, "不确定" if action == 1 else "不通过", start_time, end_time, segment_array))
        print("================")

    def parse_human(self, review_evidences, taskId):
        """人审信息"""
        print("=== 人审信息 ===")
        action: int = review_evidences["action"]
        action_time: int = review_evidences["actionTime"]
        spam_type: int = review_evidences["spamType"]
        spam_detail: str = review_evidences["spamDetail"]
        warn_count: int = review_evidences["warnCount"]
        promp_count: int = review_evidences["prompCount"]
        segments: list = review_evidences["segments"]
        status: int = review_evidences["status"]
        status_str: str = "未知"

        if status == 2:
            status_str = "检测中"
        elif status == 3:
            status_str = "检测完成"

        if action == 2:
            print("警告, taskId:%s, 检测状态:%s, 警告次数:%s, 违规详情:%s, 证据信息:%s" % (taskId, status_str, warn_count, spam_detail, segments))
        elif action == 3:
            print("断流, taskId:%s, 检测状态:%s, 警告次数:%s, 违规详情:%s, 证据信息:%s" % (taskId, status_str, warn_count, spam_detail, segments))
        elif action == 4:
            print("提示, taskId:%s, 检测状态:%s, 提示次数:%s, 违规详情:%s, 证据信息:%s" % (taskId, status_str, promp_count, spam_detail, segments))
        else:
            print("人审信息：%s" % review_evidences)
        print("================")


if __name__ == "__main__":
    """示例代码入口"""
    SECRET_ID = "your_secret_id"  # 产品密钥ID，产品标识
    SECRET_KEY = "your_secret_key"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "your_business_id"  # 业务ID，易盾根据产品业务特点分配
    api = LiveAudioCallbackAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    
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
                    callback: str = antispam["callback"]
                    dataId: str = antispam["dataId"]
                    print("taskId:%s, callback:%s, dataId:%s" % (taskId, callback, dataId))
                    evidences: dict = result["evidences"]
                    review_evidences: dict = result["reviewEvidences"]
                    if evidences is not None:
                        api.parse_machine(evidences, taskId)
                    elif review_evidences is not None:
                        api.parse_human(review_evidences, taskId)
                    else:
                        print("Invalid result: %s", result)
                asr: dict = result["asr"]
                if asr is not None:
                    taskId: str = asr["taskId"]
                    startTime: int = asr["startTime"]
                    endTime: int = asr["endTime"]
                    content: str = asr["content"]
                    print("taskId=%s，content=%s，startTime=%s秒，endTime=%s秒" % (taskId, content, startTime, endTime))
    else:
        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
