# 12306验证码识别服务器

[![Uptime Robot status](https://img.shields.io/uptimerobot/status/m783635180-ab3d4772f147c2a3b92f8fe5)](https://stats.uptimerobot.com/oyKyLhjJQ/783635180) [![Uptime Robot ratio (30 days)](https://img.shields.io/uptimerobot/ratio/m783635180-ab3d4772f147c2a3b92f8fe5)](https://stats.uptimerobot.com/oyKyLhjJQ/783635180) [![Build Status](https://travis-ci.org/YinAoXiong/12306_code_server.svg?branch=master)](https://travis-ci.org/YinAoXiong/12306_code_server) [![Docker Pulls](https://img.shields.io/docker/pulls/yinaoxiong/12306_code_server)](https://hub.docker.com/r/yinaoxiong/12306_code_server)

该项目用于构建自托管的12306验证码识别服务器，本项目的全部模型和部分代码来自于此项目 [easy12306](https://github.com/zhaipro/easy12306)，使用该项目构建的api符合 [12306购票小助手](https://github.com/testerSunshine/12306)云打码格式可以直接调用。

提供一个部署好的线上版本, [https://12306.yinaoxiong.cn](https://12306.yinaoxiong.cn/),部署在腾讯云1核1G的学生机上不保证可用性,服务状态可以通过 [https://stats.uptimerobot.com/oyKyLhjJQ/783635180](https://stats.uptimerobot.com/oyKyLhjJQ/783635180)查看.



## 接口规范

### 请求

- Method: **POST**
- URL:  ```/verify/base64/```
- Headers: Content-Type: application/x-www-form-urlencoded
- Body: 
  imageFile=>Base64 encoding of the image

### 响应

- Headers：Content-Type:application/json
- Body：

```json
{
    "code": 0,
    "data": [
        "1",  //答案图片的编号数组
        "3"
    ],
    "massage": "识别成功"
}
{
    "code": 1,
    "data": [
    ],
    "massage": "识别失败"
}
```



## python版本支持

- [x] 3.5-3.7

## 平台支持

- [x] amd64
- [x] arm64v8
- [x] arm32v7

其中arm平台建议通过docker运行

## 部署

### docker部署(推荐)

使用docker可以使用如下命令快速部署:


  ```shell
  docker run -d -p 8080:80 --name 12306 yinaoxiong/12306_code_server
  ```

### docker-compose部署(推荐)


```yaml
version: "3"

services:
  code_12306:
    image: yinaoxiong/12306_code_server
    ports:
      - 5002:80 #可以根据需要修改端口
    environment:
      - WORKERS=1 #gunicorn works 默认为1可以根据服务器配置自行调整
    restart: always
  
```

### 通过源码部署

1. 克隆并进入项目

   ```shell
   git clone https://github.com/YinAoXiong/12306_code_server.git
   cd 12306_code_server
   ```

2. 安装依赖 自行根据平台和python选择对应的tflite（下面的例子为amd64，python3.7，其他情况对应的下载地址见 [https://www.tensorflow.org/lite/guide/python](https://www.tensorflow.org/lite/guide/python)，可自行在requirements.txt中替换）

   ```shell
   pip3 install -r requirements.txt
   ```

3. 下载模型文件

    ```shell
    bash download_model.sh
    ```
    从GitHub下载慢的话可以选择执行下面的命令

    ```shell
    wget -c https://cdn.yinaoxiong.cn/models/image.model.tflite
    wget -c https://cdn.yinaoxiong.cn/models/text.model.tflite
    ```

4. 运行 默认workers为1，使用80端口，可以自行修改 gunicorn.conf

   ```shell
   gunicorn app:app -c gunicorn.conf.py
   ```

不推荐在arm平台上使用源码部署,依赖安装有些麻烦.

## 致谢

- [easy12306](https://github.com/zhaipro/easy12306) 提供项目运行的model
-  [12306购票小助手](https://github.com/testerSunshine/12306)源于该项目的一个issue
- ~~[tensorflow-on-arm](https://github.com/lhelontra/tensorflow-on-arm)提供arm上运行的tensorflow python包~~ v1.1版本后开始使用tflite而非keras
