# db design

## consumer

调用方

| 字段名 | 类型 | 描述 |
|:---: |: ---: | :---: |
|id | int | primary key
name | str | 调用方名称
pwd | str | 密码

## key

api 调用密匙表

(consumer 创建成功后, 默认生成一对 api_key/secret_key, 名称 为 default)

| 字段名 | 类型 | 描述 |
|:---: | :---: | :---: |
|id | int | primary key|
| consumer_id | int | 调用方 id
api_key | str |
secret_key | str |
name | str | api key 名称

## face

人脸数据表

| 字段名 | 类型 | 描述 |
|:---: | :---: | :---: |
id | int | primary key
name | str | 姓名
id_card | str | 身份证
arr | str | 人脸向量生成的字符串
consumer_id | int | 调用方 id