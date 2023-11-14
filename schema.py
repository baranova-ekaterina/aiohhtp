import json

from pydantic import BaseModel, validator, ValidationError
from typing import Type, Optional  
from aiohttp import web


class CreateUser(BaseModel):
    name: str
    user_pass: str

    @validator('name')
    def validate_name(cls, value):
        if len(value) > 80:
            raise ValueError('Name is too big. You have 80 symbols.')
        return value

    @validator('user_pass')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('password is too short')
        if len(value) > 100:
            raise ValueError('password is too big')
        return value


class UpdateUser(BaseModel):

    name: Optional[str]
    user_pass: Optional[str]

    @validator('name')
    def validate_name(cls, value):
        if len(value) > 80:
            raise ValueError('Name is too big. You have 80 symbols.')
        return value

    @validator('user_pass')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('password is too short')
        if len(value) > 100:
            raise ValueError('password is too big')
        return value


class CreateAdModel(BaseModel):
    title: str
    description: Optional[str]
    owner_id: int


class UpdateAdModel(BaseModel):
    title: str
    description: Optional[str]

def validate(
        json_data: dict,
        model_class: Type[CreateUser] | Type[UpdateUser] | Type[CreateAdModel] | Type[UpdateAdModel],
        ):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)

    except ValidationError as error:
        raise web.HTTPBadRequest(
            text=json.dumps({'error': error.errors()}),
            content_type='application/json'
        )
    
