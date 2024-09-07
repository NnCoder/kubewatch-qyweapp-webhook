# kubewatch-qyweapp-webhook

这是一个利用kubernetes-api监听到POD部署状态 推送给 **企业微信群机器人** 的python3脚本。

![example](https://www.crazyphper.com/tools/qywechat-demo.png)

## 特性

- 使用kubernetes-api监听到POD部署状态，进行企业微信群机器人markdown消息发送

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
```yaml
namespace: blog-crazyphper-com
token: AAAAAA-1234-7890-000-123456789000
env: test
dryRun: true
notifyPending: true
ignorePods:
  - 'some-pod'
```


### 2. 部署服务

```shell

docker build -t tools/kubewatch-qyweapp:latest . 

docker push tools/kubewatch-qyweapp:latest #建议推送到自己的私有镜像中心

vim deployment.yaml #请先修改脚本中的镜像地址

kubectl  apply -f deployment.yaml

```
Or 使用github actions部署

> M1芯片必须使用[docker buildx build](https://betterprogramming.pub/how-to-actually-deploy-docker-images-built-on-a-m1-macs-with-apple-silicon-a35e39318e97) 和参数 `--platforms linux/amd64`


## 修改markdown内容

## 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
