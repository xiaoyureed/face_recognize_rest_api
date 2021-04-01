# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Face recognition
"""

from flask import Flask, request, g

import app_props
from api.consumer_create import consumer_create_bp
from api.dataset import dataset_bp
from api.face_recognize import face_recognize_bp
from api.upload_pic import upload_pic_bp
from database.exts import db
from database.models import Key
from model.resp import BaseResp
from util import str_utils
from util.obj_utils import resp_json

'do not name this file as flask.py for it conflict with Flask framework'

app = Flask(__name__)
app.config.from_object(app_props)
db.init_app(app)

# log
#
# logging.basicConfig(**{
#     'level': logging.DEBUG
# })
app.logger.setLevel(app_props.log_level)

app.register_blueprint(upload_pic_bp)
app.register_blueprint(face_recognize_bp)
app.register_blueprint(dataset_bp)
app.register_blueprint(consumer_create_bp)


@app.errorhandler(500)
def handling_unknown_err(e):
    """Global exception Handler"""
    app.logger.exception(e)
    return resp_json(BaseResp.err(e.name))


@app.before_request
def api_key_check():
    """Global interceptor
    """
    req_path = request.path
    method_type = request.method
    app.logger.info(">>> path = {}, method = {}".format(req_path, method_type))

    if not app_props.api_key_check:
        app.logger.debug('>>> api key check closed')
        return None

    if req_path in app_props.api_key_white_list:
        app.logger.info('>>> {} in white list, pass'.format(req_path))
        return None
    headers = request.headers
    api_key_from_req = headers.get('x-api-key')
    if not api_key_from_req:
        app.logger.debug('>>> enter api-key error')
        return resp_json(BaseResp.err('no x-api-key header'))

    key_obj = Key.query.filter_by(api_key=api_key_from_req).first()
    if key_obj:
        app.logger.debug('>>> consumer_id = {}, secret_key = {}'.format(key_obj.consumer_id, key_obj.secret_key))
        g.consumer_id = key_obj.consumer_id
        g.secret_key = key_obj.secret_key
        return None
    else:
        return resp_json(BaseResp.err('Err api key'))


def request_parse(req_data):
    """解析请求数据并以json形式返回"""
    data = None
    if req_data.method == 'POST':
        data = req_data.json
    elif req_data.method == 'GET':
        data = req_data.args
    return data


def sort_dict(dic):
    """sorted according to key
    """
    return sorted(dic.items(), key=lambda d: d[0])


@app.before_request
def sign_check():  # order decided by code order
    """
    sign gen format: md5(secret_key + k1v1k2v2.. + secret_key)
    """
    if not app_props.sign_check:
        app.logger.debug('>>> sign check closed')
        return None
    # dict
    data = request_parse(request)
    # [(k,v),...]
    data_sorted = sort_dict(data)
    data_to_be_enc = []
    for entry in data_sorted:
        data_to_be_enc.append(entry[0] + entry[1])
    secret_key = g.get("secret_key")
    data_to_be_enc = secret_key + ''.join(data_to_be_enc) + secret_key
    data_enc = str_utils.md5(data_to_be_enc)
    sign_from_req = request.headers.get('x-sign')
    if not sign_from_req:
        return resp_json(BaseResp.err('no x-sign header'))
    if sign_from_req != data_enc:
        return resp_json(BaseResp.err('Sign error'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
