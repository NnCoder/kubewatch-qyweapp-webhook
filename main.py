import requests
import yaml
import json
import logging
import re
import time
from kubernetes import client, config, watch


# ------------Config part-----------------
with open('./resource/application.yml', 'r', encoding='utf-8') as f:
    global projects
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
        result = "创建" if self.EventMeta['reason'] != 'created' else "更新"
        return '# <font color=\"info\">'+self.getProgramName()+ '</font>程序已' + result

    def getProgramName(self):
        fullName = self.EventMeta['name'].split('/')[-1]
        return fullName


def sendMessage(message):
    "推送webhook消息"
    global projects
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
                time.sleep(1)
                requests.post(webhook, json.dumps(body), headers=headers)
                logging.info("==========发送成功==========")

def k8sPod():
    v1 = client.CoreV1Api()
    for ns in projects:
        logging.info("namespace: %s" % ns)
        ret = v1.list_namespaced_pod(ns)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            print(json.dumps(i))

if __name__ == '__main__':
    config.load_incluster_config()
    k8sPod()

