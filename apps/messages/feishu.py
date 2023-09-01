from .base import MessageSendingBase
import requests
import json
from datetime import datetime
import hmac
import hashlib
import base64


class FeishuMessageSending(MessageSendingBase):
    def __init__(self, message_body: dict, target: str, **kwargs) -> None:
        """
        :param message_body: dict格式的消息内容
        :param target: 需要发送到的群里的webhook
        :param kwargs: 一些额外的参数，包括secret和is_at_all（是否@所有人）等
        """
        super().__init__(message_body, target)
        self.__secret = kwargs.get('secret')
        self.is_at_all = kwargs.get('is_at_all', False)

    @staticmethod
    def get_sign(timestamp: str, secret: str) -> str:
        """
        如果传入了secret，生成加密后的签名
        :param timestamp: 时间戳
        :param secret: 钉钉机器人的加签密钥
        :return: 签名
        """
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def auth_sign(self) -> None:
        """
        生成sign并传入self.message_body
        :return: None
        """
        if self.__secret:
            _timestamp = str(int(datetime.now().timestamp()))
            sign = self.get_sign(_timestamp, self.__secret)
            self.message_body['timestamp'] = _timestamp
            self.message_body['sign'] = sign

    def add_at_info(self, *at_phone_numbers) -> None:
        """
        修改self.message_body，添加需要@的人的信息
        :param at_phone_numbers: 需要@的的人的手机号码，可添加多个
        :return: None
        """
        if self.message_body["msg_type"] == "interactive":
            if self.is_at_all:
                self.message_body["card"]["elements"][0]["text"]["content"] += "\n<at id=all></at>"
        elif self.message_body["msg_type"] == "text":
            if self.is_at_all:
                self.message_body["content"]["text"] += "<at user_id=\"all\">所有人</at>"

    def send(self) -> dict:
        """
        发送信息
        :return: 钉钉的返回结果
        """
        self.auth_sign()
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url=self.target, headers=headers, data=json.dumps(self.message_body))
        return resp.json()

    def send_text_msg(self, text: str) -> "json string":
        """
        发送简单的文字消息
        :param text: 消息内容
        :return: 钉钉返回结果
        """
        msg_body = {
            "msg_type": "text",
            "content": {
                "text": text
            },
        }
        self.message_body = msg_body
        return self.send()

    def process_on_call(self, on_call_stuff_object) -> None:
        at_phone_number = on_call_stuff_object.stuff_phone_number

    def process_additional_args(self, additional_args):
        at_phone_number = additional_args.get("at")
        at_all = additional_args.get("at_all")
        if at_all:
            self.is_at_all = True
            self.add_at_info()
