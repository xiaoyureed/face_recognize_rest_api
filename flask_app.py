# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Face recognition
"""

import face_recognition
from flask import Flask, request, jsonify
from config import consts
from database.models import Consumer
from model.resp import BaseResp, ConsumerFindResp
from database.exts import db
from service import dataset, upload_pic, face_recog

'do not name this file as flask.py for it conflict with Flask framework'

app = Flask(__name__)
app.config.from_object(consts)
db.init_app(app)


@app.route('/consumers', methods=['POST'])
def create_consumer():
    json_req = request.json
    name = json_req.get("name", "def_value").strip()
    pwd = json_req.get("pwd", "").strip()

    db.session.add(Consumer(name=name, pwd=pwd))
    db.session.commit()

    return jsonify(BaseResp.ok().dict())


@app.route('/consumers', methods=['GET'])
def find_consumer():
    consumers = Consumer.query.all()
    data = [ConsumerFindResp(id=c.id, name=c.name, pwd=c.pwd).dict() for c in consumers]
    print(data)
    return jsonify(BaseResp.ok_with_data(data).dict())


@app.route("/dataset", methods=['GET'])
def supported_dataset():
    re = dataset.execute()
    return jsonify(re.dict())


@app.route("/upload_pic", methods=['POST'])
def save_pic():
    """
    仅仅允许独照, 合照无法确认每个人的名字

    req:
    {
        "image": "base64_str",
        "name": "Tom",
        "suffix": "jpg"
    }
    """
    re = upload_pic.execute()
    return jsonify(re.dict(exclude_none=True))


def get_single_encoding(single_image_path):
    """
    resolve single image encoding

    :param single_image_path: image relative path
    :return: image encoding
    """
    image_single = face_recognition.load_image_file(single_image_path)
    return face_recognition.face_encodings(image_single)[0]


@app.route("/face_recognize", methods=["POST"])
def face_recognize():
    """
    识别

    req:
    {
        "image": "base64"
    }

    resp:
    {
        "code": 0,
        "msg": "",
        data: {
            "name": "xxx"
        }
    }
    """
    re = face_recog.execute()
    return jsonify(re.dict(exclude_none=True))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
