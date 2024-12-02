import os

log_dir: str = os.path.join(
    os.path.dirname(__file__), '..', 'log'
)
log_name = 'web.log'
os.makedirs(log_dir, exist_ok=True)
log_file_path: str = os.path.join(log_dir, log_name)

web_log_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": log_file_path,
            "formatter": "default",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {  # Корневой логгер.
            "handlers": ["file"],  # Логи будут выводиться только в файл,
                                   # добавить в консоль: ["console", "file"].
            "level": "ERROR",
            "propagate": True,
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
