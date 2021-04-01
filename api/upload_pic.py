import base64
import json
import traceback
from json.decoder import JSONDecodeError

import cv2
import face_recognition
import numpy as np
from flask import Blueprint, current_app
from flask import request, g

from database.exts import db
from database.models import Face
from model.resp import BaseResp
from util import str_utils, obj_utils

upload_pic_bp = Blueprint('upload_pic_bp', __name__)


def execute():
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

    # request params
    name = req_parsed["name"]
    id_card = req_parsed.get("idCard")
    if not id_card:
        return BaseResp.err("Field [idCard] is reuquired")
    # str
    img_b64 = req_parsed["image"]
    if img_b64.startswith("data:image/jpeg;base64,"):
        # split base64 prefix
        img_b64 = img_b64.split(",")[1]

    # # check the  name if already exist or not
    # # TODO also have to check encodings to avoid duplicated face in dataset
    # names_exist = show_dataset()
    # if name in names_exist:
    #     return jsonify(BaseResp(code=1, msg="The name you input already exist :(").dict(exclude_none=True))

    # decode base64 , return a byte arr
    img_decoded = base64.b64decode(img_b64)
    # np arr
    np_arr = np.frombuffer(img_decoded, np.uint8)
    # np arr -> cv2 bgr
    img_brg = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # bgr -> rgb
    img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)

    # # byte arr
    # img_decoded = base64.b64decode(img_b64)
    # #
    # image_np_arr = np.frombuffer(img_decoded, np.uint8)

    # # save to upload temp dir
    # # TODO consider remove upload image to save 磁盘,
    # #  or 直接从 request stream -> numpy arr -> save locations
    # cv2.imwrite("{}/{}.{}".format(consts.upload_temp_path, name, suffix),
    #             cv2.imdecode(image_np_arr, cv2.IMREAD_COLOR))

    # img_brg = cv2.imread("{}/{}.{}".format(consts.upload_temp_path, name, suffix))
    # img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(img_rgb)
    if len(face_locations) > 1:
        return BaseResp(code=1, msg="Only allow a single face in one image :(")

    # # only allow single face in one image
    # (top, right, bottom, left) = face_locations[0]
    # # we have to operate img_brg instead of img_rgb cause the second one have a wrong color mode for recog
    # single = img_brg[top:bottom, left:right]
    # # read image from a np arr
    # # imdecode = cv2.imdecode(single, cv2.IMREAD_COLOR)
    #
    # # sava to dataset dir
    # cv2.imwrite("{}/{}.{}".format(consts.dataset_path, name, suffix), single)
    # print(">>> save {}.{} into dataset".format(name, suffix))

    consumer_id = g.get("consumer_id")
    current_app.logger.debug('>>> consumer_id = {}'.format(consumer_id))
    encoding = face_recognition.face_encodings(img_rgb)[0]
    face = Face(name=name, id_card=id_card, arr=str_utils.enc_face_encoding(encoding),
                consumer_id=consumer_id)
    db.session.add(face)
    db.session.commit()

    return BaseResp(code=0, msg="")


@upload_pic_bp.route('/upload_pic', methods=['POST'])
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
    re = execute()
    return obj_utils.resp_json(re)
