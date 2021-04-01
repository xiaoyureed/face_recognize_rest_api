import base64
import json
import os
import os.path as path
import traceback
from json.decoder import JSONDecodeError

import cv2
import face_recognition
import numpy as np
from flask import request, Blueprint, g

import app_props
from database.models import Face
from model.resp import BaseResp, RecognizeResp
from util import str_utils, obj_utils


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


def execute():
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

        return BaseResp(code=1, msg=err_msg)

    # str
    img_b64 = req_parsed["image"]
    if img_b64.startswith("data:image/jpeg;base64,"):
        # split base64 prefix
        img_b64 = img_b64.split(",")[1]

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

    encodings_unknown = face_recognition.face_encodings(img_rgb)
    if not (len(encodings_unknown) > 0):
        return BaseResp(code=1, msg="No face exist in the image :(")
    if len(encodings_unknown) > 1:
        return BaseResp(code=1, msg="Too many face detected in your image :(")

    #
    consumer_id = g.get('consumer_id')

    faces = Face.query.filter_by(consumer_id=consumer_id).all()
    if len(faces) == 0:
        return BaseResp.err('Upload first')

    encodings = []
    names = []
    for face in faces:
        encodings.append(str_utils.dec_face_encoding(face.arr))
        names.append(face.name)

    (check_result, score) = compare_faces(encodings, encodings_unknown, app_props.threshold_score)
    if score <= 0:
        print(">>> score = ", score)
        return BaseResp(code=1, msg="Score 异常负值")

    count_matched = 0
    for match in check_result:
        if count_matched > 1:
            # if return , consider make tolerance lower
            return BaseResp(code=1, msg="Multiple faces were recognized as the same person :(")
        if match:
            count_matched += 1

    if count_matched == 0:
        return BaseResp(code=1, msg="Cannot recognize the face in your image :(, score -> " + str(score))

    # TODO - can be optimized, 合并到上面的循环中去
    name_find = ""
    for re_index, match in enumerate(check_result):
        if match:
            name_find = names[re_index]

    return BaseResp[RecognizeResp](code=0, msg="score -> " + str(score), data=RecognizeResp(name=name_find))


face_recognize_bp = Blueprint('face_recognize_bp', __name__)


@face_recognize_bp.route("/face_recognize", methods=["POST"])
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
    re = execute()
    return obj_utils.resp_json(re)
