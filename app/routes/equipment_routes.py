import os
import sys
from math import pi

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional


CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(
    os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', '..'))
)
from settings.config import web_settings  # noqa: E402
from app.common.authorization import get_current_user  # noqa: E402
from db.db_conn import execution_query  # noqa: E402


prefix = web_settings.WEB_PREFIX
router = APIRouter(prefix=prefix)
static_url = web_settings.WEB_STATIC_URL

directory: str = os.path.join(CURRENT_DIR, '..', '..', 'templates')
templates = Jinja2Templates(directory=directory)

POINTER_GPS = float | str
POINTER_POLES = list[tuple]
NULL_VALUE: str = 'NaN'
EARTH_RADIUS: int = 6378100


@router.get('/rhu', response_class=HTMLResponse)
async def get_equipment(
    response: Response,
    request: Request
) -> Response:
    """Страница с формами для внесения информации об оборудовании."""
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=ваша сессия истекла',
            status_code=status.HTTP_303_SEE_OTHER
        )

    user = await get_current_user(token)
    if not user:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=пользователь не найден',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Метод pop а не get, чтобы при перезагрузке страницы обнулять данные
    # в сессии.
    post_context: Optional[dict] = None
    if 'equipment_context' in request.session:
        post_context = request.session.pop('equipment_context')

    get_context: dict = {
        'prefix': prefix,
        'static_url': static_url,
        'db_pole_number': NULL_VALUE,
        'counter_number_1': '',
        'controller_number': '',
        'cabinet_number': '',
        'equipment_status': 'unknown',
        'new_modem_pole': None,
    }

    context = post_context if post_context is not None else get_context
    context['useremail'] = user['useremail']
    context['request'] = request

    return templates.TemplateResponse('equipment.html', context)


