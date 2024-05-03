from fastapi import HTTPException, Depends
from typing import Annotated, Union
from data.models.user import User, AnonymousUser, Token, TokenData
from services.users_services import find_by_username
from datetime import timedelta, datetime
from jose import jwt, JWTError, ExpiredSignatureError
from secret_key import SECRET_KEY
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def create_access_token(data: TokenData) -> Token:
    to_encode = dict(data)
    expire = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return Token(access_token=encoded_jwt, token_type='bearer')


# checks token exp validity
def is_token_exp_valid(exp: str) -> bool:
    exp_datetime = datetime.strptime(exp, '%Y-%m-%d %H:%M:%S')
    return exp_datetime > datetime.now()


# Union specifies that the returned type would be either one of these
def verify_token_access(token: str) -> Union[TokenData, str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin")
        exp_at: str = payload.get("expire")

        if not is_token_exp_valid(exp_at):
            raise ExpiredSignatureError()

        token_data = TokenData(username=username, is_admin=is_admin)
        return token_data

    # in case of token exp
    except ExpiredSignatureError:
        return "Token has expired. Please log in again"

    # in case of invalid token
    except JWTError:
        return "Invalid token"


def get_admin_required(token: Annotated[str, Depends(oauth2_scheme)]):
    admin = get_current_user(token)
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return admin


def get_user_required(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    return get_current_user(token)


def get_user_optional(token: Annotated[str, Depends(oauth2_scheme_optional)]) -> User | AnonymousUser:
    if not token:
        return AnonymousUser()
    return get_current_user(token)


def get_current_user(token):
    token_data = verify_token_access(token)

    # will return the correct msg - either invalid token or expired token
    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=400, detail=token_data)

    user = find_by_username(token_data.username)
    # if the token is verified but there is no such user (has been deleted)
    if not user:
        raise HTTPException(status_code=404, detail="No such user")

    return user


UserAuthDep = Annotated[User, Depends(get_user_required)]
AdminAuthDep = Annotated[User, Depends(get_admin_required)]
OptionalUser = Annotated[User | AnonymousUser, Depends(get_user_optional)]
