import base64
import json
from Crypto.Cipher import AES
from Crypto.Hash import MD5
import requests
import hashlib
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Origin": "https://fanyi.youdao.com",
    "Referer": "https://fanyi.youdao.com/",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def get_OUTFOX_SEARCH_USER_ID_NCOO():
    random_number = random.random() * 2147483647
    return str(random_number)


def get_cookies():
    OUTFOX_SEARCH_USER_ID_NCOO = get_OUTFOX_SEARCH_USER_ID_NCOO()
    time_ = int(time.time() * 1000)
    last_modified = (time_ - 7 * 86400000) // 1000
    url = "https://rlogs.youdao.com/rlog.php"
    params = {
        "_npid": "fanyiweb",
        "_ncat": "pageview",
        "_ncoo": OUTFOX_SEARCH_USER_ID_NCOO,
        "_nssn": "NULL",
        "_nver": "@VERSION@",
        "_ntms": time_,
        "_dict_ut": "NULL",
        "_nref": "",
        "_nurl": "https://fanyi.youdao.com/indexLLM.html#/",
        "_nres": "1384x779",
        "_nlmf": last_modified,
        "_njve": "0",
        "_nchr": "utf-8",
        "_nfrg": "/",
        "/": "NULL",
        "screen": "1384*779"
    }
    cookies = {
        "OUTFOX_SEARCH_USER_ID_NCOO": OUTFOX_SEARCH_USER_ID_NCOO
    }
    response = requests.get(url, headers=HEADERS, cookies=cookies, params=params)

    cookies.update(response.cookies.get_dict())
    return cookies


def get_timestamp():
    # 获取当前时间戳（10位）
    timestamp_10 = int(time.time())
    # 转换为13位时间戳
    timestamp_13 = timestamp_10 * 1000
    return timestamp_13


def get_sign(mysticTime, key):
    # 要计算哈希值的字符串
    input_string = f"client=fanyideskweb&mysticTime={mysticTime}&product=webfanyi&key={key}"
    # 创建一个 MD5 哈希对象
    md5_hash = hashlib.md5()
    # 更新哈希对象的输入数据，需要将字符串编码为字节
    md5_hash.update(input_string.encode('utf-8'))
    # 获取哈希值的十六进制表示
    hash_value = md5_hash.hexdigest()
    return hash_value


def get_secretKey(mysticTime, key, cookies):
    url = "https://dict.youdao.com/webtranslate/key"
    params = {
        "keyid": "webfanyi-key-getter",
        "sign": get_sign(mysticTime, key),
        "client": "fanyideskweb",
        "product": "webfanyi",
        "appVersion": "1.0.0",
        "vendor": "web",
        "pointParam": "client,mysticTime,product",
        "mysticTime": mysticTime,
        "keyfrom": "fanyi.web",
        "mid": "1",
        "screen": "1",
        "model": "1",
        "network": "wifi",
        "abtest": "0",
        "yduuid": "abcdefg"
    }
    response = requests.get(url, headers=HEADERS, cookies=cookies, params=params).json()
    data = response.get('data')
    if not data:
        print('secretKey获取失败')
        return
    else:
        return data['secretKey']


def get_webtranslate(mysticTime, key, cookies, word):
    url = "https://dict.youdao.com/webtranslate"
    data = {
        "i": word,
        "from": "zh-CHS",
        "to": "en",
        "domain": "0",
        "dictResult": "true",
        "keyid": "webfanyi",
        "sign": get_sign(mysticTime, key),
        "client": "fanyideskweb",
        "product": "webfanyi",
        "appVersion": "1.0.0",
        "vendor": "web",
        "pointParam": "client,mysticTime,product",
        "mysticTime": mysticTime,
        "keyfrom": "fanyi.web",
        "mid": "1",
        "screen": "1",
        "model": "1",
        "network": "wifi",
        "abtest": "0",
        "yduuid": "abcdefg"
    }
    response = requests.post(url, headers=HEADERS, cookies=cookies, data=data)
    return response.text


def get_decodeData(data):
    # 这里必须是字节字符串
    key = b"ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    iv = b"ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    cryptor = AES.new(MD5.new(key).digest()[:16], AES.MODE_CBC, MD5.new(iv).digest()[:16])
    res = cryptor.decrypt(base64.urlsafe_b64decode(data))
    txt = res.decode("utf-8")
    decrypted_text = json.loads(txt[: txt.rindex("}") + 1])
    return decrypted_text


if __name__ == '__main__':
    key = 'asdjnjfenknafdfsdfsd'
    word = '你好'
    # secretKey='fsdsogkndfokasodnaso'
    cookies = get_cookies()
    secretKey = get_secretKey(get_timestamp(), key, cookies)
    webtranslate_data = get_webtranslate(get_timestamp(), secretKey, cookies, word)
    translateResult = get_decodeData(webtranslate_data)
    print(translateResult['translateResult'][0][0]['tgt'])