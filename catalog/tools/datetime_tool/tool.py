import os
from datetime import datetime


def ptbr_formatted_datetime() -> str:
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                   "Sexta-feira", "Sábado", "Domingo"]
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    now = datetime.now()
    return f"{dias_semana[now.weekday()]}, {now.day} de {meses[now.month - 1]} de {now.year}, {now.strftime('%H:%M:%S')}"


def enus_formatted_datetime() -> str:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    now = datetime.now()
    return f"{weekdays[now.weekday()]}, {months[now.month - 1]} {now.day}, {now.year}, {now.strftime('%H:%M:%S')}"



def formatted_date_today() -> str:
    language = os.getenv("DATETIME_LANGUAGE", "pt")

    dispatch_map = {
        "pt": ptbr_formatted_datetime,
        "en": enus_formatted_datetime,
    }

    if language in dispatch_map:
        result = dispatch_map[language]()
        return result.rsplit(",", 1)[0]

    return dispatch_map["pt"]().rsplit(",", 1)[0]
