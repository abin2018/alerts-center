#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# **********************************************************************
#
# Description: 错误码、自定义异常类
#
# Author: Peter Hu
#
# Created Date:2017/5/4
#
# Copyright (c) ShenZhen Montnets Technology, Inc. All rights reserved.
#
# **********************************************************************


class VoiceErrorCode:
    # 参数类错误-30开头
    # 账号格式不合法
    ERROR_300001 = -300001

    # 密码格式不合法
    ERROR_300002 = -300002

    # IP和端口信息不合法
    ERROR_300003 = -300003

    # IP不合法
    ERROR_300004 = -300004

    # 端口不合法
    ERROR_300005 = -300005

    # 手机号码格式不合法
    ERROR_300006 = -300006

    # 短信内容长度不合法
    ERROR_300007 = -300007

    # 扩展子号不合法
    ERROR_300008 = -300008

    # 流水号不合法
    ERROR_300009 = -300009

    # 密码加密失败
    ERROR_300010 = -300010

    # 业务类型不合法
    ERROR_300011 = -300011

    # exdata不合法
    ERROR_300012 = -300012

    # 发送优先级不合法
    ERROR_300013 = -300013

    # 个性化群发发送条数不在1到100之间
    ERROR_300014 = -300014

    # Message对象为空
    ERROR_300015 = -300015

    # msgId参数为空或者msgId长度不为0
    ERROR_300016 = -300016

    # 账号或者密码错误
    ERROR_300017 = -300017

    # 发送类型错误
    ERROR_300018 = -300018

    # 上行mos为空或者mos集合大于0
    ERROR_300019 = -300019

    # 状态报告rpts为空或者rpts集合大于0
    ERROR_300020 = -300020

    # 请求路径为空
    ERROR_300021 = -300021

    # 是否需要日志设置不合法
    ERROR_300023 = -300023

    # 手机号码超过最大支持数量(1000)
    ERROR_300024 = -300024

    # 短信内容编码失败
    ERROR_300025 = -300025

    # 业务类错误-31开头
    # 单条发送失败
    ERROR_310001 = -310001

    # 相同内容发送失败
    ERROR_310002 = -310002

    # 个性发送失败
    ERROR_310003 = -310003

    # 获取余额失败
    ERROR_310006 = -310006

    # 获取上行失败
    ERROR_310004 = -310004

    # 获取状态报告失败
    ERROR_310005 = -310005

    # 设置账号信息失败
    ERROR_310007 = -310007

    # 账号不存在或者账号不可用
    ERROR_310008 = -310008

    # 无可用的账号
    ERROR_310009 = -310009

    # 设置账号检查线程启动失败
    ERROR_310010 = -310010

    # 设置账号检查线程停止失败
    ERROR_310011 = -310011

    # 设置全局参数失败
    ERROR_310012 = -310012

    # 移除账号失败
    ERROR_310013 = -310013

    # 该账号在账号列表不存在，无需移除
    ERROR_310014 = -310014

    # http请求失败
    ERROR_310099 = -310099

    # 回拔显示的号码不合法
    ERROR_311001 = -311001

    # 模版编号不合法
    ERROR_300026 = -300026

    # 消息类型不合法
    ERROR_300027 = -300027

    # 成功编码
    SUCCESS_CODE = 0

    # 相关超时时间配置
    # 空闲超时判断
    SPARE_TIMEOUT = (25 * 1000)

    # HTTP默认端口
    HTTP_DEFAULT_PORT = 80

    # 需要日志
    STATIC_NEED_LOG = 1

    # 检查多次主IP打印一次日志
    LOG_COUNT = 30


