from fastapi.templating import Jinja2Templates

from config import TEMPLATE_PATH
from core.sessions import get_session

templates = Jinja2Templates(directory=TEMPLATE_PATH)


def render(template, request, context):
    session = get_session(request)
    context["request"] = request
    context["user"] = session["user"]
    return templates.TemplateResponse(template, context)
