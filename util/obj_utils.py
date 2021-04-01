from flask import jsonify
from pydantic import BaseModel


def resp_json(obj: BaseModel):
    return jsonify(obj.dict(exclude_none=True))
