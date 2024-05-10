from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

common_router = APIRouter(prefix='', tags=['common'])
templates = Jinja2Templates(directory="templates")


@common_router.get(
    path='/',
    response_class=HTMLResponse,
    name='home_page_view', )
def home_page_view(
        request: Request,
):
    return templates.TemplateResponse(
        request=request, name="home_page.html"
    )
