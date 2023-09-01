import re
import IPy


def ip_string_parser(ip_string: str) -> list:
    """
    :param ip_string: ip字符串
    :return: ip列表
    支持处理如下IP字符串
    # 1.0.0.0.0
    # 2.192.168.1.1
    # 3.192.168.1.1,192.168.1.2,192.168.1.3
    # 4.192.168.1.1-5
    # 5.192.168.1.1/32
    不严谨，因为没有对返回的IP进行校验!!!
    """
    reg_ipaddr = r'^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.' \
                 r'(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$'
    ip_string_split = [ip.strip() for ip in ip_string.split(',')]
    ip_list = []
    for _ip_string in ip_string_split:
        if ',' in _ip_string:
            ip_range = [ip.strip() for ip in _ip_string.split(',')]
            ip_list += ip_range
        elif '-' in _ip_string:
            _ip, _end = [ip.strip() for ip in _ip_string.split('-')]
            prefix = '.'.join(_ip.split('.')[:3])
            start = int(_ip.split('.')[-1])
            end = int(_end)
            if end > 255:
                end = 255
            ip_list += [prefix + '.' + str(s) for s in list(range(start, end + 1))]
        elif '/' in _ip_string:
            try:
                ip_list += [i.__str__() for i in IPy.IP(_ip_string)]
            except Exception as e:
                print(e)
        elif '|' in _ip_string:
            prefix = '.'.join(_ip_string.split('.')[:3])
            _ip_tag = _ip_string.split('.')[-1]
            ip_list += [prefix + '.' + s for s in _ip_tag.split('|') if s]
        elif re.match(reg_ipaddr, _ip_string):
            ip_list.append(_ip_string)
    return ip_list


def trans_camel_case(var_string):
    var_string_list = []
    for letter in var_string:
        if letter.isupper():
            var_string_list.append('_')
            var_string_list.append(letter.lower())
        else:
            var_string_list.append(letter)
    return ''.join(var_string_list)
