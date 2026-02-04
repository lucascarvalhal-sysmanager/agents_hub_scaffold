from datetime import datetime

def formatted_date_today():
    """Retorna a data atual formatada em inglês."""
    weekdays = ["monday", "tuesday", "wednesday", "thursday",
                "friday", "saturday", "sunday"]
    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]

    today = datetime.now()
    weekday = weekdays[today.weekday()]
    day = today.day
    month = months[today.month - 1]
    year = today.year

    return f"Today is {weekday}, {month} {day}, {year}."


def get_current_datetime() -> str:
    """
    Retorna a data e hora atual formatada em português do Brasil.
    Use esta ferramenta quando o usuário perguntar sobre data, hora, dia da semana ou qualquer informação temporal.

    Returns:
        str: Data e hora atual no formato "Dia da semana, DD de Mês de AAAA, HH:MM:SS"
    """
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                   "Sexta-feira", "Sábado", "Domingo"]
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    agora = datetime.now()
    dia_semana = dias_semana[agora.weekday()]
    dia = agora.day
    mes = meses[agora.month - 1]
    ano = agora.year
    hora = agora.strftime("%H:%M:%S")

    return f"{dia_semana}, {dia} de {mes} de {ano}, {hora}"