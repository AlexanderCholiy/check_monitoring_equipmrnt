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


@router.get('/equipment', response_class=HTMLResponse)
async def get_equipment(response: Response, request: Request) -> Response:
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
        'pole_number': NULL_VALUE,
        'counter_number_1': NULL_VALUE,
        'controller_number': '',
        'cabinet_number': '',
        'equipment_status': 'unknown'
    }
    return templates.TemplateResponse('equipment.html', context)


@router.post('/equipment', response_class=HTMLResponse)
async def equipment_post(
    response: Response,
    request: Request,
    counter_number_1: str = Form(alias="counter_number_1"),
    counter_number_2: Optional[str] = Form(
        alias="counter_number_2", default=NULL_VALUE
    ),
    controller_number: str = Form(alias="controller_number"),
    pole_number: str = Form(alias="pole_number"),
    cabinet_number: str = Form(alias="cabinet_number")
) -> Response:
    """Обработка формы с POST-запросом."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(
            url=f'{prefix}/authorize?error=ваша сессия истекла',
            status_code=status.HTTP_303_SEE_OTHER
        )
    user = await get_current_user(token)
    counter_number_1 = counter_number_1.rstrip()
    counter_number_2 = counter_number_2.rstrip()
    controller_number = controller_number.rstrip()
    pole_number = pole_number.rstrip()
    cabinet_number = cabinet_number.rstrip()

    if not controller_number:
        query_filter = f'md.ModemCabinetSerial LIKE \'{cabinet_number}%\''
    elif not cabinet_number:
        query_filter = f'md.ModemSerial LIKE \'{controller_number}%\''
    else:
        query_filter = (
            f'(md.ModemSerial LIKE \'{controller_number}%\'' +
            f'OR md.ModemCabinetSerial LIKE \'{cabinet_number}%\')'
        )

    data = execution_query(
        f"""
        SELECT TOP 3
            RTRIM(ct.CounterID) AS CounterID,
            RTRIM(md.ModemPole) AS ModemPole,
            RTRIM(md.ModemSerial) AS ModemSerial,
            RTRIM(md.ModemCabinetSerial) AS ModemCabinetSerial,
            RTRIM(md.ModemStatus) AS ModemStatus,
            RTRIM(md.ModemLatitude) AS ModemLatitude,
            RTRIM(md.ModemLongtitude) AS ModemLongtitude
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

    if not data:
        equipment_status: str = 'Нет данных'
        pole_number: str = NULL_VALUE
        counter_number_1: str = NULL_VALUE
        data_problem = True
    elif len(data) > 2:
        equipment_status: str = 'Уточните номер контроллера и/или номер шкафа'
        pole_number: str = NULL_VALUE
        counter_number_1: str = NULL_VALUE
        data_problem = True
    else:
        counter_number_1: str = data[0][0]
        pole_number: str = data[0][1]
        controller_number: str = data[0][2]
        cabinet_number: str = data[0][3]
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
        print(type(modem_lat))
        print(modem_lat)
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
                ) AS Distance
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
            (row[0], round(row[1])) for row in nearest_poles_data
        ]
        print(nearest_poles_data)

    print(data)

    context: dict = {
        'request': request,
        'prefix': prefix,
        'static_url': static_url,
        'useremail': user['useremail'],
        'pole_number': pole_number,
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
    }
    return templates.TemplateResponse('equipment.html', context)
