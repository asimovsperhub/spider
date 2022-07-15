import json
import logging

import scrapy
from fake_useragent import UserAgent

from ..items import GeneralItem

"""
newuser : https://api.wfdata.club/v1/forum/info

user接口 : https://api.wfdata.club/v1/user/6336183/homePageInfo?0=6336183       
6336183用户id = 数量
userId: "6336183"
userName: "简约_"

rep {data:{userBaseInfo:{user_id,username}}}
"""

import time
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from binascii import b2a_hex, a2b_hex
import base64


def pkcs7_padding(data):
    if not isinstance(data, bytes):
        data = data.encode()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    padded_data = padder.update(data) + padder.finalize()

    return padded_data


def encrypt(text, password=b'2b7e151628aed2a6'):
    cryptor = AES.new(password, AES.MODE_CBC, password)
    text = text.encode('utf-8')

    text = pkcs7_padding(text)

    ciphertext = cryptor.encrypt(text)

    return base64.encodebytes(ciphertext).decode('utf8').strip().replace('\n', '')


def wfGetHeaders(path):
    t = str(round(time.time() * 1000)) + "000000"
    sign_url = f"url={path}$time={t}"
    return {
        'user-agent': str(UserAgent(verify_ssl=False).random),
        'Connection': 'keep-alive',
        "x-request-id": encrypt(sign_url),
    }


# user_url = "https://api.wfdata.club/v1/user/%s/homePageInfo" % uid
# singe_url = "url=/v1/user/%s/homePageInfo$time=%s" % (uid, str(round(time.time() * 1000)) + "000000")
# singe = b'2b7e151628aed2a6'
# c = encrypt(singe_url, singe)


class WEIFENG(scrapy.Spider):
    name = "wfdata"

    def __init__(self):
        self.item = GeneralItem()

    def start_requests(self):
        for uid in range(20000000):
            path = "/v1/user/%s/homePageInfo" % uid
            user_url = "https://api.wfdata.club"+path

            headers = wfGetHeaders(path)
            self.start = float(time.time())
            yield scrapy.Request(url=user_url, headers=headers, callback=self.user_, cb_kwargs={"uid": uid})

    def user_(self, rep, uid):
        data = json.loads(rep.text).get("data")
        if data:
            self.item["username"] = json.loads(rep.text).get("data").get("userBaseInfo").get("userName")
            self.item["url"] = "https://www.feng.com/user/%s/moments" % uid
            yield self.item
            end = float(time.time())
            logging.info("WFdata One Spider Time : %s" % (end - self.start))
