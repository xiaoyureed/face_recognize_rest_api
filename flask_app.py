import base64
import json
import os
import os.path as path

import cv2
import face_recognition
import numpy as np
from flask import Flask, request

'do not name this file as flask.py for it conflict with Flask framework'

# WSGI application.
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


def show_dataset():
    result = []
    file_names = os.listdir("./data_set")
    for f_name in file_names:
        (f_name_pure, _) = path.splitext(f_name)
        result.append(f_name_pure)
    return result


@app.route("/dataset", methods=['GET'])
def supported_dataset():
    dataset = show_dataset()
    return {
        "code": 0,
        "msg": "",
        "data": {
            "dataset": dataset
        }
    }


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
    # str
    req_decoded = request.get_data().decode("utf-8")
    # dict
    req_parsed = json.loads(req_decoded)
    # str
    img_b64 = req_parsed["image"]
    name = req_parsed["name"]
    suffix = req_parsed["suffix"]

    # check the  name if already exist or not
    # TODO also have to check encodings to avoid duplicated face in dataset
    names_exist = os.listdir("upload_temp")
    if name in names_exist:
        return {
            "code": 1,
            "msg": "The name you input already exist :("
        }

    # byte arr
    img_decoded = base64.b64decode(img_b64)
    #
    image_np_arr = np.frombuffer(img_decoded, np.uint8)

    # TODO consider remove upload image to save 磁盘,
    #  or 直接从 request stream -> numpy arr -> save locations
    cv2.imwrite("./upload_temp/{}.{}".format(name, suffix), cv2.imdecode(image_np_arr, cv2.IMREAD_COLOR))

    # # 格式
    # image_np_arr_rgb = cv2.cvtColor(image_np_arr, cv2.COLOR_BGR2RGB)
    # # 切割出标本
    # face_locations = face_recognition.face_locations(image_np_arr_rgb)
    # print(face_locations)

    img_brg = cv2.imread("./upload_temp/{}.{}".format(name, suffix))
    img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)

    if len(face_locations) > 1:
        return {
            "code": 1,
            "msg": "Only allow a single face in one image :("
        }

    # only allow single face in one image
    (top, right, bottom, left) = face_locations[0]
    # we have to operate img_brg instead of img_rgb cause the second one have a wrong color mode for recog
    single = img_brg[top:bottom, left:right]
    # read image from a np arr
    # imdecode = cv2.imdecode(single, cv2.IMREAD_COLOR)

    cv2.imwrite("./data_set/{}.{}".format(name, suffix), single)
    print(">>> save {}.{} into dataset".format(name, suffix))

    return {
        "code": 0,
        "msg": "ok"
    }


def get_single_encoding(single_image_path):
    """
    resolve single image encoding

    :param single_image_path: image relative path
    :return: image encoding
    """
    image_single = face_recognition.load_image_file(single_image_path)
    return face_recognition.face_encodings(image_single)[0]


def prepare_encoding_dataset(dir_path: str) -> tuple:
    """
    >remove file name extension: https://www.codegrepper.com/code-examples/python/remove+extension+filename+python
    :param dir_path: pics dir path
    :return: a tuple containing encodings as the first element and names as the second element
    """
    result = ([], [])
    file_names = os.listdir(dir_path)
    for f_name in file_names:
        if f_name == ".DS_Store":
            print(">>> skip .DS_Store :) ")
            continue
        f_path = path.join(dir_path, f_name)
        if path.isfile(f_path):
            image = face_recognition.load_image_file(f_path)
            encoding_single = face_recognition.face_encodings(image)[0]
            result[0].append(encoding_single)
            (f_name_pure, _) = path.splitext(f_name)
            result[1].append(f_name_pure)
    return result


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

    # parse the req body
    # str
    req_decoded = request.get_data().decode("utf-8")
    # dict
    req_parsed = json.loads(req_decoded)

    # str
    img_b64 = req_parsed["image"]
    # decode base64 , return a byte arr
    img_decoded = base64.b64decode(img_b64)
    # np arr
    np_arr = np.frombuffer(img_decoded, np.uint8)
    # np arr -> cv2 bgr format
    img_brg = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # bgr -> rgb
    img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)
    # 这步 optional
    # img_to_check = np.array(img_rgb)

    result = {}

    # error: Unsupported image type, must be 8bit gray or RGB image
    encodings_unknown = face_recognition.face_encodings(img_rgb)
    if not (len(encodings_unknown) > 0):
        result["code"] = 1
        result["msg"] = "No face exist in the image that you input"
        return result

    (encodings, names) = prepare_encoding_dataset("data_set")
    # tolerance, lower is more strict, def to 0.6
    check_result = face_recognition.compare_faces(encodings, encodings_unknown[0], tolerance=0.5)

    name_find = ""
    for re_index, re in enumerate(check_result):
        if re:
            name_find = names[re_index]

    if name_find == "":
        result["code"] = 1
        result["msg"] = "Cannot recognize the face in your image :("
        return result

    result["code"] = 0
    result["msg"] = ""
    result["data"] = {
        "name": name_find
    }
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
