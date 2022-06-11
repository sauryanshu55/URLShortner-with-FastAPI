# URLShortner-with-FastAPI

Use the Shell command on the root directory
```
$> uvicorn shortener_app.main:API --reload
```
Navigate to the given address from the promt to the browser, which generally is:
<a href> http://127.0.0.1:8000/ </a> or alternatiely <a href> http://127.0.0.1:8000/docs#/ </a>
and the methof create_url in the SwaggerUI or http://127.0.0.1:8000/{url} to create the shortened link.

The program uses uvicorn webserver, and FastAPI to model an SQLite database. Included is a CRUD function to manage the  database.
