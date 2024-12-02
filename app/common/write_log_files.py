import os
import logging
from logging import Logger


DEFAULT_LOG_DIR: str = os.path.join(
    os.path.dirname(__file__), '..', '..', 'log'
)


def write_log_files(
    log_name: str,
    log_dir: str = DEFAULT_LOG_DIR,
    log_level: str = 'INFO'
) -> Logger:
    """
    Настройка логирования в приложении.

    Args:
        name (str): Имя логгера.
        level (str): Уровень логирования (DEBUG, INFO, WARNING, ERROR,
        CRITICAL).

    Raises:
        ValueError: Некорректный уровень логирования.
    """

    log_levels: dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    if log_level not in log_levels:
        raise ValueError(
            f'Недопустимый уровень логирования: {log_level}. ' +
            f'Допустимые значения: {list(log_levels.keys())}'
        )

    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f'{log_name}.log')

    # Настройка логгера:
    logger = logging.getLogger(log_name)
    logger.setLevel(log_levels[log_level])

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
