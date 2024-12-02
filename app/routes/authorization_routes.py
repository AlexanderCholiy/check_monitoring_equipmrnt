import os
import sys
from datetime import timedelta

from fastapi import APIRouter, Request, status, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates


CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(
    os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', '..'))
)
from settings.config import web_settings  # noqa: E402
from app.common.authorization import (  # noqa: E402
    authenticate_user, create_access_token
)


prefix = web_settings.WEB_PREFIX
router = APIRouter(prefix=prefix)
static_url = web_settings.WEB_STATIC_URL

directory: str = os.path.join(CURRENT_DIR, '..', '..', 'templates')
templates = Jinja2Templates(directory=directory)


@router.get('/', response_class=RedirectResponse)
async def index(
    request: Request, token: str | None = None
) -> RedirectResponse:
    """
    Проверка токена аутентификации для доступа к главной странице приложения.
    Если токен действителен и пользователь существует, отображается домашняя
    страница. В противном случае пользователь перенаправляется на страницу
    авторизации.
    """
    token = request.cookies.get('access_token')
    if token:
        return RedirectResponse(
            url=f'{prefix}/monitoring', status_code=status.HTTP_303_SEE_OTHER
        )
    return RedirectResponse(
        url=f'{prefix}/authorize', status_code=status.HTTP_303_SEE_OTHER
    )


@router.get('/authorize')
async def authorize(request: Request) -> HTMLResponse:
    """Страница авторизации пользователя."""
    error = request.query_params.get('error')
    context: dict = {
        'request': request,
        'static_url': static_url,
        'prefix': prefix,
        'error': error
    }
    return templates.TemplateResponse('authorization.html', context)


@router.post('/token', response_class=RedirectResponse)
async def login_for_access_token(
    request: Request,
    useremail: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False)
) -> RedirectResponse:
    """
    Если аутентификация успешна, создается токен доступа. Токен содержит данные
    о пользователе (в данном случае его электронную почту) и устанавливает
    время действия токена. Если пользователь не найден или не правильный логин
    и(или) пароль, тогда происходит перенаправление на страницу авторизации с
    сообщением об ошибке.
    """

    user = authenticate_user(useremail, password)
    if isinstance(user, int):
        error_messages = {
            1001: 'пользователь не найден',
            1002: 'неправильный логин или пароль'
        }

        response = RedirectResponse(
            url=f'{prefix}/authorize?error={error_messages[user]}',
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.delete_cookie('access_token')
        response.delete_cookie('saved_password')
        return response

    access_token_expires = timedelta(
        minutes=web_settings.WEB_SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS
    )
    access_token = create_access_token(
        user_data={'sub': user['useremail']},
        expires_delta=access_token_expires
    )

    response = RedirectResponse(
        url=f'{prefix}/monitoring', status_code=status.HTTP_303_SEE_OTHER
    )
    cookie_time = web_settings.WEB_SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS
    response.set_cookie(
        key='access_token',
        value=f'Bearer {access_token}',
        httponly=True,
        max_age=cookie_time
    )

    if remember_me:
        response.set_cookie(
            key='saved_useremail', value=useremail, max_age=cookie_time
        )
        response.set_cookie(
            key='saved_password', value=password, max_age=cookie_time
        )
        response.set_cookie(
            key='remember_me', value='true', max_age=cookie_time
        )
    else:
        response.delete_cookie('saved_useremail')
        response.delete_cookie('saved_password')
        response.delete_cookie('remember_me')

    return response


@router.get('/logout')
@router.post('/logout', response_class=RedirectResponse)
async def logout(request: Request) -> RedirectResponse:
    """
    Выход пользователя из системы, удаление токена и перенаправление на
    страницу авторизации.
    """
    response = RedirectResponse(
        url=f'{prefix}/authorize', status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie('access_token')
    return response
