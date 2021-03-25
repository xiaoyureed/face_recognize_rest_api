# coding:utf-8
import multiprocessing

bind = "0.0.0.0:5000"  # binding host:port
workers = multiprocessing.cpu_count() * 2 + 1  # progress number
errorlog = './log/gunicorn.error.log'  # error log , 得新建 log dir, 给读写权限, 文件会自动创建
accesslog = './log/gunicorn.access.log'  #
backlog = 512  # 监听队列
proc_name = 'gunicorn_pre_project'  # progress name
timeout = 30  # def to 30s。
worker_class = 'gevent'  # 使用gevent模式，还可以使用sync 模式，def to sync模式

threads = 3  # thread number in one progress
loglevel = 'info'  # 错误日志的级别，而访问日志的级别无法设置

# 设置gunicorn访问日志格式，错误日志无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

daemon = True
