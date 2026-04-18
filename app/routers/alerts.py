from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.alerts_service import get_alerts

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/alerts')
def alerts(request: Request):
    return templates.TemplateResponse('alerts.html', {'request': request, 'alerts': get_alerts()})
