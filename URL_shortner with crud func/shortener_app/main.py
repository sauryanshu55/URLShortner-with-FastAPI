from email import message
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import crud_function
from . import preconditions, sqlite_types
from .sqlite_database import SessionLocal, engine
import secrets
import validators
from starlette.datastructures import URL
from .config import get_settings
# """
# URL shortner using FastAPI
# DATE: 11th June, 2022
# Author: Sauryanshu Khanal
# CITATIONS: https://www.youtube.com/watch?v=tLKKmouUams
#            https://codereview.stackexchange.com/questions/264277/designing-an-url-shortener
#            https://www.askpython.com/python/examples/url-shortener
#            https://simiokunowo.hashnode.dev/build-a-url-shortener-with-fastapi-mongodb-and-python

# 1. Webserver used is uvicorn
# 2. Interacts with the modeled SQLite database using CRUD functions
# 3. Bug in the number of counts, explained more in the documentation of the code




# """
# API instance that loads the FastAPI instance on to it. All FastAPi Methods, PUT, DELETE, GET and PUSH used on this instance, and all information stored on this instance
# """
API = FastAPI()
sqlite_types.Base.metadata.create_all(bind=engine)

# """
# API Homepage, http://127.0.0.1:8000/
# """
@API.get("/")
def api_homepage():
    return "URL shortner API\n Goto Swagger UI, create_shortened_url to shorten URL"

# """
# Opens an SQLLite database to store information that is to be followed
# """
def open_sqlite_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# """
# Raises an Error if the HTTP return is invalid as defined by the HTTPEXception class
# """
def return_http_error(error_msg):
    raise HTTPException(status_code=400, detail=error_msg)

# '''
# Raises an error if the HTTP gives no response
# '''
def return_absent_url(request):
    message = "URL '{given_url}' doesn't exist".format(given_url=request.url)
    raise HTTPException(status_code=404, detail=message)

# """
# Stores the admin info and returns db_url class to show on the webpage in the format of JSON files (coded as a dictionary in Python)
# """
def get_admin_info(db_url: sqlite_types.URL) -> preconditions.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = API.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

# """
# Returns the admin info: shortened link, secret pass + click count if as is in the db_url class. Else raises an HTTP exception
# """
@API.get("/admin/{secret_key}",name="admin Info",response_model=preconditions.URLInfo,)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(open_sqlite_database)):
    if db_url := crud_function.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        return_absent_url(request)


# """
# POST method to enter the info: userinput URL to the API, and then make a shortened link and then store the shortenned link to the API
# """
@API.post("/url", response_model=preconditions.URLInfo)
def create_url(url: preconditions.URLBase, db: Session = Depends(open_sqlite_database)):
    if not validators.url(url.target_url):
        return_http_error(message="Invalid URL Given")
    db_url = crud_function.create_database_url(db=db, url=url)
    return get_admin_info(db_url)

# OLD Code
# @API.get("/{url_key}")
# def adminpage_sqlite_database(url_key: str, request: Request, db: Session = Depends(open_sqlite_database)):
#     db_url = (
#         db.query(sqlite_types.URL)
#         .filter(sqlite_types.URL.key == url_key, sqlite_types.URL.is_active)
#         .first()
#     )
#     if db_url:
#         return RedirectResponse(db_url.target_url)
#     else:
#         return_absent_url(request)


@API.get("/{url_key}")
def forward_to_target_url(url_key: str, request: Request, db: Session = Depends(open_sqlite_database)):
    if db_url := crud_function.get_database_url_by_key(db=db, url_key=url_key):
        return RedirectResponse(db_url.target_url)
    else:
        return_absent_url(request=request)

# """
# If secret_key is correct and entered in the format /admin/{xxxxxx}, then the URL is deleted. Alternatively SwaggerUI can be used
# """
@API.delete("/admin/{secret_key}")
def delete_shortened_link(secret_key: str, request: Request, db: Session = Depends(open_sqlite_database)):
    if db_url := crud_function.delete_shortened_link(db, secret_key=secret_key):
        message = f"Deleted shortened URL for '{db_url.target_url}'"
        return {" ": message}
    else:
        return_absent_url(request)
