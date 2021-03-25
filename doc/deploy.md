## deploy

```shell
# dependencies
#ref -> requierements.txt
# dlib (https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)

#source code
git clone --depth 1 http://122.191.199.53:60030/xiaoyu/face_recognize_app
cd face_recognize_app

# log dir, dataset dir, upload temp. 有读写权限 
mkdir log data_set upload_temp


#install gunicorn, gevent
pip3 install gunicorn gevent

#nginx
apt install nginx
cp ./nginx/face_recog.conf /etc/nginx/conf.d/default.conf

#start
gunicorn flask_app:app -c gunicorn.conf.py
service nginx restart
```



