
# Webengineering 2 - Flask API


## Used Technologies and Concepts

[Welcome to Flask - Flask Documentation (2.2.x)](https://flask.palletsprojects.com/en/2.2.x/)

[SQLAlchemy ORM - SQLAlchemy 1.4 Documentation](https://docs.sqlalchemy.org/en/14/orm/)


## Environmet Variables

| Variable | Description                |
| :-------- | :------------------------- |
| `POSTGRES_PERSONAL_USER` | postgres db User |
| `POSTGRES_PERSONAL_PASSWORD` | db Password (same as user)|
| `KEYCLOAK_HOST` | for validation-Use (default = traefik) |
| `KEYCLOAK_REALM` | for validation-Use (default = biletado) |
| `POSTGRES_PERSONAL_DBNAME` | database name |
| `POSTGRES_PERSONAL_HOST` | Host of database |
| `POSTGRES_PERSONAL_PORT` | Port (same as Host) of database |
| `BACKEND_RESERVATIONS_IMAGE_REPOSITORY` | Image of this repository|
| `BACKEND_RESERVATIONS_IMAGE_VERSION` | Version of Image |


## Programs
| Programs | Description                |
| :-------- | :------------------------- |
| `app.py` | Creates the FLASK API in a Class and implements Configuration (App, Db and Logging) |
| `API_functions.py` | Implements API_functions class, which defines every function for the possible endpoints with the corresponding method [GET,PUT,POST,DELETE]|
| `routes.py` | This program contain the routes for the API and is the Main program for this project (runs the application) |
| `database.py` | Creates a model class with database scheme (reservations)|
| `authorization.py` | Handles the authorization for some methods , checks the validation of JWT |
| `validation.py` | Validates different Parameter values e.g JSON, Query and checks validation of inputs in the URL|

## Testing

