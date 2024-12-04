import os
import sys
import re

import pandas as pd
from colorama import Fore, Style, init

CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, '..')))
from app.common.generate_pswd import get_password_hash  # noqa: E402

init(autoreset=True)
USERS_FILE_PATH: str = os.path.join(CURRENT_DIR, 'users.csv')
EMAIL_PATTERN: str = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


def main():
    """Добавление логина и захешированного пароля в файл с пользователями."""
    user_email = input(
        Fore.BLUE + Style.BRIGHT + 'Введите email пользователя: ' +
        Fore.WHITE + Style.NORMAL
    ).strip()

    if not re.match(EMAIL_PATTERN, user_email):
        raise ValueError(Fore.RED + Style.NORMAL + 'Некорректный email.')

    df = pd.read_csv(USERS_FILE_PATH)

    if user_email in df['useremail'].values:
        raise ValueError(Fore.RED + Style.NORMAL + 'Email уже существует.')

    user_password = input(
        Fore.GREEN + Style.BRIGHT + 'Введите пароль пользователя: ' +
        Fore.WHITE + Style.NORMAL
    ).strip()

    if len(user_password) < 8:
        raise ValueError(
            Fore.GREEN + Style.BRIGHT +
            'Пароль должен содержать минимум 10 символов.'
        )

    hashed_password = get_password_hash(user_password)

    new_user = {
        'useremail': user_email,
        'hashed_password': hashed_password
    }
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    df.to_csv(USERS_FILE_PATH, index=False)
    print(Fore.GREEN + Style.BRIGHT + 'Пользователь добавлен успешно!')


if __name__ == '__main__':
    while True:
        try:
            add_new_user = input(
                Fore.WHITE + Style.DIM +
                'Добавить нового пользователя? (Y/N): '
            )
            if add_new_user.lower() not in ('y', 'n'):
                continue
            elif add_new_user.lower() == 'n':
                break

            main()
        except ValueError as e:
            print(e)
        except KeyboardInterrupt:
            print(
                Fore.BLUE + Style.DIM +
                '\nПрограмма завершена.'
            )
            break  # Завершаем программу после обработки прерывания