@router.post('/rhu', response_class=HTMLResponse)
async def equipment_post(
    response: Response,
    request: Request,
    controller_number: Optional[str] = Form(alias="controller_number"),
    new_modem_pole: Optional[str] = Form(
        alias="new_modem_pole", default=None
    ),
    cabinet_number: Optional[str] = Form(alias="cabinet_number"),
    counter_number_1: Optional[str] = Form(alias="counter_number_1")
) -> Response:
    """Обработка формы с POST-запросом."""
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=ваша сессия истекла',
            status_code=status.HTTP_303_SEE_OTHER
        )

    user = await get_current_user(token)
    if not user:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=пользователь не найден',
            status_code=status.HTTP_303_SEE_OTHER
        )

    if not all((controller_number, cabinet_number, counter_number_1)):
        if 'equipment_context' in request.session:
            request.session.pop('equipment_context')
            return RedirectResponse(
                url=f"{prefix}/rhu", status_code=status.HTTP_303_SEE_OTHER
            )

    if controller_number is not None:
        controller_number = controller_number.rstrip()
    if cabinet_number is not None:
        cabinet_number = cabinet_number.rstrip()
    if counter_number_1 is not None:
        counter_number_1 = counter_number_1.rstrip()
    if new_modem_pole is not None:
        new_modem_pole = new_modem_pole.rstrip()

    if controller_number:
        query_filter = f'ModemSerial = \'{controller_number}\''
    elif cabinet_number:
        query_filter = f'ModemCabinetSerial = \'{cabinet_number}\''
    else:
        query_filter = f'CounterID = \'{counter_number_1}\''

    data = execution_query(
        f"""
        SELECT TOP 3
            RTRIM(ct.CounterID) AS CounterID,
            RTRIM(md.ModemPole) AS ModemPole,
            RTRIM(md.ModemSerial) AS ModemSerial,
            RTRIM(md.ModemCabinetSerial) AS ModemCabinetSerial,
            RTRIM(md.ModemStatus) AS ModemStatus,
            RTRIM(md.ModemLatitude) AS ModemLatitude,
            RTRIM(md.ModemLongtitude) AS ModemLongtitude,
            RTRIM(md.NewModemPole) AS NewModemPole
        FROM
            MSys_Modems AS md
            LEFT JOIN MSys_Counters AS ct
            ON md.ModemID = ct.CounterModem
        WHERE
            {query_filter}
            AND md.ModemLevel IN (2, 102);
        """
    )

    data_problem: bool = False
    two_counters: bool = False
    bad_status: bool = False
    modem_lat: Optional[POINTER_GPS] = None
    modem_long: Optional[POINTER_GPS] = None
    gps_problem: bool = False
    nearest_poles_data: Optional[POINTER_POLES] = None

    db_pole_number: str = NULL_VALUE
    counter_number_2: Optional[str] = None
    db_new_modem_pole: str = None

    if not data:
        equipment_status: str = 'Нет данных'
        data_problem = True
    elif len(data) > 2:
        equipment_status: str = 'Уточните номер контроллера и/или номер шкафа'
        data_problem = True
    else:
        counter_number_1: str = data[0][0]
        db_pole_number: str = data[0][1]
        controller_number: str = data[0][2]
        cabinet_number: str = data[0][3]
        db_new_modem_pole: Optional[str] = data[0][7]

        if len(data) == 2:
            two_counters = True
            counter_number_2 = data[1][0]
        equipment_status: int = int(data[0][4])

        if equipment_status in (1000, 1004):
            equipment_status = 'ONLINE'
        else:
            bad_status = True
            equipment_status = 'OFFLINE'
        modem_lat: POINTER_GPS = float(
            data[0][5]) if data[0][5] else NULL_VALUE
        modem_long: POINTER_GPS = float(
            data[0][6]) if data[0][6] else NULL_VALUE

    if modem_lat in {None, NULL_VALUE} or modem_long in {None, NULL_VALUE}:
        gps_problem = True
    else:
        lat_start_rad: float = modem_lat * pi / 180
        lon_start_rad: float = modem_long * pi / 180
        nearest_poles_data = execution_query(
            f"""
            SELECT TOP 3
                RTRIM(PoleID) AS PoleID,
                {EARTH_RADIUS} * ACOS(
                    SIN({lat_start_rad}) * SIN(Radians(PoleLatitude))
                    + COS({lat_start_rad}) * COS(Radians(PoleLatitude))
                    * COS(Radians(PoleLongtitude) - {lon_start_rad})
                ) AS Distance,
                RTRIM(PoleOnAirDate) AS PoleOnAirDate
            FROM MSys_Poles
            WHERE {EARTH_RADIUS} * ACOS(
                SIN({lat_start_rad}) * SIN(Radians(PoleLatitude))
                + COS({lat_start_rad}) * COS(Radians(PoleLatitude))
                * COS(Radians(PoleLongtitude) - {lon_start_rad})
            ) BETWEEN 0 AND {EARTH_RADIUS}
            ORDER BY Distance;
            """
        )
        nearest_poles_data: POINTER_POLES = [
            (
                row[0], round(row[1]), row[2] if row[2] else NULL_VALUE
            ) for row in nearest_poles_data
        ]

    good_notification: bool = False
    pole_updated_message: Optional[str] = None

    if new_modem_pole and not data_problem:
        check_new_modem_pole = execution_query(
            f"""
            SELECT COUNT(*)
            FROM MSys_Poles
            WHERE PoleID LIKE '{new_modem_pole}%'
            """
        )[0][0]
        if check_new_modem_pole == 1 and new_modem_pole != db_new_modem_pole:
            execution_query(
                f"""
                UPDATE MSys_Modems
                SET
                    NewModemPole = (
                        SELECT TOP 1 PoleID
                        FROM Msys_Poles
                        WHERE PoleID LIKE '{new_modem_pole}%'
                    )
                WHERE
                    {query_filter}
                    AND ModemLevel IN (2, 102);
                """
            )
            db_new_modem_pole = execution_query(
                f"""
                SELECT TOP 1 RTRIM(PoleID)
                FROM Msys_Poles
                WHERE PoleID LIKE '{new_modem_pole}%'
                """
            )[0][0]
            good_notification = True
            pole_updated_message = 'Данные обновлены.'
        elif check_new_modem_pole == 0:
            pole_updated_message = f'Опора {new_modem_pole} отсутствует в БД'
        elif check_new_modem_pole > 1:
            pole_updated_message = (
                f'Уточните новый шифр опоры: {new_modem_pole}'
            )

    new_modem_pole = db_new_modem_pole or new_modem_pole

    request.session['equipment_context'] = {
        'prefix': prefix,
        'static_url': static_url,
        'db_pole_number': db_pole_number,
        'counter_number_1': counter_number_1,
        'counter_number_2': counter_number_2,
        'controller_number': controller_number,
        'cabinet_number': cabinet_number,
        'equipment_status': equipment_status,
        'data_problem': data_problem,
        'two_counters': two_counters,
        'bad_status': bad_status,
        'gps_problem': gps_problem,
        'nearest_poles_data': nearest_poles_data,
        'new_modem_pole': new_modem_pole,
        'pole_updated_message': pole_updated_message,
        'good_notification': good_notification,
    }

    return RedirectResponse(
        url=f"{prefix}/rhu", status_code=status.HTTP_303_SEE_OTHER
    )
