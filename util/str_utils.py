import hashlib
import uuid

import numpy as np


def md5(target: str) -> str:
    """md5 encryption
    """
    md5_hash_obj = hashlib.md5()
    md5_hash_obj.update(target.encode("utf-8"))
    # length 32
    return md5_hash_obj.hexdigest()


def gen_uuid(namespace: str) -> str:
    id_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, namespace)
    return str(id_uuid)


def enc_face_encoding(encoding) -> str:
    # the element in list is an array
    np_arr_list = encoding.tolist()
    # arr -> str
    np_str_list = [str(arr) for arr in np_arr_list]
    encoding_str = ",".join(np_str_list)
    return encoding_str


def dec_face_encoding(encoding_str: str):
    dlist = encoding_str.strip(' ').split(',')
    # 将list中str转换为float
    dfloat = list(map(float, dlist))
    face_encoding = np.array(dfloat)
    return face_encoding
