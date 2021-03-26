# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Face recognition
"""

import base64
import json
import os
import os.path as path
from json.decoder import JSONDecodeError
import traceback

import cv2
import face_recognition
import numpy as np
from flask import Flask, request

'do not name this file as flask.py for it conflict with Flask framework'

app = Flask(__name__)

CONST_DATASET_PATH = "./data_set"
CONST_UPLOAD_TEMP_PATH = "./upload_temp"
# tolerance
# will be more strict if make it lower
CONST_TOLERANCE = 0.4


@app.route('/')
def hello_world():
    return 'Hello, World!'


def show_dataset():
    result = []
    file_names = os.listdir(CONST_DATASET_PATH)
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
    # req_parsed = None
    try:
        req_parsed = json.loads(req_decoded)
    except JSONDecodeError as err:
        err_msg = "Json Format error: " + str(err)
        print(">>> ", err_msg)
        print(traceback.format_exc())

        return {
            "code": 1,
            "msg": err_msg
        }

    # str
    img_b64 = req_parsed["image"]
    name = req_parsed["name"]
    suffix = req_parsed["suffix"]

    # check the  name if already exist or not
    # TODO also have to check encodings to avoid duplicated face in dataset
    # names_exist = os.listdir()
    names_exist = show_dataset()
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
    cv2.imwrite("{}/{}.{}".format(CONST_UPLOAD_TEMP_PATH, name, suffix),
                cv2.imdecode(image_np_arr, cv2.IMREAD_COLOR))

    # # 格式
    # image_np_arr_rgb = cv2.cvtColor(image_np_arr, cv2.COLOR_BGR2RGB)
    # # 切割出标本
    # face_locations = face_recognition.face_locations(image_np_arr_rgb)
    # print(face_locations)

    img_brg = cv2.imread("{}/{}.{}".format(CONST_UPLOAD_TEMP_PATH, name, suffix))
    img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=0, model="cnn")

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

    cv2.imwrite("{}/{}.{}".format(CONST_DATASET_PATH, name, suffix), single)
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
    Prepare encodings for faces exist in dataset folder

    :param dir_path: pics dir path
    :return: a tuple containing two element (encodings, names)
    """
    result = ([], [])
    # The filenames contain suffix, which have to be removed
    file_names = os.listdir(dir_path)
    for f_name in file_names:

        #  skip .DS_Store, only for mac
        if f_name == ".DS_Store":
            continue

        f_path = path.join(dir_path, f_name)
        if path.isfile(f_path):
            image = face_recognition.load_image_file(f_path)
            encoding_single = face_recognition.face_encodings(image)[0]
            result[0].append(encoding_single)
            (f_name_pure, _) = path.splitext(f_name)
            result[1].append(f_name_pure)
        else:
            print(">>> unexpected object, such as dir, link ....")
    return result


# 计算两张图片的相似度，范围：[0,1]
def simcos(A, B):
    A = np.array(A)
    B = np.array(B)
    dist = np.linalg.norm(A - B)  # 二范数
    sim = 1.0 / (1.0 + dist)  #
    return sim


# Threshold越高识别越精准，但是检出率越低
def compare_faces(x, y, Threshold):
    ressim = []
    match = [False] * len(x)
    for fet in x:
        sim = simcos(fet, y)
        ressim.append(sim)
    if max(ressim) > Threshold:  # 置信度阈值
        match[ressim.index(max(ressim))] = True
    return match, max(ressim)


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
    try:
        req_parsed = json.loads(req_decoded)
    except JSONDecodeError as err:
        err_msg = "Json Format error: " + str(err)
        print(">>> ", err_msg)
        print(traceback.format_exc())

        return {
            "code": 1,
            "msg": err_msg
        }

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

    # error: Unsupported image type, must be 8bit gray or RGB image
    encodings_unknown = face_recognition.face_encodings(img_rgb)
    if not (len(encodings_unknown) > 0):
        return {
            "code": 1,
            "msg": "No face exist in the image that you input :("
        }
    if len(encodings_unknown) > 1:
        return {
            "code": 1,
            "msg": "Too many face detected in your image :("
        }

    # read dataset at one time, 耗费内存
    (encodings, names) = prepare_encoding_dataset(CONST_DATASET_PATH)
    # check_result = face_recognition.compare_faces(
    #     encodings, encodings_unknown[0], tolerance=CONST_TOLERANCE
    # )

    (check_result, score) = compare_faces(encodings, encodings_unknown, 0.8)
    if score <= 0:
        print(">>> score = ", score)
        return {
            "code": 1,
            "msg": "Score 异常负值"
        }

    count_matched = 0
    for match in check_result:
        if count_matched > 1:
            # if return , consider make tolerance lower
            return {
                "code": 1,
                "msg": "Multiple face were matched."
            }
        if match:
            count_matched += 1

    if count_matched == 0:
        return {
            "code": 1,
            "msg": "Cannot recognize the face in your image :(, score -> " + str(score)
        }

    # TODO - can be optimized, 合并到上面的循环中去
    name_find = ""
    for re_index, match in enumerate(check_result):
        if match:
            name_find = names[re_index]

    return {
        "code": 0,
        "msg": "score -> " + str(score),
        "data": {
            "name": name_find
        }
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
