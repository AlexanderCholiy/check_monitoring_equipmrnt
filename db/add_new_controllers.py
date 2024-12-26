import os
import sys

import pandas as pd

CURRENT_DIR: str = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, '..')))
from db.db_conn import execution_query  # noqa: E402


def add_new_controllers():
    """Добавление новых контроллеров в БД."""
    df = pd.read_excel(
        os.path.join(CURRENT_DIR, '..', 'data', 'new_equipment.xlsx'),
        'new_rhu'
    )
    count_df: int = len(df)

    for index, row in df.iterrows():
        modem_version: str = str(row.ModemVersion).strip()
        modem_serial: str = str(row.ModemSerial).strip()
        modem_counter: str = str(row.ModemCounter).strip()
        modem_imsi: str = str(row.ModemIMSI).replace('\'', '').strip()
        modem_id: str = str(row.ModemID).strip()
        modem_msisdn: str = str(row.ModemMsisdn).strip()
        counter_id: str = str(row.CounterID).strip()
        modem_cabinet_serial: str = str(row.ModemCabinetSerial).strip()

        try:
            if modem_id != '10.28.19.233':
                continue
            # Добавляем/обновляем данные о новом контроллере:
            execution_query(
                f"""
                MERGE INTO MSys_Modems AS Target
                USING (VALUES (
                    '{modem_id}',
                    102,
                    '{modem_msisdn}',
                    '{modem_counter}',
                    '{modem_serial}',
                    '{modem_imsi}',
                    '{modem_cabinet_serial}',
                    '{modem_version}',
                    1001,
                    'undefined'
                )) AS Source (
                    ModemID,
                    ModemLevel,
                    ModemMsisdn,
                    ModemCounter,
                    ModemSerial,
                    ModemIMSI,
                    ModemCabinetSerial,
                    ModemVersion,
                    ModemStatus,
                    ModemPole
                )
                ON Target.ModemID = Source.ModemID
                AND Target.ModemLevel = Source.ModemLevel
                WHEN MATCHED THEN
                    UPDATE SET
                        ModemMsisdn = Source.ModemMsisdn,
                        ModemCounter = Source.ModemCounter,
                        ModemSerial = Source.ModemSerial,
                        ModemIMSI = Source.ModemIMSI,
                        ModemCabinetSerial = Source.ModemCabinetSerial,
                        ModemVersion = Source.ModemVersion
                WHEN NOT MATCHED THEN
                    INSERT (
                        ModemID,
                        ModemLevel,
                        ModemMsisdn,
                        ModemCounter,
                        ModemSerial,
                        ModemIMSI,
                        ModemCabinetSerial,
                        ModemVersion,
                        ModemStatus,
                        ModemPole
                    )
                    VALUES (
                        Source.ModemID,
                        Source.ModemLevel,
                        Source.ModemMsisdn,
                        Source.ModemCounter,
                        Source.ModemSerial,
                        Source.ModemIMSI,
                        Source.ModemCabinetSerial,
                        Source.ModemVersion,
                        Source.ModemStatus,
                        Source.ModemPole
                    );
                """
            )

            # Добавляем/обновляем данные о новом счетчике:
            execution_query(
                f"""
                MERGE INTO MSys_Counters AS Target
                USING (
                    VALUES ('{counter_id}', '{modem_id}', 5000, 0, 200)
                ) AS Source (
                    CounterID,
                    CounterModem,
                    CounterStatus,
                    CounterNumber,
                    CounterOp
                )
                ON Target.CounterID = Source.CounterID
                WHEN MATCHED THEN
                    UPDATE SET
                        CounterModem = Source.CounterModem,
                        CounterStatus = Source.CounterStatus,
                        CounterNumber = Source.CounterNumber,
                        CounterOp = Source.CounterOp
                WHEN NOT MATCHED THEN
                    INSERT (
                        CounterID,
                        CounterModem,
                        CounterStatus,
                        CounterNumber,
                        CounterOp
                    )
                    VALUES (
                        Source.CounterID,
                        Source.CounterModem,
                        Source.CounterStatus,
                        Source.CounterNumber,
                        Source.CounterOp
                    );
                """
            )

        except Exception:
            ...
        else:
            print(
                'Обновляем MSys_Modems: ' +
                f'{round((100*(index + 1) / count_df), 2)}%',
                end='\r'
            )

    print()


if __name__ == '__main__':
    add_new_controllers()
