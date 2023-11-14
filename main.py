from aiohttp import web
from server import orm_context, session_middleware, UserView, AdView

app = web.Application() 

app.cleanup_ctx.append(orm_context) 

app.middlewares.append(session_middleware)

app.add_routes(
    [
        web.post('/users/', UserView),
        web.get('/users/{user_id:\d+}', UserView),
        web.patch('/users/{user_id:\d+}', UserView),
        web.delete('/users/{user_id:\d+}', UserView),

        web.post('/advertisements/', AdView),
        web.get('/advertisements/{advertisement_id:\d+}', AdView),
        web.patch('/advertisements/{advertisement_id:\d+}', AdView),
        web.delete('/advertisements/{advertisement_id:\d+}', AdView),
    ]
)

# запускаем приложение.
web.run_app(app)