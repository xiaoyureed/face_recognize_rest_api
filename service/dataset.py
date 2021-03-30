from model.resp import BaseResp, DatasetResp
from service.common import show_dataset


def execute():
    dataset = show_dataset()
    re = BaseResp[DatasetResp](code=0, msg="", data=DatasetResp(dataset=dataset))
    return re
