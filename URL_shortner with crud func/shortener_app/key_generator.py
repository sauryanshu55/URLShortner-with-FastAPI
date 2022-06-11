from sqlalchemy.orm import Session
import secrets
import string
from shortener_app import crud_function

# """
# Key generation method upto the length 5, for the unique endpoint valuess, i.e /admin/{key-value}
# """
def create_random_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

# """
# While the chances are minimal, ensures that no two key-values are the same, iterates onn a while loop if same
# """
def create_unique_random_key(db: Session) -> str:
    key = create_random_key()
    while crud_function.get_database_url_by_key(db, key):
        key = create_random_key()
    return key