from passlib.context import CryptContext


# an instance of the CryptContext class that specifies the hashing algorithm - bcrypt in this case
pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_pass(password: str) -> str:
    return pass_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pass_context.verify(plain_password, hashed_password)
