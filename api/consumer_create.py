from flask import Blueprint, current_app
from flask import request
from pydantic import BaseModel

from database.exts import db
from database.models import Consumer, Key
from model.resp import BaseResp, ConsumerFindResp
from util import str_utils
from util.obj_utils import resp_json

consumer_create_bp = Blueprint('consumer_create_bp', __name__)


@consumer_create_bp.route('/consumers', methods=['POST'])
def register():
    re = execute()
    return resp_json(re)


@consumer_create_bp.route('/consumers', methods=['GET'])
def find_consumer():
    consumers = Consumer.query.all()
    data = [ConsumerFindResp(id=c.id, name=c.name, pwd=c.pwd).dict() for c in consumers]
    current_app.logger.debug(data)
    return resp_json(BaseResp.ok_with_data(data))


class ConsumerCreateResp(BaseModel):
    api_key: str
    secret_key: str


def execute():
    json_req = request.json
    name = json_req.get("name", "def_name").strip()
    pwd = json_req.get("pwd", "def_pwd").strip()

    # check if name duplicate
    # find = Consumer.query.filter_by(name=name).all()
    # if len(find) > 0:
    #     return BaseResp.err('all error')
    find = Consumer.query.filter_by(name=name).first()
    if find:
        return BaseResp.err('name already exist')

    consumer = Consumer(name=name, pwd=str_utils.md5(pwd))
    db.session.add(consumer)
    db.session.flush()
    current_app.logger.debug(">>> insert consumer, id = {}".format(consumer.id))

    api_key = str_utils.gen_uuid(name)
    secret_key = str_utils.gen_uuid(pwd)
    key = Key(consumer_id=consumer.id, api_key=api_key, secret_key=secret_key)
    db.session.add(key)
    db.session.flush()
    current_app.logger.debug(">>> insert key, id = {}".format(key.id))

    db.session.commit()
    return BaseResp.ok_with_data(ConsumerCreateResp(api_key=api_key, secret_key=secret_key))
