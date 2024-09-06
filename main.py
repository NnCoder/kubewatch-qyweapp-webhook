import requests
import yaml
import json
import logging
from kubernetes import client, config, watch


# ------------Config part-----------------
with open('./resource/application.yml', 'r', encoding='utf-8') as f:
    global projects
    projects = yaml.load(f.read(), Loader=yaml.FullLoader)
# projects = {
#     """
#     在这里配置kubernetes中的namespace前缀、微信群机器人token、环境地址
#     比如命名空间是blog-crazyphper-com-staging和blog-crazyphper-com-production，那么就：
#
#     """
#     'namespace':{
#         'token':'',
#         'testing_url':''
#     }
# }

#------------Config part end-----------------

API = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
PODS = {}
PENDING_TEXT = '''CD部署任务通知⏳
>命名空间：<font color="info">{namespace}</font>
>环境：<font color="info">{env}</font>
>Pod名称：<font color="info">{pod_name}</font>
>镜像版本：<font color="info">{image_tag}</font>
>任务状态：<font color="warning">部署中...</font>'''

RUNNING_TEXT = '''CD部署任务通知✅
>命名空间：<font color="info">{namespace}</font>
>环境：<font color="info">{env}</font>
>Pod名称：<font color="info">{pod_name}</font>
>镜像版本：<font color="info">{image_tag}</font>
>任务状态：<font color="info">已部署</font>'''
def send_message(namespace, pod_name: str, image_tag, is_pending):
    "推送webhook消息"
    global projects
    #判断是否pending状态也通知
    if is_pending and not projects.get('notifyPending', False):
       return
    #判断是否在忽略的pod内
    ignore_pods = projects.get('ignorePods', [])
    for pod in ignore_pods:
        if pod_name.index(pod) != -1:
            return

    text = PENDING_TEXT if is_pending else RUNNING_TEXT
    text = text.format(namespace=namespace, env=projects['env'], pod_name=pod_name, image_tag=image_tag)
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    body = {
        "msgtype": "markdown",
        "markdown": {
            "content": text
        }
    }
    if projects['dryRun']:
        print(json.dumps(body))
    else:
        webhook = API+projects['token']
        requests.post(webhook, json.dumps(body), headers=headers)
        logging.info("==========发送成功==========")

def pods():
    global projects
    v1 = client.CoreV1Api()
    w = watch.Watch()
    client_watch = w.stream(v1.list_namespaced_pod, namespace=projects['namespace'])
    for event in client_watch:
        deal_pod_event(event)


def deal_pod_event(event):
    # Event: ADDED Pod blog-crazyphper-com-74c58d9d4d-dk5n9 101.x0x.3x.4x Running
    namespace = event['object'].metadata.namespace
    containers = event['object'].spec.containers
    # 获取镜像名及版本
    image_tag = ''
    for container in containers:
        if container.name != 'istio-proxy':
            # 截取最后一个  /  后的字符串
            image_tag = container.image.split('/')[-1]

    # 获取容器是否启动成功
    ready_status = ''
    conditions = event['object'].status.conditions
    # 修复conditions为NoneType问题
    if conditions is not None:
        for condition in conditions:
            if condition.type == 'Ready':
                ready_status = condition.status
    pod_name = event['object'].metadata.name
    pod_status_phase = event['object'].status.phase
    # The type of event such as "ADDED", "DELETED"
    event_type = event['type']
    if event_type == 'ADDED':
        PODS.setdefault(pod_name, pod_status_phase)
        # 如果在部署中，提示在部署
        if pod_status_phase == 'Pending':
            send_message(namespace=namespace, pod_name=pod_name, image_tag=image_tag, is_pending=True)
    if event_type == 'MODIFIED':
        his_pod_status = PODS.get(pod_name)
        if his_pod_status is not None and his_pod_status == 'Pending':
            if ready_status == 'True':
                PODS[pod_name] = pod_status_phase
                #从创建态到Ready态 - 发送消息
                send_message(namespace=namespace, pod_name=pod_name, image_tag=image_tag, is_pending=False)
    if event_type == 'DELETED':
        PODS.pop(pod_name)
    print("Event: %s %s %s %s %s, image_tag: %s, ready_status: %s" % (
        event_type, event['object'].kind, pod_name, event['object'].spec.node_name,
        event['object'].status.phase, image_tag, ready_status))

    # sendMessage(event)
if __name__ == '__main__':
    config.load_incluster_config()
    pods()


