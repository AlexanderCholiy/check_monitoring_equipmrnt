import os
import sys

from fastapi import APIRouter, Request, status
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(
    os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', '..'))
)
from settings.config import web_settings  # noqa: E402
from app.common.authorization import get_current_user  # noqa: E402


prefix = web_settings.WEB_PREFIX
router = APIRouter(prefix=prefix)
static_url = web_settings.WEB_STATIC_URL

directory: str = os.path.join(CURRENT_DIR, '..', '..', 'templates')
templates = Jinja2Templates(directory=directory)


@router.get('/equipment', response_class=HTMLResponse)
async def equipment(response: Response, request: Request) -> Response:
    """Страница с формами для внесения информации об оборудовании."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=ваша сессия истекла',
            status_code=status.HTTP_303_SEE_OTHER
        )
    user = await get_current_user(token)
    context: dict = {
        'request': request,
        'prefix': prefix,
        'static_url': static_url,
        'useremail': user['useremail'],
        'pole-number': 'NaN',
        'counter-number': 'NaN',
        'controller-number': '',
        'cabinet-number': '',
        'status': 'unknown',
    }
    return templates.TemplateResponse('equipment.html', context)
