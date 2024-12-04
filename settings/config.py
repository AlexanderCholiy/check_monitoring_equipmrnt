import os

from dotenv import load_dotenv

env_path: str = os.path.join(
    os.path.dirname(__file__), '.env'
)
load_dotenv(env_path)


class WebSettings:
    """Параметры подключения приложения и настройки безопасности."""
    WEB_HOST: str = os.getenv('WEB_HOST')
    WEB_PORT: int = int(os.getenv('WEB_PORT'))
    WEB_PREFIX: str = '/rhu-update'
    WEB_STATIC_URL: str = '/equipment-static'
    WEB_SECURITY_SECRET_KEY: str = os.getenv('WEB_SECURITY_SECRET_KEY')
    WEB_MIDDLEWARE_SECRET_KEY: str = os.getenv('WEB_MIDDLEWARE_SECRET_KEY')
    WEB_SECURITY_ALGORITHM: str = os.getenv('WEB_SECURITY_ALGORITHM')
    WEB_SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS: int = int(
        os.getenv('WEB_SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS')
    )


web_settings = WebSettings()


class DbSettings:
    """Параметры подключения к базе данных."""
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = int(os.getenv('DB_PORT'))
    DB_USER: str = os.getenv('DB_USER')
    DB_PSWD: str = os.getenv('DB_PSWD')
    DB_NAME: str = os.getenv('DB_NAME')


db_settings = DbSettings()