# 错误码转字符串
errorCodeDic = dict()
errorCodeDic[VoiceErrorCode.ERROR_300001] = '账号格式不合法'
errorCodeDic[VoiceErrorCode.ERROR_300002] = '密码格式不合法'
errorCodeDic[VoiceErrorCode.ERROR_300003] = 'IP和端口信息不合法'
errorCodeDic[VoiceErrorCode.ERROR_300004] = 'IP不合法'
errorCodeDic[VoiceErrorCode.ERROR_300005] = '端口不合法'
errorCodeDic[VoiceErrorCode.ERROR_300006] = '手机号码格式不合法'
errorCodeDic[VoiceErrorCode.ERROR_300007] = '短信内容长度不合法'
errorCodeDic[VoiceErrorCode.ERROR_300008] = '扩展子号不合法'
errorCodeDic[VoiceErrorCode.ERROR_300009] = '流水号不合法'
errorCodeDic[VoiceErrorCode.ERROR_300010] = '设置账号检查线程启动失败'
errorCodeDic[VoiceErrorCode.ERROR_300011] = '业务类型不合法'
errorCodeDic[VoiceErrorCode.ERROR_300012] = '扩展数据不合法'
errorCodeDic[VoiceErrorCode.ERROR_300013] = '发送优先级不合法'
errorCodeDic[VoiceErrorCode.ERROR_300014] = '个性化群发发送条数不在0到100之间'
errorCodeDic[VoiceErrorCode.ERROR_300015] = 'Message对象为空'
errorCodeDic[VoiceErrorCode.ERROR_300016] = 'msgId参数为空或者msgId长度不为0'
errorCodeDic[VoiceErrorCode.ERROR_300017] = '账号或者密码错误'
errorCodeDic[VoiceErrorCode.ERROR_300018] = '发送类型错误'
errorCodeDic[VoiceErrorCode.ERROR_300019] = '上行mos为空或者mos集合大于0'
errorCodeDic[VoiceErrorCode.ERROR_300020] = '状态报告rpts为空或者rpts集合大于0'
errorCodeDic[VoiceErrorCode.ERROR_300021] = '请求路径为空'
# 22暂无
errorCodeDic[VoiceErrorCode.ERROR_300023] = '是否需要日志设置不合法'
errorCodeDic[VoiceErrorCode.ERROR_300024] = '手机号码超过最大支持数量'
errorCodeDic[VoiceErrorCode.ERROR_300025] = '短信内容编码失败'
errorCodeDic[VoiceErrorCode.ERROR_300025] = '短信内容编码失败'
errorCodeDic[VoiceErrorCode.ERROR_300025] = '短信内容编码失败'

errorCodeDic[VoiceErrorCode.ERROR_310001] = '单条发送失败'
errorCodeDic[VoiceErrorCode.ERROR_310002] = '相同内容发送失败'
errorCodeDic[VoiceErrorCode.ERROR_310003] = '个性发送失败'
errorCodeDic[VoiceErrorCode.ERROR_310006] = '获取余额失败'
errorCodeDic[VoiceErrorCode.ERROR_310004] = '获取上行失败'
errorCodeDic[VoiceErrorCode.ERROR_310005] = '获取状态报告失败'
errorCodeDic[VoiceErrorCode.ERROR_310007] = '设置账号信息失败'
errorCodeDic[VoiceErrorCode.ERROR_310008] = '账号不存在或者账号不可用'
errorCodeDic[VoiceErrorCode.ERROR_310009] = '无可用的账号'
errorCodeDic[VoiceErrorCode.ERROR_310010] = '设置账号检查线程启动失败'
errorCodeDic[VoiceErrorCode.ERROR_310011] = '设置账号检查线程停止失败'
errorCodeDic[VoiceErrorCode.ERROR_310012] = '设置全局参数失败'
errorCodeDic[VoiceErrorCode.ERROR_310013] = '移除账号失败'
errorCodeDic[VoiceErrorCode.ERROR_310014] = '该账号在账号列表不存在，无需移除'
errorCodeDic[VoiceErrorCode.ERROR_310099] = 'http请求失败'
errorCodeDic[VoiceErrorCode.ERROR_311001] = '回拔显示的号码不合法'


def FORMAT_ERROR_CODE(errorcode):
    return errorCodeDic.get(errorcode, 'Unkown Error Code')


class SmsValueError(Exception):
    def __init__(self, errorcode):
        self.errorcode = errorcode

    def __str__(self):
        return FORMAT_ERROR_CODE(self.errorcode) + '(' + str(self.errorcode) + ')'
