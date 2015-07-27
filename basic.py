# -*- coding=utf-8 -*-
# Created Time: 2015年07月23日 星期四 11时45分03秒
# File Name: basic.py

from __future__ import print_function

import json
import time
import string
import random
import hashlib
import requests
import xml.etree.ElementTree as ET


class WechatPay(object):
    '''
    微信支付类
    '''
    def __init__(self, mch_id, wxappid, key, cert_path, key_path, sign=None):
        self._mch_id = mch_id
        self._wxappid = wxappid
        self._key = key
        self._cert_path = cert_path
        self._key_path = key_path
        self._sign = sign

    def arraytoxml(self, arr):
        '''array转xml'''
        xml = ["<xml>"]
        for k, v in arr.iteritems():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v.encode('utf-8')))
        xml.append("</xml>")
        return "\n".join(xml)

    def xmltoarray(self, xml):
        '''xml转array'''
        array_data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    def _formatBizQueryParaMap(self, paraMap, urlencode):
        '''格式化参数，签名过程需要使用'''
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = urllib.quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v.encode('utf-8')))
        return "&".join(buff)

    def get_sign(self, obj):
        '''生成签名'''
        s = self._formatBizQueryParaMap(obj, False)
        s = "{0}&key={1}".format(s, self._key)
        s = hashlib.md5(s).hexdigest()
        self._sign = s.upper()
        return self._sign

    def generate_noncestr(self, length=32):
        self._nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
        return self._nonce_str

    def cash_redpack(self, mch_billno, send_name, nick_name, re_openid, total_amount, wishing, client_ip, act_name, remark, logo_imgurl=None, sub_mch_id=None):
        '''普通红包'''
        data  = {
            'mch_billno': mch_billno,
            'send_name': send_name,
            'nick_name': nick_name,
            're_openid': re_openid,
            'total_amount': str(total_amount),
            'total_num': '1',
            'wishing': wishing,
            'client_ip': client_ip,
            'act_name': act_name,
            'remark': remark,
            'max_value': str(total_amount),
            'min_value': str(total_amount),
            'wxappid': self._wxappid,
        }
        if logo_imgurl:
            data['logo_imgurl'] = logo_imgurl
        if sub_mch_id:
            data['sub_mch_id'] = sub_mch_id

        return self._post(
            url="https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack",
            data=data
        )

    def fission_redpack(self, mch_billno, send_name, re_openid, total_amount, total_num, wishing, act_name, remark, amt_type='ALL_RAND', amt_list=[]):
        data = {
            'mch_billno': mch_billno,
            'wxappid': self._wxappid,
            'send_name': send_name,
            're_openid': re_openid,
            'total_amount': str(total_amount),
            'total_num': str(total_num),
            'amt_type': amt_type,
            'wishing': wishing,
            'act_name': act_name,
            'remark': remark,
        }
        return self._post(
            url="https://api.mch.weixin.qq.com/mmpaymkttransfers/sendgroupredpack",
            data=data
        )

    def query_redpack(self, mch_billno):
        '''红包查询'''
        data = {
            'mch_billno': mch_billno,
            'bill_type': 'MCHT',
            'appid': self._wxappid,
        }
        return self._post(
            url="https://api.mch.weixin.qq.com/mmpaymkttransfers/gethbinfo",
            data=data
        )

    def _request(self, method, url, **kwargs):
        self.generate_noncestr()
        kwargs['data'].update(
            {
                'mch_id': self._mch_id,
                'nonce_str': self._nonce_str,
            }
        )
        self.get_sign(kwargs['data'])
        kwargs['data'].update(
            {
                'key': self._key,
                'sign': self._sign,
            }
        )
        data = self.arraytoxml(kwargs['data'])
        print(data)
        r = requests.request(
            method=method,
            url=url,
            data=data,
            cert=(self._cert_path, self._key_path)
        )
        # return self.xmltoarray(r.text.encode('utf-8'))
        return r.text

    def _post(self, url, **kwargs):
        return self._request(
            method='post',
            url=url,
            **kwargs
        )

    def _get(self, url, **kwargs):
        return self._request(
            method='get',
            url=url,
            **kwargs
        )
