import json
from typing import Type, Callable, Awaitable

from aiohttp import web
import bcrypt
#from sqlalchemy.exc import IntegrityError
from models import engine, Session, AdModel, User, Base
from schema import validate, UpdateAdModel, CreateAdModel, CreateUser, UpdateUser


ERROR_TYPE = Type[web.HTTPUnauthorized] | Type[web.HTTPForbidden] | Type[web.HTTPNotFound]


def raise_http_error(error_class: ERROR_TYPE, message: str | dict):
    raise error_class(
        text=json.dumps({"status": "error", "description": message}),
        content_type="application/json",
    )


async def get_orm_item(item_class: Type[User] | Type[AdModel], item_id: int | str, session: Session):
    item = await session.get(item_class, item_id)
    if item is None:
        raise raise_http_error(web.HTTPNotFound, f"{item_class.__name__} not found")

    return item


def hash_password(password: str):
    encoded_password = password.encode()
    hashed_password = bcrypt.hashpw(password=encoded_password, salt=bcrypt.gensalt())
    decoded_password = hashed_password.decode()
    return decoded_password


async def orm_context(some_app: web.Application):
  
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all) 
    yield
    await engine.dispose() 


@web.middleware
async def session_middleware(
    request: web.Request, handler: Callable[[web.Request], Awaitable[web.Response]]
) -> web.Response:
    async with Session() as session:
        request["session"] = session
        return await handler(request)


class UserView(web.View):

    async def get(self):
        user_id = int(self.request.match_info.get('user_id'))  
        user = await get_orm_item(User, user_id, session=self.request.get('session'))  
        response = web.json_response({'user_id': user.id, 'user_name': user.name})  
        return response

    async def post(self):
        user_data = await self.request.json() 
        validated_data = validate(json_data=user_data, model_class=CreateUser) 
        user_password = validated_data.get('user_pass') 
        hashed_pass = hash_password(user_password)  
        validated_data['user_pass'] = hashed_pass  
        new_user = User(**validated_data)  
        self.request.get('session').add(new_user)  
        try:
            await self.request.get('session').commit() 
        except IntegrityError: 
            raise web.HTTPConflict(text=json.dumps({'status': 'user already exists'}), content_type='application/json')

        return web.json_response({'user_id': new_user.id})  


async def patch(self):   
        user_id = int(self.request.match_info.get('user_id'))  
        user_data = await self.request.json()  
        user_validated_data = validate(json_data=user_data, model_class=UpdateUser) 
        if 'user_pass' in user_validated_data: 
            user_validated_data['user_pass'] = hash_password(user_validated_data.get('user_pass'))

        user = await get_orm_item(item_class=User, item_id=user_id, session=self.request['session'])
        for field, value in user_validated_data.items(): 
            setattr(user, field, value)
        self.request['session'].add(user) 
        await self.request['session'].commit() 

        return web.json_response({'user_id': user_id}) 

async def delete(self):
        user_id = int(self.request.match_info.get('user_id')) 
        user = await get_orm_item(item_class=User, item_id=user_id, session=self.request['session'])
        session = self.request['session']
        await session.delete(user)
        await session.commit()
        return web.json_response({'status': 'user is deleted'})


class AdView(web.View):

    async def get(self, advertisement_id: int):
        adv_id = int(self.request.match_info.get(advertisment_id))
        adv = await get_orm_item(advertisement_id=advertisement_id, item_id=adv_id, session=self.request.get('session'))
        response = web.json_response({'advertisement_id': adv.id, 'title': adv.title, 'owner_id': adv.owner_id})
        return response
     
   
    async def post(self):
        adv_data = await self.request.json() 
        validated_data = validate(json_data=adv_data, model_class=CreateAdModel) 
        new_adv = AdModel(**validated_data) 
        self.request.get('session').add(new_adv)  
        await self.request.get('session').commit()  
        return web.json_response({'advertisement_title': new_adv.title})
    
    async def patch(self):
    
        adv_id = int(self.request.match_info.get('advertisement_id'))  
        adv_data = await self.request.json()  
        validated_data = validate(json_data=adv_data, model_class=UpdateAdModel)  
        # достаем объект из БД
        adv = await get_orm_item(item_class=AdModel, item_id=adv_id, session=self.request.get('session'))
        for field, value in validated_data.items():  
            setattr(adv, field, value)
        self.request.get('session').add(adv)  
        await self.request.get('session').commit()  

        return web.json_response({'adv_id': adv.id})
        

    async def delete(self):
        
        adv_id = int(self.request.match_info.get('advertisement_id'))  
        adv = await get_orm_item(item_class=AdModel, item_id=adv_id, session=self.request.get('session'))
        await self.request.get('session').delete(adv)
        await self.request.get('session').commit()

        return web.json_response({'status': f'advertisement {adv_id} is deleted'})
       


#app.add_url_rule("/advertisements/<int:id_ad>/", view_func=AdView.as_view('advertisements_delete'),
                 #methods=['DELETE', 'GET'])
#app.add_url_rule("/advertisements", view_func=AdView.as_view('advertisements_create'), methods=['POST'])