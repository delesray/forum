from fastapi import HTTPException, Depends
from typing import Annotated
from data.models import User, TokenData
from services.users_services import is_authenticated, from_token, find_by_username
from datetime import timedelta, datetime
from jose import jwt, JWTError, ExpiredSignatureError
from data.models import Token, TokenData
from secret_key import SECRET_KEY
from fastapi.security import OAuth2PasswordBearer
from common.responses import Unauthorized, BadRequest



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: TokenData) -> Token:
    to_encode = dict(data)
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return Token(access_token=encoded_jwt, token_type='jwt')


# checks token exp validity
def is_token_exp_valid(exp: str) -> bool:
    exp_datetime = datetime.strptime(exp, '%Y-%m-%d %H:%M:%S')
    return exp_datetime > datetime.now()


def verify_token_access(token: str) -> TokenData | JWTError:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin")
        #exp_at: str = payload.get("expire")

        # is is okay to raise raise from inside try block
        # if not is_token_exp_valid(exp_at):
        #     raise JWTError()
        
        token_data = TokenData(username=username, is_admin=is_admin)
        return token_data
    
    except ExpiredSignatureError:
        raise JWTError("Token has expired. Please log in again.")

    except JWTError as e:
        return e


def get_current_user(token: str = Depends(oauth2_scheme)) -> User | BadRequest | Unauthorized:
    token_data = verify_token_access(token)

    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=400, detail="Invalid token")

    user = find_by_username(token_data.username)

    # if the token is verified but there is no such user (has been deleted), raise 404
    if not user:
        raise HTTPException(status_code=404, detail="No such user")
    
    return user


def get_user_or_raise_401(token: str) -> User | HTTPException:
    if not is_authenticated(token):
        raise HTTPException(status_code=401)

    return from_token(token)


def is_admin_or_raise_401_403(token: str) -> bool | HTTPException:
    user = get_user_or_raise_401(token)
    if not user.is_admin:
        raise HTTPException(status_code=401)
    return True

UserAuthDep = Annotated[User, Depends(get_current_user)]
