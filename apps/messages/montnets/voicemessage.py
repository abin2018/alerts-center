#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# **********************************************************************
#
# Description: 云语音短信包实体
#
# Author: Peter Hu
#
# Created Date:2017/4/26
#
# Copyright (c) ShenZhen Montnets Technology,, Inc. All rights reserved.
#
# **********************************************************************

import hashlib
import json
import time
import urllib
import os

MONTNETS_API_USERID = os.environ.get('MONTNETS_API_USERID')
MONTNETS_API_PWD = os.environ.get('MONTNETS_API_PWD')
MONTNETS_API_URL = os.environ.get('MONTNETS_API_URL')


class VoiceBaseMessage():
    def __init__(self, apiName):
        self._userid = MONTNETS_API_USERID  # 发送者帐号
        self._pwd = MONTNETS_API_PWD  # 发送者帐号的密码
        self._url = MONTNETS_API_URL  # 请前往您的控制台获取请求域名(IP)或联系梦网客服进行获取
        self._apiname = apiName

    @property
    def fullurl(self):
        return self._fullurl

    @fullurl.setter
    def fullurl(self, fullurl):
        self._fullurl = fullurl

    @property
    def userid(self):
        return self._userid

    @userid.setter
    def userid(self, userid):
        self._userid = userid

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, pwd):
        self._pwd = pwd

    @property
    def apiname(self):
        return self._apiname

    def md5pwd(self, timestamp):
        # md5(userid + '00000000' + password + timestamp)
        tempPwd = self.userid.upper() + '00000000' + self.pwd + timestamp
        md5 = hashlib.md5()
        md5.update(tempPwd.encode('utf-8'))
        md5Pwd = md5.hexdigest()
        return md5Pwd

    def content2gbk(self, content):
        # gdb编码短信业务内容
        gbkcontent = content.encode(encoding='gbk')
        # python3.3:
        # gbkcontent = urllib.parse.urlencode({'':gbkcontent})
        # python2.7:
        gbkcontent = urllib.parse.urlencode({'': gbkcontent})
        gbkcontent = gbkcontent.split("=")[1]
        return gbkcontent

    def toJson(self):  # 虚函数，返回http body
        pass

    def makeupRet(self, errorCode):  # 虚函数，根据错误码构造返回值
        pass


# 语音短信包
class VoiceMessage(VoiceBaseMessage):
    def __init__(self):
        VoiceBaseMessage.__init__(self, 'template_send')
        self._content = u''  # 文本内容,unicode明文
        self._timestamp = ''
        self._svrtype = ''
        self._exno = '',
        self._custid = ''
        self._exdata = ''

    @property
    def mobile(self):
        return self._mobile

    @mobile.setter
    def mobile(self, mobile):
        self._mobile = mobile
        if self._mobile is None:
            self._mobile = ''

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content
        if self._content is None:
            self._content = u''

    @property
    def exno(self):
        return self._exno

    @exno.setter
    def exno(self, exno):
        self._exno = exno
        if self._exno is None:
            self._exno = ''

    @property
    def custid(self):
        return self._custid

    @custid.setter
    def custid(self, custid):
        self._custid = custid
        if self._custid is None:
            self._custid = ''

    @property
    def tmplid(self):
        return self._tmplid

    @tmplid.setter
    def tmplid(self, tmplid):
        self._tmplid = tmplid
        if self._tmplid is None:
            self._tmplid = ''

    @property
    def msgtype(self):
        return self._msgtype

    @msgtype.setter
    def msgtype(self, msgtype):
        self._msgtype = msgtype
        if self._msgtype is None:
            self._msgtype = ''

    # 根据错误码构造返回值
    def makeupRet(self, errorCode):
        assert isinstance(errorCode, int)
        ret = {
            'result': str(errorCode),
            'msgid': '0',
            'custid': ''
        }
        return ret

    # http body
    def toJson(self):

        timestamp = time.strftime("%m%d%H%M%S", time.localtime())  # MMDDHHMMSS
        md5pwd = self.md5pwd(timestamp)
        gbkcontent = self.content2gbk(self.content.strip())

        payload = {
            'userid': self.userid.upper(),
            'pwd': md5pwd,
            'mobile': self.mobile,
            'content': gbkcontent,
            'timestamp': timestamp,
            'exno': self.exno,
            'custid': self.custid,
            'tmplid': self.tmplid,
            'msgtype': self.msgtype
        }

        body = json.dumps(payload, sort_keys=False)
        return body


# 获取状态报告接口
class VoiceRpt(VoiceMessage):
    def __init__(self):
        VoiceBaseMessage.__init__(self, 'get_rpt')
        self._retsize = 500  # 每次请求想要获取的上行最大条数,默认100条

    @property
    def retsize(self):
        return self._retsize

    @retsize.setter
    def retsize(self, retsize):
        # 每次请求想要获取的上行最大条数。最大500,超过500按500返回。小于等于0或不填时，系统返回默认条数，默认500条
        if retsize is not None:
            assert isinstance(retsize, int)
            self._retsize = retsize
            if retsize > 500:
                self._retsize = 500
            if retsize <= 0:
                self._retsize = 500

                # 根据错误码构造返回值

    def makeupRet(self, errorCode):
        assert isinstance(errorCode, int)
        ret = {
            'result': str(errorCode),
            'rpts': []
        }
        return ret

    def toJson(self):

        timestamp = time.strftime("%m%d%H%M%S", time.localtime())  # MMDDHHMMSS
        md5pwd = self.md5pwd(timestamp)

        payload = {
            'userid': self.userid.upper(),
            'pwd': md5pwd,
            'timestamp': timestamp,
            'retsize': self.retsize
        }

        body = json.dumps(payload, sort_keys=False)
        return body


# 查询余额包
class VoiceBalanceMessage(VoiceMessage):
    def __init__(self):
        VoiceBaseMessage.__init__(self, 'get_balance')

    # 根据错误码构造返回值
    def makeupRet(self, errorCode):
        assert isinstance(errorCode, int)
        ret = {
            'result': str(errorCode),
            'chargetype': '0',
            'balance': '0',
            'money': '0'
        }
        return ret

    # 组包,仅http body
    def toJson(self):
        # md5(userid + '00000000' + password + timestamp)
        timestamp = time.strftime("%m%d%H%M%S", time.localtime())  # MMDDHHMMSS
        md5pwd = self.md5pwd(timestamp)

        # http body
        payload = {
            'userid': self.userid.upper(),
            'pwd': md5pwd,
            'timestamp': timestamp,
        }

        body = json.dumps(payload, sort_keys=False)
        return body
