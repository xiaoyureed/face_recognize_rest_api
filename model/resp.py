from typing import List, TypeVar, Generic, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel

# define a generic type
DataT = TypeVar('DataT')


class BaseResp(GenericModel, Generic[DataT]):
    """Common response class

    ref -> https://pydantic-docs.helpmanual.io/usage/models/#generic-models
    """
    code: int
    msg: str
    data: Optional[DataT] = None

    @classmethod
    def ok(cls):
        result = cls(code=0, msg="")
        return result

    @classmethod
    def ok_with_data(cls, data: DataT):
        result = cls[DataT](code=0, msg="", data=data)
        return result

    @classmethod
    def err(cls, msg: str):
        result = cls(code=1, msg=msg)
        return result


class DatasetResp(BaseModel):
    """response for checking marked faces"""
    dataset: List[str]


class RecognizeResp(BaseModel):
    name: str
    idCard: str


class ConsumerFindResp(BaseModel):
    id: int
    name: str
    pwd: str
