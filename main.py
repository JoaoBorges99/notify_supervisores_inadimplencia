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

TRUE_VALUES = {"1", "true", "yes", "sim", "s", "on"}
FALSE_VALUES = {"0", "false", "no", "nao", "não", "n", "off"}


def _is_enabled(env_name: str, default: bool = True) -> bool:
    raw = os.getenv(env_name)
    if raw is None or raw.strip() == "":
        return default

    value = raw.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False

    raise ValueError(f"{env_name} inválido: '{raw}'. Use true ou false")


def _limpar_arquivos_gerados(prefixo: str):
    pasta = "arquivos-gerados"
    if not os.path.exists(pasta):
        return

    for filename in os.listdir(pasta):
        if not filename.startswith(prefixo):
            continue

        file_path = os.path.join(pasta, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def _nome_ga(titulo) -> str:
    try:
        return str(titulo).split("-")[1].strip().upper()
    except Exception:
        return str(titulo).upper()


def _run_job_envio(
    job_label: str,
    obter_relatorio,
    mensagem: str,
    prefixo_arquivo: str,
    excel_modo: str,
):
    print(f"Execução do job '{job_label}' iniciada - {datetime.now()} ")
    _limpar_arquivos_gerados(prefixo_arquivo)

    api = ApiRequest()
    sup_data = api.get_supervisores_ativos()

    if not sup_data:
        print(f"Nenhum supervisor retornado para o job '{job_label}'.")
        print(f"Execução do job '{job_label}' finalizada - {datetime.now()} ")
        return

    for supervisor in sup_data:
        if not supervisor.get("telefone"):
            continue

        numero_limpo = re.sub(r"[^0-9]", "", supervisor["telefone"])
        nome = _nome_ga(supervisor["titulo"])

        json_relatorio = obter_relatorio(
            api,
            supervisor["codigo"],
            supervisor["titulo"],
        )

        if json_relatorio == []:
            print(
                f"Não há nenhum conteudo a ser enviado para o {supervisor['codigo']}-{str(supervisor['titulo']).upper()}"
            )
            continue

        nome_arquivo = f"{prefixo_arquivo}{supervisor['codigo']}-{datetime.now().date()}"
        caminho_arquivo = create_excel.writeExcel(
            json_relatorio,
            nome_arquivo,
            modo=excel_modo,
        )

        if _is_enabled("DRY_RUN", False):
            print(
                f"[DRY_RUN] job={job_label} ga={supervisor['codigo']}-{nome} "
                f"telefone=55{numero_limpo} arquivo={nome_arquivo}.xlsx "
                f"linhas={len(json_relatorio)}"
            )
            continue

        retorno_msg = api.send_mensagem_chatbot(
            mensagem.format(nome=nome),
            f"55{numero_limpo}",
            caminho_arquivo,
            f"{nome_arquivo}.xlsx",
        )
        print(retorno_msg)

    print(f"Execução do job '{job_label}' finalizada - {datetime.now()} ")


def run_job_inadimplencia():
    _run_job_envio(
        "inadimplencia",
        lambda api, codigo, titulo: api.relatorio_inadiplencia_filtrando_supervisor(
            codigo, titulo
        ),
        "Olá *{nome}*, segue em anexo o realtorio de inadimplência dos clientes da base de sua equipe.",
        "sup-",
        "financeiro",
    )


def run_job_cadastro_incompleto():
    _run_job_envio(
        "cadastro_incompleto",
        lambda api, codigo, titulo: api.relatorio_cadastro_incompleto_filtrando_supervisor(
            codigo, titulo
        ),
        "Olá *{nome}*, segue em anexo o relatório de clientes bloqueados por cadastro incompleto da base da sua equipe.",
        "cadastro-sup-",
        "listagem",
    )


def _parse_schedule_days(raw_days: str, env_name: str = "SCHEDULE_DAYS"):
    if not raw_days:
        raise ValueError(f"{env_name} é obrigatório. Exemplo: SEG,TER,QUA")

    days = []
    for item in raw_days.split(","):
        day = item.strip().upper()
        if day not in WEEKDAY_MAP:
            raise ValueError(
                f"Dia inválido em {env_name}: '{day}'. Use: SEG,TER,QUA,QUI,SEX,SAB,DOM"
            )
        day_value = WEEKDAY_MAP[day]
        if day_value not in days:
            days.append(day_value)

    if not days:
        raise ValueError(f"{env_name} não pode ficar vazio.")
    return days


def _parse_schedule_times(raw_times: str, env_name: str = "SCHEDULE_TIMES"):
    if not raw_times:
        raise ValueError(f"{env_name} é obrigatório. Exemplo: 08:00,12:30")

    parsed = []
    seen = set()
    for item in raw_times.split(","):
        time_str = item.strip()
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError as error:
            raise ValueError(
                f"Horário inválido em {env_name}: '{time_str}'. Formato aceito: HH:MM"
            ) from error

        key = (parsed_time.hour, parsed_time.minute)
        if key not in seen:
            seen.add(key)
            parsed.append(parsed_time)

    if not parsed:
        raise ValueError(f"{env_name} não pode ficar vazio.")

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


def _build_jobs():
    jobs = []

    if _is_enabled("INADIMPLENCIA_ENABLED", True):
        jobs.append(
            {
                "name": "inadimplencia",
                "days": _parse_schedule_days(
                    os.getenv("SCHEDULE_DAYS", ""), "SCHEDULE_DAYS"
                ),
                "times": _parse_schedule_times(
                    os.getenv("SCHEDULE_TIMES", ""), "SCHEDULE_TIMES"
                ),
                "run": run_job_inadimplencia,
            }
        )

    if _is_enabled("CADASTRO_ENABLED", True):
        jobs.append(
            {
                "name": "cadastro_incompleto",
                "days": _parse_schedule_days(
                    os.getenv("CADASTRO_SCHEDULE_DAYS", "SEG"),
                    "CADASTRO_SCHEDULE_DAYS",
                ),
                "times": _parse_schedule_times(
                    os.getenv("CADASTRO_SCHEDULE_TIMES", "08:00"),
                    "CADASTRO_SCHEDULE_TIMES",
                ),
                "run": run_job_cadastro_incompleto,
            }
        )

    if not jobs:
        raise ValueError(
            "Nenhum job habilitado. Defina INADIMPLENCIA_ENABLED e/ou CADASTRO_ENABLED como true."
        )

    return jobs


def _executar_job(job):
    print(f"Disparo do job '{job['name']}' iniciado")
    try:
        job["run"]()
    except Exception as error:
        print(f"Falha no job '{job['name']}': {error}")


def _executar_jobs_habilitados():
    jobs = _build_jobs()
    for job in jobs:
        _executar_job(job)


def _format_times(times):
    return ",".join(t.strftime("%H:%M") for t in times)


def run_scheduler():
    timezone, timezone_name = _get_timezone()
    jobs = _build_jobs()

    jobs_info = " | ".join(
        f"{job['name']} dias={os.getenv('SCHEDULE_DAYS') if job['name'] == 'inadimplencia' else os.getenv('CADASTRO_SCHEDULE_DAYS', 'SEG')} horários={_format_times(job['times'])}"
        for job in jobs
    )
    print(f"Scheduler iniciado | timezone={timezone_name} | {jobs_info}")

    last_run_keys = {job["name"]: None for job in jobs}
    while True:
        now = datetime.now(timezone)
        current_day = now.weekday()

        for job in jobs:
            if current_day not in job["days"]:
                continue

            for schedule_time in job["times"]:
                if now.hour == schedule_time.hour and now.minute == schedule_time.minute:
                    current_key = (
                        now.date().isoformat(),
                        current_day,
                        now.hour,
                        now.minute,
                    )
                    if last_run_keys[job["name"]] != current_key:
                        print(
                            f"Disparo agendado [{job['name']}] em {now.isoformat()}"
                        )
                        _executar_job(job)
                        last_run_keys[job["name"]] = current_key
                    break

        time.sleep(20)


def main():
    load_dotenv()
    _get_timezone()
    run_mode = os.getenv("RUN_MODE", "once").strip().lower()

    if run_mode == "once":
        _executar_jobs_habilitados()
        return

    if run_mode == "scheduler":
        run_scheduler()
        return

    raise ValueError(
        f"RUN_MODE inválido: '{run_mode}'. Valores aceitos: once ou scheduler"
    )


if __name__ == "__main__":
    main()
