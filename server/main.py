import uvicorn
from fastapi import FastAPI, Request
from routers.users import users_router
from routers.categories import categories_router
from routers.topics import topics_router
from routers.admin import admin_router
from routers.replies import replies_router
from routers.votes import votes_router
from routers.messages import messages_router

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(topics_router)
app.include_router(admin_router)
app.include_router(replies_router)
app.include_router(votes_router)
app.include_router(messages_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)  # response_class is for the /docs to know that the response will be HTML
async def welcome_view(request: Request):
    return templates.TemplateResponse(
        request=request, name="welcome.html", context={"welcome": 'Welcome people'}
    )


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


@app.get("/categories_demo", response_class=HTMLResponse)
async def categories_demo_view(
        request: Request,
        search: str | None = None
):
    from services.categories_services import get_all
    categories = get_all(search=search)

    return templates.TemplateResponse(
        request=request, name="categories_demo.html", context={'categories': categories}
    )


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
