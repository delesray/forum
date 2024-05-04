from __future__ import annotations
from math import ceil
from urllib.parse import parse_qs
from passlib.context import CryptContext
from starlette.requests import Request
from pydantic import BaseModel

# an instance of the CryptContext class that specifies the hashing algorithm - bcrypt in this case
pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_pass(password: str) -> str:
    return pass_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pass_context.verify(plain_password, hashed_password)


class PaginationInfo:
    def __init__(self, total_elements, page, size, pages):
        self.total_elements = total_elements
        self.page = page
        self.size = size
        self.pages = pages


class Links:
    def __init__(self, current, first, last, next=None, prev=None):
        self.current = current
        self.first = first
        self.last = last
        self.next = next
        self.prev = prev


def get_pagination_info(total_elements, page, size) -> PaginationInfo:
    info = PaginationInfo(
        total_elements=total_elements,
        page=page,
        size=size,
        pages=ceil(total_elements / size)
    )
    return info


def create_links(request: Request, pagination_info: PaginationInfo) -> Links:
    # base_url = str(request.url_for("get_all_topics"))
    pi = pagination_info

    # todo discuss: because self is keyword?
    links = Links(
        current=f"{request.url}",
        first=f"{result_url(request, 1, pi.size)}",
        last=f"{result_url(request, pi.pages, pi.size)}",
        next=f"{result_url(request, pi.page + 1, pi.size)}" if pi.page * pi.size < pi.total_elements else None,
        prev=f"{result_url(request, pi.page - 1, pi.size)}" if pi.page - 1 >= 1 else None
    )
    return links


def result_url(request: Request, page: int, size: int) -> str:
    parsed_query = parse_qs(request.url.query)

    parsed_query.update({'page': [str(page)], 'size': [str(size)]})
    new_query = '&'.join(f'{key}={val[0]}' for key, val in parsed_query.items())

    new_url = f'{request.url.scheme}://{request.url.netloc}{request.url.path}'
    if new_query:
        new_url += f'?{new_query}'

    return new_url
