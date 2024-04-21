import uvicorn
from fastapi import FastAPI
from routers.users import users_router
from routers.categories import categories_router
from routers.topics import topics_router
from routers.admin import admin_router

app = FastAPI()
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(topics_router)
app.include_router(admin_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
