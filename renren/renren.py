#-*-coding:utf-8-*-

import requests
import json
import re
import random
import pickle
import feed
from urllib.parse import urlparse, parse_qsl
from ntype import NTYPES
from encrypt import encryptString

class RenRen:

    def __init__(self, email=None, pwd=None):
        self.session = requests.Session()
        self.token = {}

        if email and pwd:
            self.login(email, pwd)

    def loginByCookie(self, cookie_path):
        self.session.cookies = pickle.loads(open(cookie_path, 'rb').read())
        return self.getToken()

    def saveCookie(self, cookie_path):
        open(cookie_path, 'wb').write(pickle.dumps(self.session.cookies))

    def login(self, email, pwd):
        key = self.getEncryptKey()
        data = {
            'email': email,
            'origURL': 'http://www.renren.com/home',
            'icode': '',
            'domain': 'renren.com',
            'key_id': 1,
            'captcha_type': 'web_login',
            'password': encryptString(key['e'], key['n'], pwd) if key['isEncrypt'] else pwd,
            'rkey': key['rkey']
        }
        url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
        r = self.post(url, data)
        result = r.json()
        if result['code']:
            print('login successfully')
            self.email = email
            r = self.get(result['homeUrl'])
            self.getToken(r.text)
        else:
            print('login error', r.text)


    def getEncryptKey(self):
        r = requests.get('http://login.renren.com/ajax/getEncryptKey')
        return r.json()

    def getToken(self, html=''):
        p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

        if not html:
            r = self.get('http://www.renren.com')
            html = r.text

        result = p.search(html)
        self.token = {
            'requestToken': result.group(1),
            '_rtk': result.group(2)
        }

    def request(self, url, method, data={}):
        if data:
            data.update(self.token)
        if method == 'get':
            return self.session.get(url, data=data)
        elif method == 'post':
            return self.session.post(url, data=data)

    def get(self, url, data={}):
        return self.request(url, 'get', data)

    def post(self, url, data={}):
        return self.request(url, 'post', data)

    def getUserInfo(self):
        r = self.get('http://notify.renren.com/wpi/getonlinecount.do')
        return r.json()

    def get_feed(self, page = 0):
        r = self.get('http://www.renren.com/feedretrieve3.do?begin=' + str(page) + '&limit=50&p=0')
        r.raise_for_status()
        f = feed.parse_feed_v3(r.text)
        return f
        
    def getNotifications(self):
        url = 'http://notify.renren.com/rmessage/get?getbybigtype=1&bigtype=1&limit=999&begin=0&view=16'
        r = self.get(url)
        r.raise_for_status()
        return r.json()

    def getDoings(self, uid, page=0):
        url = 'http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=%d' % (str(uid), page)
        r = self.get(url)
        return r.json()['doingArray']

    def getDoingById(self, owner_id, doing_id):
        doings = self.getDoings(owner_id)
        doing = filter(lambda doing: doing['id'] == doing_id, doings)
        return doing[0] if doing else None

    def getDoingComments(self, owner_id, doing_id):
        url = 'http://status.renren.com/feedcommentretrieve.do'
        r = self.post(url, {
            'doingId': doing_id,
            'source': doing_id,
            'owner': owner_id,
            't': 3
        })

        return r.json()['replyList']

    def getCommentById(self, owner_id, doing_id, comment_id):
        comments = self.getDoingComments(owner_id, doing_id)
        comment = filter(lambda comment: comment['id'] == comment_id, comments)
        return comment[0] if comment else None

    def addComment(self, data):
        url = 'http://status.renren.com/feedcommentreply.do'
        #url = 'http://page.renren.com/doing/reply'

        payloads = {
            't': 3,
            'rpLayer': 0,
            'source': data['doing_id'],
            'owner': data['owner_id'],
            'c': data['message']
        }

        if data.get('reply_id', None):
            payloads.update({
                'rpLayer': 1,
                'replyTo': data['author_id'], 
                'replyName': data['author_name'],
                'secondaryReplyId': data['reply_id'],
                'c': '回复%s：%s' % (data['author_name'].encode('utf-8'), data['message'])
            })

        print(self.email, 'going to send a comment: ', payloads['c'])

        r = self.post(url, payloads)
        r.raise_for_status()

        print('comment sent', r.json())
        return r.json()

if __name__ == '__main__':
    renren = RenRen()
    renren.login('email', 'password')
    #renren.loginByCookie('cookie.txt')
    info = renren.getUserInfo()
    print('hello', info['hostname'])
    print(renren.getNotifications())
