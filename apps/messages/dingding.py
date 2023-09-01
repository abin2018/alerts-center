from .base import MessageSendingBase
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse


class DingdingMessageSending(MessageSendingBase):
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
    def get_timestamp_and_sign(secret: str) -> tuple:
        """
        如果传入了secret，生成加密后的时间戳和签名
        :param secret: 钉钉机器人的加签密钥
        :return: 时间戳和签名
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def get_webhook_url(self) -> str:
        """
        将self.get_timestamp_and_sign 生成的timestamp和sign作为参宿和添加到webhook的url中
        :return: webhook的url
        """
        if self.__secret:
            timestamp, sign = self.get_timestamp_and_sign(self.__secret)
            return "{}&timestamp={}&sign={}".format(self.target, timestamp, sign)
        return self.target

    def add_at_info(self, *at_phone_numbers) -> None:
        """
        修改self.message_body，添加需要@的人的信息
        :param at_phone_numbers: 需要@的的人的手机号码，可添加多个
        :return: None
        """
        self.message_body['at'] = {}
        self.message_body['at']["isAtAll"] = self.is_at_all
        if at_phone_numbers:
            self.message_body['at']["atMobiles"] = list(at_phone_numbers)
            if self.message_body["msgtype"] == "markdown":
                for phone_number in at_phone_numbers:
                    self.message_body["markdown"]["text"] += "\n- @{}".format(phone_number)
            elif self.message_body["msgtype"] == "text":
                for phone_number in at_phone_numbers:
                    self.message_body["text"]["content"] += "\n@{}".format(phone_number)

    def send(self) -> dict:
        """
        发送信息
        :return: 钉钉的返回结果
        """
        webhook_url = self.get_webhook_url()
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url=webhook_url, headers=headers, data=json.dumps(self.message_body))
        return resp.json()

    def send_text_msg(self, content: str) -> dict:
        """
        发送简单的文字消息
        :param content: 消息内容
        :return: 钉钉返回结果
        """
        msg_body = {
            "msgtype": "text",
            "text": {
                "content": content
            },
        }
        self.message_body = msg_body
        return self.send()

    def process_on_call(self, on_call_stuff_object) -> None:
        at_phone_number = on_call_stuff_object.stuff_phone_number
        self.add_at_info(at_phone_number)

    def process_additional_args(self, additional_args):
        at_phone_number = additional_args.get("at")
        at_all = additional_args.get("at_all")
        if at_all:
            self.is_at_all = True
            self.add_at_info()
        if at_phone_number:
            at_phone_number_list = [_.strip() for _ in at_phone_number.split(",")]
            self.add_at_info(*at_phone_number_list)
