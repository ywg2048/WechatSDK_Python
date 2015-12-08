#coding=utf-8
import hashlib
import json
from lxml import etree
from config import *
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime
import urllib
import time
from django import template
from django.template import RequestContext,Context 
from django.template.loader import render_to_string,get_template
import re
from django.db import connection
from django.shortcuts import render_to_response
import sys
import os
import requests
from xml.dom import minidom

class QYSDK(object):
    """微信企业号sdk"""
    def __init__(self, token=None, corpid=None, appsecret=None, AESKey=None,access_token=None):
        """
        :param token: 微信 Token
        :param corpid: CorpID
        :param appsecret: App Secret
        :param AESKey: AESKey
        :param access_token: 直接导入的 access_token 值, 该值需要在上一次该类实例化之后手动进行缓存并在此处传入, 如果不传入, 将会在需要时自动重新获取
        
        """
        self.__token = token
        self.__corpid = corpid
        self.__appsecret = appsecret
        self.__AESKey=AESKey
        self.__access_token=access_token
        

        self.__is_parse = False
        self.__message = None

    def check_signature(self, signature, timestamp, nonce):
        """
        验证微信消息真实性
        :param signature: 微信加密签名
        :param timestamp: 时间戳
        :param nonce: 随机数
        :return: 通过验证返回 True, 未通过验证返回 False
        """
        self._check_token()

        if not signature or not timestamp or not nonce:
            return False
        else:
        	return True    
        
    def parse_data(self, data):
        """
        解析微信服务器发送过来的数据并保存类中
        :param data: HTTP Request 的 Body 数据
        :raises ParseError: 解析微信服务器数据错误, 数据不合法
        """
        result = {}
        if type(data) == str:
            data = data.encode('utf-8')
        elif type(data) == str:
            pass
        else:
            raise ParseError()

        try:
            doc = minidom.parseString(data)
        except Exception:
            raise ParseError()

        params = [ele for ele in doc.childNodes[0].childNodes
                  if isinstance(ele, minidom.Element)]

        for param in params:
            if param.childNodes:
                text = param.childNodes[0]
                result[param.tagName] = text.data
        result['raw'] = data
        result['type'] = result.pop('MsgType').lower()

        message_type = MESSAGE_TYPES.get(result['type'], UnknownMessage)
        self.__message = message_type(result)
        self.__is_parse = True

    def get_message(self):
        """
        获取解析好的 WechatMessage 对象
        :return: 解析好的 WechatMessage 对象
        """
        self._check_parse()

        return self.__message            
    def _check_parse(self):
        """
        检查是否成功解析微信服务器传来的数据
        :raises NeedParseError: 需要解析微信服务器传来的数据
        """
        if not self.__is_parse:
            raise NeedParseError()    
    def _check_token(self):
        """
        检查 Token 是否存在
        :raises NeedParamError: Token 参数没有在初始化的时候提供
        """
        if not self.__token:
            raise NeedParamError('Please provide Token parameter in the construction of class.')
    def send_text_messages(self,touser,toparty,totag,agentid,content):
        """
          发送文本消息
        """
        data="""
            {
                "touser": "%s",
                "toparty": "%s",
                "totag": "%s ",
                "msgtype": "text",
                "agentid": "%s",
                "text": {
                    "content": "%s"
                },
                "safe":"0"
            }
        """ % (touser,toparty,totag,agentid,content)
        url=WEIXIN_SUFFIX+"message/send?access_token=%s"% self.__access_token
        
        result=self.post_request(url,data)
        
        return result
    def send_image_messages(self,touser,toparty,totag,agentid,media_id):
        """
          发送图片消息
        """
        data="""
            {
               "touser": "%s",
               "toparty": "%s",
               "totag":"%s",
               "msgtype": "image",
               "agentid": "%s",
               "image": {
                     "media_id": "%s"
                },
                "safe":"0"
             }

        """  %(touser,toparty,totag,agentid,media_id)
        url=WEIXIN_SUFFIX+"message/send?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        return result
    def send_voice_messages(self,touser,toparty,totag,agentid,media_id):
        """
          发送语音消息
        """
        data="""
            {
               "touser": "%s",
               "toparty": "%s",
               "totag":"%s",
               "msgtype": "voice",
               "agentid": "%s",
               "voice": {
                     "media_id": "%s"
                },
                "safe":"0"
             }

        """  %(touser,toparty,totag,agentid,media_id)
        url=WEIXIN_SUFFIX+"message/send?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def send_video_messages(self,touser,toparty,totag,agentid,media_id,title,description):
        """
          发送video消息
        """
        data="""
            {
               "touser": "%s",
               "toparty": "%s",
               "totag":"%s",
               "msgtype": "video",
               "agentid": "%s",
               "video": {
                     "media_id": "%s",
                     "title":"%s",
                     "description":"%s"
                },
                "safe":"0"
             }

        """  %(touser,toparty,totag,agentid,media_id,title,description)
        url=WEIXIN_SUFFIX+"message/send?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def send_news_messages(self,touser,toparty,totag,agentid,articles):
        """
          发送图文消息
        """
        data="""
            {
               "touser": "%s",
               "toparty": "%s",
               "totag":"%s",
               "msgtype": "news",
               "agentid": "%s",
               "news": {
                     "articles":[%s]
                },
                "safe":"0"
             }

        """  %(touser,toparty,totag,agentid,articles)
        url=WEIXIN_SUFFIX+"message/send?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def upload_media(self):
        """
         上传多媒体
        """    
        pass
    def download(self):
        """
          下载多媒体
        """    
        pass
    def department_create(self,name,parentid,order):
        """
         创建部门
          name     部门名称。长度限制为1~64个字符
          parentid 父亲部门id。根部门id为1
          order	   在父部门中的次序。从1开始，数字越大排序越靠后
        """
        data="""
            {
              "name":"%s",
              "parentid":"%s",
              "order":"%s"
            }
        """ % (name,parentid,order) 
        url=WEIXIN_SUFFIX+"department/create?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def department_update(self,departmentid,name,parentid,order):
        """
         更新部门
          id       部门id
          name     部门名称。长度限制为1~64个字符
          parentid 父亲部门id。根部门id为1
          order	   在父部门中的次序。从1开始，数字越大排序越靠后
        """
        data="""
            {
             "id": %s,
             "name": "%s",
             "parentid": "%s",
             "order": "%s"
            }
        """ % (departmentid,name,parentid,order) 
        url=WEIXIN_SUFFIX+"department/update?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def department_delete(self,departmentid):
        """
         删除部门
          id       部门id
          
        """
        url=WEIXIN_SUFFIX+"department/delete?access_token=%s&id=%s"% (self.__access_token,departmentid)
        result=self.get_request(url)
        
        return result
    def department_list(self):
        """
          获取部门列表
          
        """
        url=WEIXIN_SUFFIX+"department/list?access_token=%s"% self.__access_token
        result=self.get_request(url)
        
        return result
    def user_create(self,userid,name,department,position,mobile,email,weixinid,extattr):
        """
        创建成员：
        access_token 是 调用接口凭证
        userid     是  员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
        name       是  成员名称。长度为1~64个字符
        department 否  成员所属部门id列表。注意，每个部门的直属员工上限为1000个
        position   否  职位信息。长度为0~64个字符
        mobile     否  手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
        email      否  邮箱。长度为0~64个字符。企业内必须唯一
        weixinid   否  微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
        extattr    否  扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """ 
        data="""
             {
               "userid": "%s",
               "name": "%s",
               "department": [%s],
               "position": "%s",
               "mobile": "%s",
               "email": "%s",
               "weixinid": "%s",
               "extattr": {"attrs":[%s]} 

             }
            """  % (userid,name,department,position,mobile,email,weixinid,extattr)
        url=WEIXIN_SUFFIX+"user/create?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def user_update(self,userid,name,department,position,mobile,email,weixinid,enable,extattr):
        """
        更新成员：
        access_token 是 调用接口凭证
        userid     是  员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
        name       是  成员名称。长度为1~64个字符
        department 否  成员所属部门id列表。注意，每个部门的直属员工上限为1000个
        position   否  职位信息。长度为0~64个字符
        mobile     否  手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
        email      否  邮箱。长度为0~64个字符。企业内必须唯一
        weixinid   否  微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
        enable     否  启用/禁用成员。1表示启用成员，0表示禁用成员
        extattr    否  扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """ 
        data="""
             {
               "userid": "%s",
               "name": "%s",
               "department": [%s],
               "position": "%s",
               "mobile": "%s",
               "email": "%s",
               "weixinid": "%s",
               "enable":%s,
               "extattr": {"attrs":[%s]} 

             }
            """  % (userid,name,department,position,mobile,email,weixinid,enable,extattr)
        url=WEIXIN_SUFFIX+"user/update?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def user_delete(self,userid):
        """
          删除单个成员
          
        """
        url=WEIXIN_SUFFIX+"user/delete?access_token=%s&userid=%s"% (self.__access_token,userid)
        result=self.get_request(url)
        
        return result 
    def user_batchdelete(self,useridlist):
        """
          批量删除成员
        """
        data="""
             {
             "useridlist":%s
             }
        """ % (useridlist)
        url=WEIXIN_SUFFIX+"user/batchdelete?access_token=%s"% self.__access_token
        result=self.post_request(url,data)
        
        return result
    def user_get(self,userid):
        """
          获取成员的基本信息
        """     
        url=WEIXIN_SUFFIX+"user/get?access_token=%s&userid=%s"%(self.__access_token,userid)
        result=self.get_request(url)
        
        return result
    def user_simplelist(self,departmentid,fetch_child,status):
        """
          获取部门成员
          department_id 是   获取的部门id
          fetch_child   否   1/0：是否递归获取子部门下面的成员
          status        否   0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """     
        url=WEIXIN_SUFFIX+"user/simplelist?access_token=%s&department_id=%s&fetch_child=%s&status=%s" % (self.__access_token,departmentid,fetch_child,status)
        result=self.get_request(url)
        
        return result
    def user_list(self,departmentid,fetch_child,status):
        """
          获取部门成员详情
          department_id 是   获取的部门id
          fetch_child   否   1/0：是否递归获取子部门下面的成员
          status        否   0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """     
        url=WEIXIN_SUFFIX+"user/list?access_token=%s&department_id=%s&fetch_child=%s&status=%s" % (self.__access_token,departmentid,fetch_child,status)
        result=self.get_request(url)
        print(result)
        return result
    def invite_send(self,userid,invite_tips):
        """
        邀请成员关注
        认证号优先使用微信推送邀请关注，如果没有weixinid字段则依次对手机号，
        邮箱绑定的微信进行推送，全部没有匹配则通过邮件邀请关注。 邮箱字段无效则邀请失败。 
        非认证号只通过邮件邀请关注。邮箱字段无效则邀请失败。 已关注以及被禁用用户不允许发起邀请关注请求
        access_token  是   调用接口凭证
        userid        是   用户的userid
        invite_tips   否   推送到微信上的提示语（只有认证号可以使用）。当使用微信推送时，该字段默认为“请关注XXX企业号”，邮件邀请时，该字段无效
        """ 
        data="""
            {
            "userid":"%s",
            "invite_tips":"%s"
            }
        """   % (userid,invite_tips)
        url=WEIXIN_SUFFIX+"invite/send?access_token=%s" % self.__access_token
        result=self.post_request(url,data)
        
        return result
    def menu_create(self,data,agentid):
        """创建菜单
        data数据包示例：
         {
           "button":[
              {
                "type":"click",
                "name":"今日歌曲",
                "key":"V1001_TODAY_MUSIC"
              },
              {
                 "name":"菜单",
                 "sub_button":[
                    {
                      "type":"view",
                      "name":"搜索",
                      "url":"http://www.soso.com/"
                    },
                    {
                      "type":"click",
                      "name":"赞一下我们",
                      "key":"V1001_GOOD"
                    }
                  ]
              }
            ]
          }其他类型见官网
          agentid 应用的id
        """
        url=WEIXIN_SUFFIX+"menu/create?access_token=%s&agentid=%s" % (self.__access_token,agentid)
        result=self.post_request(url,data)
        
        return result
    def menu_delete(self,agentid):
        """
         关闭并删除菜单
         agent id应用的id
        """     
        url=WEIXIN_SUFFIX+"menu/delete?access_token=%s&agentid=%s" % (self.__access_token,agentid)
        result=self.get_request(url)
        
        return result
    def menu_get(self,agentid):
        """
          获取应用的菜单
          agentid 应用的id
        """         
        url=WEIXIN_SUFFIX+"menu/get?access_token=%s&agentid=%s" % (self.__access_token,agentid)
        result=self.get_request(url)
        
        return result
    def OAuth2_link(self,redirect_uri):
    	"""
         构造OAuth2授权链接
         redirect_uri 需要调转的url
    	"""
        url="https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=SCOPE&state=STATE#wechat_redirect" % (self.__corpid,redirect_uri)
        return url
    def OAuth2_get_userinfo(self,code,agentid):
        """
          通过OAuth2授权获取用户userid和设备号
          code 用户确定授权之后会在URL上带有code
          agentid 应用的id 必须要和跳转时候的id一致
        """    
        url=WEIXIN_SUFFIX+"user/getuserinfo?access_token=%s&code=%s&agentid=%s" % (self.__access_token,code,agentid)
        result=self.get_request(url)
        return result
    def get_request(self,url):
        """
        get请求
        """
        result = urllib.request.urlopen(url).read()
        result=json.loads(result.decode("utf-8"))
        return result
    def post_request(self,url,data):
        """
          post请求
        """
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondataasbytes = data.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))

        result=urllib.request.urlopen(req, jsondataasbytes).read()
        result = json.loads(result.decode("utf-8"))

        return result	