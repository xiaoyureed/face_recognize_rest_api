def obj_to_dict(obj: object):
    re = {}
    re.update(obj.__dict__())
    return re
