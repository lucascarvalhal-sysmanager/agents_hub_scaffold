import os
from datetime import datetime

TRANSLATIONS = {
    "pt": {
        "days": ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                 "Sexta-feira", "Sábado", "Domingo"],
        "months": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        "format": "{day}, {d} de {month} de {year}, {time}"
    },
    "en": {
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"],
        "months": ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
        "format": "{day}, {month} {d}, {year}, {time}"
    },
    "es": {
        "days": ["Lunes", "Martes", "Miércoles", "Jueves",
                 "Viernes", "Sábado", "Domingo"],
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        "format": "{day}, {d} de {month} de {year}, {time}"
    },
}


def get_current_datetime(include_time: bool = True) -> str:
 
    language = os.getenv("DATETIME_LANGUAGE", "pt")
    trans = TRANSLATIONS.get(language, TRANSLATIONS["pt"])
    now = datetime.now()

    result = trans["format"].format(
        day=trans["days"][now.weekday()],
        month=trans["months"][now.month - 1],
        d=now.day,
        year=now.year,
        time=now.strftime("%H:%M:%S")
    )

    if include_time:
        return result
    return result.rsplit(",", 1)[0]
