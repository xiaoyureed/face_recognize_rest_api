from database.models import Face
from model.resp import BaseResp, DatasetResp
from flask import Blueprint, g

from util.obj_utils import resp_json

dataset_bp = Blueprint('dataset_bp', __name__)


@dataset_bp.route("/dataset", methods=['GET'])
def supported_dataset():
    re = execute()
    return resp_json(re)


def execute():
    # consumer_id = g.get('consumer_id')
    consumer_id = g.consumer_id
    faces = Face.query.filter_by(consumer_id=consumer_id).all()
    dataset = [face.name for face in faces]
    re = BaseResp[DatasetResp](code=0, msg="", data=DatasetResp(dataset=dataset))
    return re
