"""创建一个addons类，对捕获的接口数据，进行解密"""
import mitmproxy.http
from logging import error, ERROR, basicConfig
from base64 import b64decode
from mitmproxy.script import concurrent
from myproject.dec import decrypt


class Addon(object):
    def __init__(self, need_listen):
        self.need_listen = set(need_listen.split("|"))
        self.decrypt = decrypt()
        basicConfig(
            level=ERROR,
            filename='logfile/error.log',
            filemode='a',
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    @concurrent
    def response(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host not in self.need_listen:
            return
        else:
            try:
                # 使用text会使用utf-8解码，打开单体时的js会导致报错，故而采用字节判断
                # Y4kSy 暂定为是否进行解密的依据
                if flow.response.content[:5] != b'Y4kSy':
                    return
                # 调用解密的js文件，返回base64编码的字符串。拿到的数据转码为utf-8返回客户端
                if result := self.decrypt.call('decrypt', flow.response.text):
                    flow.response.text = b64decode(result).decode("utf-8")
                else:
                    return
            except Exception as e:
                error("Url: %s   Msg: %s" % (flow.request.url, e))
                return
