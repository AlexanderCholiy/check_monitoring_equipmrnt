import os
import sys

import pandas as pd
from fastapi import Depends
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
from pydantic import EmailStr

CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, '..', '..')))
from settings.config import web_settings  # noqa: E402
from generate_pswd import verify_password, oauth2_scheme  # noqa: E402

USER_DATA_CSV: str = os.path.join(
    CURRENT_DIR, '..', '..', 'settings', 'users.csv'
)


def load_user_data() -> pd.DataFrame:
    """Загружает данные пользователей из CSV-файла."""
    return pd.read_csv(USER_DATA_CSV, quotechar='"', encoding='utf-8')


def authenticate_user(useremail: EmailStr, password: str) -> dict | int:
    """
    Авторизация пользователя:
    - если запись с пользователем отсутствует -> 1001;
    - если логин/пароль неверный -> 1002;
    - если всё в порядке -> словарь с данными пользователя.
    """
    user_data = load_user_data()
    user_row = user_data[user_data['useremail'] == useremail]
    if user_row.empty:
        return 1001

    user = user_row.iloc[0].to_dict()

    if not verify_password(password, user["hashed_password"]):
        return 1002

    return user


def create_access_token(
    user_data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Создаем JWT токен для пользователя."""
    to_encode = user_data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})  # Добавляем время истечения токена.
    encoded_jwt = jwt.encode(
        to_encode,
        web_settings.WEB_SECURITY_SECRET_KEY,
        algorithm=web_settings.WEB_SECURITY_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> Optional[dict]:
    """
    Функция предназначена для извлечения информации о текущем пользователе из
    предоставленного токена.
    """
    try:
        token = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(
            token,
            web_settings.WEB_SECURITY_SECRET_KEY,
            algorithms=[web_settings.WEB_SECURITY_ALGORITHM],
        )
        email: Optional[str] = payload.get("sub")
        if email is None:
            return None

        user_data = load_user_data()
        user_row = user_data[user_data['useremail'] == email]
        if user_row.empty:
            return None

        user = user_row.iloc[0].to_dict()
        return user
    except JWTError:
        return None


if __name__ == '__main__':
    print(authenticate_user('user2@example.com', 'qwerty2'))
