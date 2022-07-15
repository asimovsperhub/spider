import json
import requests
import base64
from urllib.parse import unquote
import os, jpype
import redis


# class obBase64(object):
#     # decodingTable = []
#     # encodingTable = []
#     def __init__(self):
#         b2 = [48, 57, 95, 45, 49, 56, 54, 51, 52, 50, 55, 53, 35]
#         bArr2 = [i for i in b2]
#         bArr3 = [i + 65 for i in range(len(bArr2))]
#         bArr4 = [(bArr3[len(bArr3) - 1] + i) + 1 for i in range(len(bArr3))]
#         bArr5 = [i + 97 for i in range(len(bArr4))]
#         bArr6 = [(bArr5[len(bArr5) - 1] + i) + 1 for i in range(len(bArr5))]
#         bArr = [i for i in [bArr5, bArr2, bArr3, bArr6, bArr4]]
#         i2 = 0
#         bArr7 = []
#         for i in range(len(bArr[0]) * len(bArr)):
#             bArr7.append([bArr[i % 5], [i / 5]])
#             if bArr7[i] == 108:
#                 i2 = i
#         bArr8 = []
#         for i in range(i2):
#             bArr8.append(bArr7[i])
#         for i in range(64 - i2):
#             bArr8.insert(i2 + i, bArr7[i2 + 1 + i])
#         self.encodingTable = bArr8
#         self.decodingTable = []
#         for i in range(len(self.encodingTable)):
#             self.decodingTable[self.encodingTable[i]] = i
#
#     def decode(self, data: bytearray) -> bytearray:
#         bArr = [((((len(data) / 4) - 1) * 3) + 1) if data[len(data) + -2] == 108 else
#                 ((((len(data) / 4) - 1) * 3) + 2) if data[len(data) + -1] == 108 else ((len(data) / 4) * 3)]
#
#         i = 0
#         i2 = 0
#         while i < len(data) - 4:
#             b = self.decodingTable[data[i]]
#             b2 = self.decodingTable[data[i + 1]]
#             b3 = self.decodingTable[data[i + 2]]
#             b4 = self.decodingTable[data[i + 3]]
#             bArr[i2] = (b << 4) | (b2 >> 4)
#             bArr[i2 + 1] = (b2 << 4) | (b3 >> 2)
#             bArr[i2 + 2] = (b3 << 6) | b4
#             i += 4
#             i2 += 3
#         if data[len(data) - 2] == 108:
#             bArr[len(bArr) - 1] = (self.decodingTable[data[len(data) - 4]] << 2) | (
#                     self.decodingTable[data[len(data) - 3]] >> 4)
#         elif data[len(data) - 1] == 108:
#             b = self.decodingTable[data[len(data) - 4]]
#             b2 = self.decodingTable[data[len(data) - 3]]
#             b3 = self.decodingTable[data[len(data) - 2]]
#             bArr[len(bArr) - 2] = (b << 2) | (b2 >> 4)
#             bArr[len(bArr) - 1] = (b2 << 4) | (b3 >> 2)
#         else:
#             b = self.decodingTable[data[len(data) - 4]]
#             b2 = self.decodingTable[data[len(data) - 3]]
#             b3 = self.decodingTable[data[len(data) - 2]]
#             b4 = self.decodingTable[data[len(data) - 1]]
#             bArr[len(bArr) - 3] = (b << 2) | (b2 >> 4)
#             bArr[len(bArr) - 2] = (b2 << 4) | (b3 >> 2)
#             bArr[len(bArr) - 1] = (b3 << 6) | b4
#         return bArr
#
#     def Dodecode(self, data: str):
#         # bytearry 对应java中 data.getBytes()
#         return str(self.decode(bytearray(data, encoding='utf-8')).decode('utf-8'))
#
# def ObfuseBase64(self, decodeStr: str) -> str:
#     if decodeStr.startswith("{") or decodeStr.endswith("}"):
#         return decodeStr
#     if decodeStr.startswith("\"") and decodeStr.endswith("\""):
#         decodeStr = decodeStr[1:len(decodeStr) - 1]
#     return self.Dodecode(decodeStr)


class Mrzb(object):
    __slots__ = ["_driverId", "_phone", "_password", "_cid", "_os", "_appversion", "_userId", "_device", "jvmstatus"]

    # global jvmstatus
    # jvmstatus = {"status": -1}

    def __init__(self):
        self._driverId = "3a49ca48dc9e772074fb1a4ac8746c9de"
        self._phone = "18675528647"
        self._password = "qwert12345"
        self._cid = "mr360ZS"
        self._os = "android"
        self._appversion = "8110"
        self._userId = ""
        self._device = "HWGRA"

    @staticmethod
    def decode(sIn: str) -> json:
        try:
            jarpath = "/home/root1/deco.jar"
            if not jpype.isJVMStarted():
                jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % jarpath, convertStrings=True)
            Test = jpype.JClass('deco.ObfuseTableBase64')
            t = Test()
            jsonObject = t.doDecode(sIn)
            jsonObject_ = unquote(jsonObject)
            # jpype.shutdownJVM()
            return str(jsonObject_)

        except UnicodeEncodeError as e:
            print(e)

    def login(self):
        sRequest = "phone=%s" % self._phone + \
                   "&password=%s" % self._password + \
                   "&driverid=%s" % self._driverId + \
                   "&cid=%s" % self._cid + \
                   "&os=%s" % self._os + \
                   "&appversion=%s" % self._appversion + \
                   "&device=%s" % self._device + \
                   "&cert=" + "CXeKPnoxCERLREokpXOHC9NLPQb3fQ-Kp9RxRQ0tpnal"

        url = "https://zhibo.lvdou66.com/account/user/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        rep = requests.post(url=url, data=sRequest, headers=headers, )
        msg = json.loads(self.decode(rep.text))
        token = msg.get("token")
        uid = msg.get("uid")
        return uid, token

    def data(self) -> str:
        uid, token = self.login()
        if uid or token:
            data = "uid=%s&driverid=%s" % (uid, self._driverId) + "&fid=%s" + "&device=%s&" % self._device + \
                   "manufactruer=brand&cid=%s&plat=12&os=%s&appversion=%s&brand=brand&shell=shell135&" % (
                       self._cid, self._os, self._appversion) + \
                   "pkg=miren&model=HUAWEI GRA-UL00&imsi=&bootloader=unknown&" + \
                   "cert=CXeKPnoxCERLREokpXOHC9NLPQb3fQ-Kp9RxRQ0tpnal" + "&token=%s" % token
            return data
        return ""


if __name__ == '__main__':
    m = Mrzb()
    m.login()
    print(m.data())
