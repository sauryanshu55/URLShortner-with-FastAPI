# """
# preconditions.py stores the data types of the data stored in the API as classes inheriting BaseModel
# """
from pydantic import BaseModel


class URLBase(BaseModel):
    target_url: str #target_url stores the the URL that the shortened URL will redirect to


class URL(URLBase):
    is_active: bool #True if the shortened link is active
    clicks: int #number of clikcs (There is a bug in this update method, something to do in the crud function)

    class Config:
        orm_mode = True


class URLInfo(URL):
    url: str #Final Shortened URL
    admin_url: str #admin URL to access the admin page