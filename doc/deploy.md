## install dependencies

ref -> requierements.txt

```shell
git clone --depth 1 
```

## nginx

```shell
cp ./nginx/face_recog.conf /etc/nginx/conf.d/default.conf
```

## log

```shell
mkdir "log"
```

## gunicorn

install gunicorn, gevent

```shell
#start
gunicorn flask_app:app -c gunicorn.conf.py
```


