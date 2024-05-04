from __future__ import annotations

from math import ceil

from passlib.context import CryptContext

from data.models.topic import PaginationInfo

# an instance of the CryptContext class that specifies the hashing algorithm - bcrypt in this case
pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_pass(password: str) -> str:
    return pass_context.hash(password)


print(hash_pass('random'))
print(hash_pass('deni'))
print(hash_pass('olesya'))


def verify_password(plain_password, hashed_password) -> bool:
    return pass_context.verify(plain_password, hashed_password)


def pagination_info(total_elements, page, size):
    if not total_elements:
        return None
    else:
        return PaginationInfo(
            total_elements=total_elements,
            page=page,
            size=size,
            pages=ceil(total_elements / size)
        )
