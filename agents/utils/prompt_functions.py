from google.adk.tools import FunctionTool
from catalog.tools.datetime import get_current_datetime as _get_datetime_func


def _get_current_datetime() -> str:
    """
    Retorna a data e hora atual formatada.
    Use esta ferramenta quando precisar saber a data ou hora atual.
    """
    return _get_datetime_func(include_time=True)


get_current_datetime = FunctionTool(_get_current_datetime)

__all__ = ["get_current_datetime"]
