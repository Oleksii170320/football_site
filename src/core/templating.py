from fastapi.templating import Jinja2Templates

from config import TEMPLATE_PATH

templates = Jinja2Templates(directory=TEMPLATE_PATH)
