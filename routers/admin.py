from fastapi import APIRouter, Header
from data.models import Category
from services import categories_services
from common.auth import get_user_or_raise_401, is_admin_or_raise_401_403
from common.responses import BadRequest, Forbidden, Unauthorized, Created

#from devtools import debug

admin_router = APIRouter(prefix='/admin', tags=['admin'])


@admin_router.post('/categories', status_code=201)
def create_category(category: Category, x_token: str = Header()):
    is_admin_or_raise_401_403(x_token)  # todo potential decorator

    result = categories_services.create(category)
    if isinstance(result, Category):
        return result
    return BadRequest(result.msg)
