from fastapi import FastAPI
from routers.users import users_router
import uvicorn

app = FastAPI()
app.include_router(users_router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
