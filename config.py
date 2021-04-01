import logging

# salt for md5 enc
salt = "salt_2021@#"

log_level = logging.DEBUG

# enable api key check
api_key_check = False
api_key_white_list = ['/consumers']

# enable sign check
sign_check = False

# if higher, then stricter
threshold_score = 0.738
# lower, stricter
# threshold_tolerance = 0.4

######
# db
######
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'face_recognize'
USERNAME = 'root'
PASSWORD = '123456'
DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,
                                                                                        password=PASSWORD, host=HOST,
                                                                                        port=PORT, db=DATABASE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# setup to True when debug
SQLALCHEMY_ECHO = True
# db conn pool size, def to 5
# SQLALCHEMY_POOL_SIZE = 5
# conn timeout
# SQLALCHEMY_POOL_TIMEOUT =
# 空闲超过多久回收连接
# SQLALCHEMY_POOL_RECYCLE
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它
# SQLALCHEMY_TRACK_MODIFICATIONS
# 连接池达到最大值后可以创建的连接数
# SQLALCHEMY_MAX_OVERFLOW

