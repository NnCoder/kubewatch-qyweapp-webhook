# kubewatch-qyweapp-webhook

这是一个可以让kubewatch 推送webhook给 **企业微信群机器人** 的python3脚本。

![example](https://www.crazyphper.com/tools/qywechat-demo.png)

## 特性

- 支持kubewatch接收到POD状态变更为`created`和`updated`时，进行企业微信群机器人markdown消息发送

##  文件目录介绍

```shell
.
├── README.md                       # 本文件
├── Dockerfile                      # kubernetes 服务部署配置脚本
├── deployment.yaml                 # Dockerfile
├── requirements.txt                # 所需资源文本
├── main.py                         # 主运行程序脚本
```

## 使用方法

### 1.在main.py中指定kubernetes命名空间

kubernetes的namespaces应该具有命名规范，比如一个叫做`趣味畅玩`的游戏项目，有验收环境(staging)和正式生产环境(production)，那么namespaces可以是`fun-game-staging`和`fun-game-production`。

> 识别环境字符串所使用的是`string.split('-')[-1]`

这样做的好处是脚本能够识别出各个环境的演示网址，并拼接在markdown中进行企业微信机器人消息推送。

接下来请修改application.yml变量：
```python
'blog-crazyphper-com':
    'token':'AAAAAA-1234-7890-000-123456789000'
    'staging_url':'https://blog.staging.crazyphper.com'
    'production_url':'https://blog.crazyphper.com
```


### 2. 部署服务

```shell

docker build -t webhook/qyweapp-kubewatch:latest . 

docker push webhook/qyweapp-kubewatch:latest #建议推送到自己的私有镜像中心

vim deployment.yaml #请先修改脚本中的镜像地址

kubectl  apply -f deployment.yaml

```

> M1芯片必须使用[docker buildx build](https://betterprogramming.pub/how-to-actually-deploy-docker-images-built-on-a-m1-macs-with-apple-silicon-a35e39318e97) 和参数 `--platforms linux/amd64`

### 3.测试运行效果

测试用kube-watch 格式JSON

```json
{"eventmeta": {"kind": "pod", "name": "project-example-com-staging/backend-xxxx-yyy", "namespace": "project-example-com-staging", "reason": "created"}, "text": "A `pod` in namespace `project-example-com-staging` has been `created`:\n`project-example-com-staging/backend-xxxx-yyy`", "time": "2021-02-26T08: 12: 08.758617965Z"}
```

使用curl发送：
```shell
curl -H "Content-Type: application/json" -X POST -d '{"eventmeta": {"kind": "pod", "name": "project-example-com-staging/backend-xxxx-yyy", "namespace": "project-example-com-staging", "reason": "created"}, "text": "A `pod` in namespace `project-example-com-staging` has been `created`:\n`project-example-com-staging/backend-xxxx-yyy`", "time": "2021-02-26T08: 12: 08.758617965Z"}' "http://wechat-webhook:8080"
```

## 修改markdown内容

参考[企业微信机器人配置说明](https://developer.work.weixin.qq.com/document/path/91770)

## 调整kube-watch内容

参考[Go webhook](https://github.com/bitnami-labs/kubewatch/blob/master/pkg/handlers/webhook/webhook.go)和[代码](https://github.com/bitnami-labs/kubewatch/blob/master/pkg/handlers/webhook/webhook.go)

## 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
