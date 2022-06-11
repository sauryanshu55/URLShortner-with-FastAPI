from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import preconditions, sqlite_types
from .sqlite_database import SessionLocal, engine
# from http.client import HTTPException
import secrets
import validators

API = FastAPI()
sqlite_types.Base.metadata.create_all(bind=engine)

@API.get("/")
def api_homepage():
    return "URL shortner API\n Goto Swagger UI, create_shortened_url to shorten URL"

def open_sqlite_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def return_http_error(error_msg):
    raise HTTPException(status_code=400, detail=error_msg)


def return_absent_url(request):
    message = "URL '{given_url}' doesn't exist".format(given_url=request.url)
    raise HTTPException(status_code=404, detail=message)


@API.post("/url", response_model=preconditions.URLInfo)
def shorten_url(url: preconditions.URLBase, db: Session = Depends(open_sqlite_database)):
    if not validators.url(url.target_url):
        return_http_error(message="Invalid URL")

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "".join(secrets.choice(chars) for _ in range(5))
    password = "".join(secrets.choice(chars) for _ in range(8))
    db_url = sqlite_types.URL(target_url=url.target_url, key=key, secret_key=password)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.url = key
    db_url.admin_url = password

    return db_url


@API.get("/{url_key}")
def adminpage_sqlite_database(url_key: str, request: Request, db: Session = Depends(open_sqlite_database)):
    db_url = (
        db.query(sqlite_types.URL)
        .filter(sqlite_types.URL.key == url_key, sqlite_types.URL.is_active)
        .first()
    )
    if db_url:
        return RedirectResponse(db_url.target_url)
    else:
        return_absent_url(request)