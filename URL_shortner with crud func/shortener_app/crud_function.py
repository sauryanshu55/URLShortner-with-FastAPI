from . import key_generator, sqlite_types, preconditions
from sqlalchemy.orm import Session
from shortener_app import key_generator


# """
# create_database_url method returns either None or a database entry with a provided key
# """
def create_database_url(db: Session, url: preconditions.URLBase) -> sqlite_types.URL:
    key = key_generator.create_unique_random_key(db)
    secret_key = f"{key}_{key_generator.create_random_key(length=8)}"
    db_url = sqlite_types.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


# """
# Both these functions flitrate the modeled SQLite database to search database by the keys, or  the secret key for the admin page
# """
def get_database_url_by_key(db: Session, url_key: str) -> sqlite_types.URL:
    return (
        db.query(sqlite_types.URL)
        .filter(sqlite_types.URL.key == url_key, sqlite_types.URL.is_active)
        .first()
    )

def get_db_url_by_secret_key(db: Session, secret_key: str) -> sqlite_types.URL:
    return (
        db.query(sqlite_types.URL)
        .filter(sqlite_types.URL.secret_key == secret_key, sqlite_types.URL.is_active)
        .first()
    )


# '''
# BUG here!
# Ideally should update the count as links are cliked, as of now, only remains 0
# '''
def update_link_clicks(db: Session, db_url: preconditions.URL) -> sqlite_types.URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url

# '''
# Deletes the shortened keys, as per the provided secret_key, if authemticated
# '''
def delete_shortened_link(db: Session, secret_key: str) -> sqlite_types.URL:
    db_url = get_db_url_by_secret_key(db, secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url    