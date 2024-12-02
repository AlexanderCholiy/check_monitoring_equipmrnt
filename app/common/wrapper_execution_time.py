import os
import sys

from datetime import datetime, timedelta
from colorama import Fore, Style
from functools import wraps


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from write_log_files import write_log_files, DEFAULT_LOG_DIR  # noqa: E402


def wrapper_execution_time(
    write_log_file: bool = False,
    log_name: str = 'execution_time',
    log_dir: str = DEFAULT_LOG_DIR,
    log_level: str = 'INFO'
) -> None:
    """
    Измерение времени выполнения функции и записи его в log файл.

    Args:
        log_name (str): Имя файла (без расширения .log).
        log_dir (str): Путь к директории для логов.
        log_level (str): Уровень логирования (DEBUG, INFO, WARNING, ERROR,
        CRITICAL).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            if write_log_file:
                logger = write_log_files(
                    log_name=log_name, log_dir=log_dir, log_level=log_level
                )
                log_method = getattr(logger, log_level.lower(), logger.info)

            try:
                if write_log_file:
                    log_method(f'Запуск функции {func.__name__}.')
                result = func(*args, **kwargs)
                return result

            finally:
                end_time = datetime.now()
                execution_time = end_time - start_time

                if execution_time.total_seconds() >= 60:
                    minutes = execution_time // timedelta(minutes=1)
                    message = (
                        f'Функция {func.__name__} выполнялась {minutes} мин.'
                    )
                elif execution_time.total_seconds() >= 1:
                    seconds = int(execution_time.total_seconds())
                    message = (
                        f'Функция {func.__name__} выполнялась {seconds} сек.'
                    )
                else:
                    mcseconds = int(execution_time.total_seconds() * 1_000_000)
                    message = (
                        f'Функция {func.__name__} выполнялась {mcseconds} мкс.'
                    )

                if write_log_file:
                    log_method(message)
                    log_message = (
                        f'Лог-файл: {log_name}.\nДиректория логов: {log_dir}.'
                    )
                    print(Fore.WHITE + Style.DIM + log_message)

                print(Fore.WHITE + Style.DIM + message)

        return wrapper

    return decorator
