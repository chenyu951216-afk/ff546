from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.watchlist_service import get_watchlist

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/watchlist')
def watchlist(request: Request):
    return templates.TemplateResponse('watchlist.html', {'request': request, 'stocks': get_watchlist()})
