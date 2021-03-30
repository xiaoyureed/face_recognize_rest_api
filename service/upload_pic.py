import base64
import json
import traceback
from json.decoder import JSONDecodeError


import cv2
import face_recognition
import numpy as np
from flask import request, jsonify

from config import consts
from model.resp import BaseResp
from service.common import show_dataset


def execute():
    # str
    req_decoded = request.get_data().decode("utf-8")
    # name = request.json.get("name", "def value").strip();

    # dict
    # req_parsed = None
    try:
        req_parsed = json.loads(req_decoded)
    except JSONDecodeError as err:
        err_msg = "Json Format error: " + str(err)
        print(">>> ", err_msg)
        print(traceback.format_exc())

        return jsonify(BaseResp(code=1, msg=err_msg).dict(exclude_none=True))

    # request params
    # str
    img_b64 = req_parsed["image"]
    if img_b64.startswith("data:image/jpeg;base64,"):
        # split base64 prefix
        img_b64 = img_b64.split(",")[1]
    name = req_parsed["name"]
    suffix = req_parsed["suffix"]
    # id_card = req_parsed["id_card"]

    # check the  name if already exist or not
    # TODO also have to check encodings to avoid duplicated face in dataset
    # names_exist = os.listdir()
    names_exist = show_dataset()
    if name in names_exist:
        return jsonify(BaseResp(code=1, msg="The name you input already exist :(").dict(exclude_none=True))

    # byte arr
    img_decoded = base64.b64decode(img_b64)
    #
    image_np_arr = np.frombuffer(img_decoded, np.uint8)



    # TODO consider remove upload image to save 磁盘,
    #  or 直接从 request stream -> numpy arr -> save locations
    cv2.imwrite("{}/{}.{}".format(consts.upload_temp_path, name, suffix),
                cv2.imdecode(image_np_arr, cv2.IMREAD_COLOR))

    img_brg = cv2.imread("{}/{}.{}".format(consts.upload_temp_path, name, suffix))
    img_rgb = cv2.cvtColor(img_brg, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)

    if len(face_locations) > 1:
        return jsonify(BaseResp(code=1, msg="Only allow a single face in one image :(").dict(exclude_none=True))

    # only allow single face in one image
    (top, right, bottom, left) = face_locations[0]
    # we have to operate img_brg instead of img_rgb cause the second one have a wrong color mode for recog
    single = img_brg[top:bottom, left:right]
    # read image from a np arr
    # imdecode = cv2.imdecode(single, cv2.IMREAD_COLOR)

    cv2.imwrite("{}/{}.{}".format(consts.dataset_path, name, suffix), single)
    print(">>> save {}.{} into dataset".format(name, suffix))

    return BaseResp(code=0, msg="")
