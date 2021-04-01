# face recog api

图片传输通过 base64 格式

在线 base64 -> https://www.sojson.com/image2base64.html, 前缀 "data:image/jpeg;base64," 可以不用去除了

除申请 api_key/api_secret 外, 所有请求需要提供两个 request header: 

(为了方便测试, `x-sign` 检查暂时关闭了, 可以不传)

```
x-api-key
x-sign  生成规则: 请求参数按照名称升序排列, 然后 md5(secret_key + k1v1k2v2.. + secret_key)
```

## apply api_key secret_key

先申请 api_key/secret_key , 调用其他 api 时, 认证使用

post - http://8.136.113.182/consumers

req:

```json
{
  "name": "白鹤滩",
  "pwd": "xxxx"
}
```

resp:

```json
{
  "code": 0,
  "data": {
    "api_key": "1a9471e9-1573-3eb3-9ad5-09aa2244c1d9",
    "secret_key": "5b1ace33-a38a-3178-9a4b-759a48e914fb"
  },
  "msg": ""
}
```

## dataset

查看已经标记的人脸

### req

get - http://8.136.113.182/dataset

### resp

```json
{
  "code": 0,
  "data": {
    "dataset": [
    ]
  },
  "msg": ""
}
```

## face recognize

识别

### req

post - http://8.136.113.182/face_recognize

req:

```json
{
  "image": "base64_str"
}
```

### resp

```json
{
  "code": 0,
  "data": {
    "name": "刘诗诗"
  },
  "msg": ""
}
```

## upload api

上传照片, 标识

### req

post - http://8.136.113.182/upload_pic

```json
{
  "image": "base64_str",
  "name": "zhang",
  "idCard": "432232"
}
```

### resp

```json
{
  "code": 0,
  "msg": ""
}
```
