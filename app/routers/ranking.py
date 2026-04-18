from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.ranking_service import build_rankings

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/ranking')
def ranking(request: Request):
    payload = build_rankings()
    return templates.TemplateResponse('ranking.html', {'request': request, **payload})
