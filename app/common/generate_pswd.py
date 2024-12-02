from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сравнимваем обычный введенный пароль пользователя с тем, что хранится в БД.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Преобразуем обычный пароль пользователя в зашифрованный, который уже будет
    храниться в БД.
    """
    return pwd_context.hash(password)


if __name__ == '__main__':
    password = 'qwerty2'
    hashed_password = get_password_hash(password=password)
    print(hashed_password)
