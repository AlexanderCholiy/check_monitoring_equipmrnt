import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DBAPIError
from sqlalchemy.orm import sessionmaker, declarative_base
from colorama import Fore, Style

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings.config import db_settings  # noqa: E402


SQLALCHEMY_DATABASE_URL_SERVER: str = (
    f'mssql+pyodbc://{db_settings.DB_USER}:{db_settings.DB_PSWD}' +
    f'@{db_settings.DB_HOST}:{db_settings.DB_PORT}/{db_settings.DB_NAME}' +
    '?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
)

engine = create_engine(SQLALCHEMY_DATABASE_URL_SERVER)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Зависимость для управления подключениями к базе данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execution_query(query: str) -> bool | list:
    """
    Выполнение SQL запроса.
    Возвращает результат для SELECT запросов, True для запросов требующих
    COMMIT, или False в случае ошибки.

    Args:
        query (str): SQL запрос в виде строки.

    Returns:
        list | bool: результат запроса, True при успешном COMMIT, или False в
        случае ошибки.
    """
    db = SessionLocal()
    try:
        result = db.execute(text(query))

        if result.returns_rows:
            rows = result.fetchall()
            return rows
        else:
            db.commit()
            return True

    except DBAPIError as e:
        print(
            Fore.RED + Style.NORMAL + 'Ошибка при выполнении запроса:' +
            Fore.WHITE + Style.DIM + e +
            Fore.RED + Style.NORMAL + 'Запрос:' +
            Fore.WHITE + Style.DIM + query
        )
        return False

    except OperationalError as e:
        print(
            Fore.RED + Style.NORMAL + 'Ошибка при подключении к базе данных:' +
            Fore.WHITE + Style.DIM + str(e)
        )
        return False

    except SQLAlchemyError as e:
        print(
            Fore.RED + Style.DIM + 'Ошибка SQLAlchemy:' +
            Fore.WHITE + Style.DIM + e
        )
        return False

    except Exception as e:
        print(
            Fore.RED + Style.DIM + 'Неожиданная ошибка:' +
            Fore.WHITE + Style.DIM + e
        )
        return False

    finally:
        if db is not None:
            db.close()


if __name__ == '__main__':
    print(
        execution_query('SELECT TOP 10 * FROM MSys_Modems')
    )
