import os
import re
import shutil
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

import create_excel
from api_request import ApiRequest

WEEKDAY_MAP = {
    "SEG": 0,
    "TER": 1,
    "QUA": 2,
    "QUI": 3,
    "SEX": 4,
    "SAB": 5,
    "DOM": 6,
}


def get_relatorio_por_supervisor():
    print(f"Execução do envio de mensgens iniciada - {datetime.now()} ")

    if os.path.exists("arquivos-gerados"):
        for filename in os.listdir("arquivos-gerados"):
            file_path = os.path.join("arquivos-gerados", filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    sup_data = ApiRequest().get_supervisores_ativos()

    for supervisor in sup_data:
        if supervisor["telefone"] is not None:
            numero_limpo = re.sub(r"[^0-9]", "", supervisor["telefone"])

            try:
                nome = str(supervisor["titulo"]).split("-")[1].strip().upper()
            except Exception:
                nome = str(supervisor["titulo"]).upper()

            json_relatorio = ApiRequest().relatorio_inadiplencia_filtrando_supervisor(
                supervisor["codigo"],
                supervisor["titulo"],
            )

            if json_relatorio == []:
                print(
                    f"Não há nenhum conteudo a ser enviado para o {supervisor['codigo']}-{str(supervisor['titulo']).upper()}"
                )
                continue

            caminho_arquivo = create_excel.writeExcel(
                json_relatorio,
                f"sup-{supervisor['codigo']}-{datetime.now().date()}",
            )

            retorno_msg = ApiRequest().send_mensagem_chatbot(
                f"Olá *{nome}*, segue em anexo o realtorio de inadimplência dos clientes da base de sua equipe.",
                #'5533991461098',
                f"55{numero_limpo}",
                caminho_arquivo,
                f"sup-{supervisor['codigo']}-{datetime.now().date()}.xlsx",
            )
            print(retorno_msg)

    print(f"Execução finalizada - {datetime.now()} ")


def _parse_schedule_days(raw_days: str):
    if not raw_days:
        raise ValueError("SCHEDULE_DAYS é obrigatório. Exemplo: SEG,TER,QUA")

    days = []
    for item in raw_days.split(","):
        day = item.strip().upper()
        if day not in WEEKDAY_MAP:
            raise ValueError(
                f"Dia inválido em SCHEDULE_DAYS: '{day}'. Use: SEG,TER,QUA,QUI,SEX,SAB,DOM"
            )
        day_value = WEEKDAY_MAP[day]
        if day_value not in days:
            days.append(day_value)

    if not days:
        raise ValueError("SCHEDULE_DAYS não pode ficar vazio.")
    return days


def _parse_schedule_times(raw_times: str):
    if not raw_times:
        raise ValueError("SCHEDULE_TIMES é obrigatório. Exemplo: 08:00,12:30")

    parsed = []
    seen = set()
    for item in raw_times.split(","):
        time_str = item.strip()
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError as error:
            raise ValueError(
                f"Horário inválido em SCHEDULE_TIMES: '{time_str}'. Formato aceito: HH:MM"
            ) from error

        key = (parsed_time.hour, parsed_time.minute)
        if key not in seen:
            seen.add(key)
            parsed.append(parsed_time)

    if not parsed:
        raise ValueError("SCHEDULE_TIMES não pode ficar vazio.")

    return sorted(parsed, key=lambda t: (t.hour, t.minute))


def _get_timezone():
    timezone_name = os.getenv("TIMEZONE", "").strip()
    if not timezone_name:
        raise ValueError("TIMEZONE é obrigatório. Use: TIMEZONE=America/Sao_Paulo")

    try:
        return ZoneInfo(timezone_name), timezone_name
    except Exception as error:
        raise ValueError(
            f"TIMEZONE inválido: '{timezone_name}'. Exemplo válido: America/Sao_Paulo"
        ) from error


def run_scheduler():
    timezone, timezone_name = _get_timezone()
    schedule_days = _parse_schedule_days(os.getenv("SCHEDULE_DAYS", ""))
    schedule_times = _parse_schedule_times(os.getenv("SCHEDULE_TIMES", ""))

    print(
        f"Scheduler iniciado | timezone={timezone_name} | dias={os.getenv('SCHEDULE_DAYS')} | horários={os.getenv('SCHEDULE_TIMES')}"
    )

    last_run_key = None
    while True:
        now = datetime.now(timezone)
        current_day = now.weekday()
        current_key = (now.date().isoformat(), current_day, now.hour, now.minute)

        if current_day in schedule_days:
            for schedule_time in schedule_times:
                if now.hour == schedule_time.hour and now.minute == schedule_time.minute:
                    if last_run_key != current_key:
                        print(f"Disparo agendado em {now.isoformat()}")
                        get_relatorio_por_supervisor()
                        last_run_key = current_key
                    break

        # Evita alto consumo e executa com precisão suficiente para minuto.
        time.sleep(20)


def main():
    load_dotenv()
    _get_timezone()
    run_mode = os.getenv("RUN_MODE", "once").strip().lower()

    if run_mode == "once":
        get_relatorio_por_supervisor()
        return

    if run_mode == "scheduler":
        run_scheduler()
        return

    raise ValueError(
        f"RUN_MODE inválido: '{run_mode}'. Valores aceitos: once ou scheduler"
    )


if __name__ == "__main__":
    main()