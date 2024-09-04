from flask import Flask, request
import requests
import yaml
import json
import os
import logging
import re
import time

app = Flask(__name__)

#------------Config part-----------------
with open('./resource/application.yml', 'r', encoding='utf-8') as f:
    projects = yaml.load(f.read(), Loader=yaml.FullLoader)

# projects = {
#     """
#     在这里配置kubernetes中的namespace前缀、微信群机器人token、环境地址
#     比如命名空间是blog-crazyphper-com-staging和blog-crazyphper-com-production，那么就：
#     'blog-crazyphper-com':{
#         'token':'AAAAAA-1234-7890-000-123456789000',
#         'staging_url':'https://blog.staging.crazyphper.com',
#         'production_url':'https://blog.crazyphper.com'
#     }
#     """
#     'your-namespace-prefix':{
#         'token':'',
#         'testing_url':''
#     }
# }

#------------Config part end-----------------

API = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
class WebhookMessage:
    def __init__(self):
        self.EventMeta = {}
        self.Text = ''
        self.Project = [i for i in projects.values()][0]
        self.Time = ''

    def __str__(self):
        return self.toString()

    def toString(self):
        "返回需要发送的文本"
        #根据namespace后缀判断环境
        env = self.EventMeta['namespace'].split('-')[-1]
        result = "创建" if self.EventMeta['reason'] != 'created' else "更新"
        return ('# <font color=\"info\">'+self.getProgramName()+'</font>程序已部署 \n '
                '> 运行环境：['+env.capitalize()+']('+self.Project[env+'_url']+') \n '
                '> 部署结果：<font color=\"comment\">'+result+'</font>')

    def getProgramName(self):
        fullName = self.EventMeta['name'].split('/')[-1]
        return fullName.split('-')[0]


def sendMessage(message):
    "推送webhook消息"
    if message['eventmeta']['kind'] == 'pod' and message['eventmeta']['reason'] != 'deleted':
        for namespace in projects:
            if re.match(namespace,message['eventmeta']['namespace']):
                playground = WebhookMessage()
                playground.Time = message['time']
                playground.Text = message['text']
                playground.EventMeta = message['eventmeta']
                playground.Project = projects[namespace]
                headers = {'Content-Type': 'application/json;charset=utf-8'}
                body = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": playground.toString()
                    }
                }
                webhook = API+projects[namespace]['token']
                time.sleep(5)
                requests.post(webhook, json.dumps(body), headers=headers)
                logging.warning("==========发送成功==========")


@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'GET':
        return ('wow,"GET"? realy?',200,None)
    else:
        message = json.loads(request.data)
        sendMessage(message)
        return ('send success', 200, None)

if __name__ == '__main__':
    # 打印运行配置
    print(app.config)
    app.run(port=8080,host="0.0.0.0")
