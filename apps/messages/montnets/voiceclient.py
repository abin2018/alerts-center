#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# **********************************************************************
#
# Description: 云文本短信客户端模块
#
# Author: Peter Hu
#
# Created Date:2017/5/10
#
# Copyright (c) ShenZhen Montnets Technology,, Inc. All rights reserved.
#
# **********************************************************************

import time
import json
import traceback
import requests
import os
from . import voicemessage
from .voiceexception import *


MONTNETS_API_USERID = os.environ.get('MONTNETS_API_USERID')
MONTNETS_API_PWD = os.environ.get('MONTNETS_API_PWD')
MONTNETS_API_URL = os.environ.get('MONTNETS_API_URL')
MONTNETS_API_TMPLID = os.environ.get('MONTNETS_API_TMPLID')

# 语音短信发送客户端
class VoiceClient():
    def __init__(self, mobile):
        self._userid = MONTNETS_API_USERID  # 发送者帐号
        self._pwd = MONTNETS_API_PWD  # 发送者帐号的密码
        self._url = MONTNETS_API_URL  # 请前往您的控制台获取请求域名(IP)或联系梦网客服进行获取
        self._mobile = mobile

    @property
    def userid(self):
        return self._userid

    @property
    def pwd(self):
        return self._pwd

    @property
    def url(self):
        return self._url

    # http post
    def postVoiceMessage(self, message):
        fullurl = self.url + message.apiname
        try:
            r = None
            body = message.toJson()
            timeout = (5, 30)

            headers = {'Content-Type': 'application/json', 'Connection': 'Close'}
            # 短连接请求
            r = requests.post(fullurl, data=body, headers=headers, timeout=timeout)

            r.encoding = 'utf-8'
            debugStr = '\n[------------------------------------------------------------\n' + \
                       'http url:' + fullurl + '\n' + \
                       'headers:' + headers.__str__() + '\n' + \
                       body + '\n' + \
                       'status code:' + str(r.status_code) + '\n' + \
                       r.text + \
                       '\n-------------------------------------------------------------]\n'
            # print debugStr

            # http请求失败
            if (r.status_code != requests.codes.ok):
                return message.makeupRet(VoiceErrorCode.ERROR_310099)

            # 请求成功,解析服务器返回的json数据,
            rTest = json.loads(r.text)
            return rTest
        except SmsValueError as v:
            return message.makeupRet(v.errorcode)
        except requests.RequestException as e:
            print(traceback.format_exc().__str__())
            return message.makeupRet(VoiceErrorCode.ERROR_310099)
        except Exception as e:
            print(traceback.format_exc().__str__())
            return message.makeupRet(VoiceErrorCode.ERROR_310099)

    # 模板发送(语音)
    def voiceTemplateSend(self):
        message = voicemessage.VoiceMessage()
        # 发送者帐号
        message.userid = self.userid
        # 密码
        message.pwd = self.pwd
        # 接收方手机号码
        message.mobile = self._mobile

        #
        # 语音内容验证码4到8位字符，并且只能是数字或者字母不区分大小写
        #
        verificationCode = time.strftime("%H%M%S", time.localtime())
        # message.content = verificationCode

        #
        # 回拨显示的号码：目前需要备案后才能支持使用，如果没有备案将会返回错误码 -401094（显示号码不合法）
        #
        message.exno = ''  # 不需要就填空

        # 用户自定义流水编号：该条短信在您业务系统内的ID，比如订单号或者短信发送记录的流水号。填写后发送状态返回值内将包含这个ID。
        # 最大可支持64位的ASCII字符串：字母、数字、下划线、减号，如不需要则不用提交此字段或填空
        message.custid = 'b3d0a2783d31b21b8573'

        #
        # 语音模版编号：
        # 当msgtype为1时，语音模板编号为非必须项，
        # 当msgtype为3时，语音模板编号为必填项
        #
        message.tmplid = MONTNETS_API_TMPLID

        #
        # 消息类型：
        # 1：语音验证码
        # 3：语音通知：只有当显号为12590时，实际发出的消息类型仍为语音验证码，并且使用梦网自带的语音模板发送语音验证码，其他显号下仍然使用语音模板编号对应的模板发送语音通知。
        #
        message.msgtype = '3'

        ret = self.postVoiceMessage(message)
        return ret
        # print 'voiceTemplateSend:', ret

    # 获取状态报告(语音)
    def getVoiceRpt(self):
        message = voicemessage.VoiceRpt()
        # 发送者帐号
        message.userid = self.userid
        # 密码
        message.pwd = self.pwd
        message.retsize = 500  # 最大值填500

        ret = self.postVoiceMessage(message)
        return ret
        print('getVoiceRpt:', ret)

    # 查询剩余条数(语音)
    def getVoiceRemains(self):
        message = voicemessage.VoiceBalanceMessage()
        # 发送者帐号
        message.userid = self.userid
        # 密码
        message.pwd = self.pwd

        ret = self.postVoiceMessage(message)
        print('getVoiceRemains:', ret)
