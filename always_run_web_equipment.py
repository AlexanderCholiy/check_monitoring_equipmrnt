import os
from datetime import datetime
from urllib.parse import unquote

from colorama import Fore, Style, init
from uvicorn import Config, Server
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from settings.config import web_settings
from settings.web_log_config import web_log_config
from app.common.wrapper_execution_time import wrapper_execution_time
from app.common.authorization import get_current_user
from app.common.write_log_files import write_log_files
from app.routes import (
    authorization_routes,
    equipment_routes
)


init(autoreset=True)

CURRENT_DIR: str = os.path.dirname(__file__)
USER_LOG_DIR: str = os.path.join('/', 'var', 'log', 'application-220')
user_loger = write_log_files('access', USER_LOG_DIR)

app = FastAPI(debug=False, title='MonitoringEquipment', version='1.0')
app.include_router(authorization_routes.router)
app.include_router(equipment_routes.router)
app.mount(
    web_settings.WEB_STATIC_URL,
    StaticFiles(directory=os.path.join(CURRENT_DIR, 'static')),
    name='static',
)

app.add_middleware(
    SessionMiddleware,
    secret_key=web_settings.WEB_MIDDLEWARE_SECRET_KEY
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Получение информации о пользователе и URL."""
    token = request.cookies.get("access_token")
    user = await get_current_user(token) if token else None
    useremail = user['useremail'] if user else 'unknown_user'
    url = request.url.path
    method = request.method
    request_time = datetime.now().strftime('%d/%b/%Y:%H:%M:%S')

    response: Response = await call_next(request)

    status_code = response.status_code
    referer = request.headers.get('referer', '')
    decoded_referer = unquote(referer)

    user_loger.info(
        f'{request.client.host} - {useremail} [{request_time}] ' +
        f'"{method} {url} HTTP/1.0" {status_code} ' +
        f'"{decoded_referer}" ' +
        f'"{request.headers.get("user-agent", "")}"'
    )

    return response


@wrapper_execution_time(write_log_file=True, log_name='run_web_server')
def start_server():
    workers = (os.cpu_count() * 2) + 1
    config = Config(
        app=app,
        host=web_settings.WEB_HOST,
        port=web_settings.WEB_PORT,
        workers=workers,
        reload=False,
        log_level='error',
        log_config=web_log_config,
    )
    server = Server(config)
    server.run()


if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    script_name_without_extension = script_name.split('.')[0]

    print(
        Fore.MAGENTA + Style.BRIGHT +
        f'Запуск файла: {script_name_without_extension}\n'
        + Fore.CYAN + Style.DIM +
        'Для отладки запускайте приложение с помощью команды: '
        + Fore.WHITE + Style.DIM +
        f'python -m uvicorn {script_name_without_extension}:app --reload '
        f'--host {web_settings.WEB_HOST} --port {web_settings.WEB_PORT} ' +
        '--workers 1\n'
        + Fore.CYAN + Style.DIM + 'Сайт: '
        + Fore.WHITE + Style.DIM +
        f'{web_settings.WEB_HOST}:{web_settings.WEB_PORT}' +
        web_settings.WEB_PREFIX
    )

    try:
        start_server()
    except (KeyboardInterrupt, SystemExit):
        print(Fore.RED + 'Сервер остановлен.')
