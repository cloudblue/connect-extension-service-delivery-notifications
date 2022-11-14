from datetime import datetime
from typing import Any, List, Optional

import peewee
from pydantic import BaseModel, Extra
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):  # pragma: no branch
            return list(res)  # pragma: no cover
        return res


class Settings(BaseModel):
    name: str
    email_sender: str


class Rule(BaseModel):
    id: Optional[str]
    installation_id: Optional[str]
    product_id: str
    product_name: str
    product_logo: Optional[str]
    message: str
    enabled: bool

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EmailLog(BaseModel):
    id: Optional[str]
    installation_id: Optional[str]
    date: datetime
    body: Optional[str]
    email_from: Optional[str]
    email_response: Optional[str]
    email_to: str
    product_id: str
    product_name: str
    product_logo: Optional[str]
    request_id: Optional[str]
    asset_id: Optional[str]

    def dict(self, **kwargs):
        kwargs.pop('exclude_none', None)
        return super().dict(exclude_none=True, **kwargs)

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EmailLogPage(BaseModel):
    count: int
    results: List[EmailLog]


class Product(BaseModel, extra=Extra.ignore):
    id: str
    name: str
    icon: Optional[str]


class Error(BaseModel):
    code: str
    message: str
