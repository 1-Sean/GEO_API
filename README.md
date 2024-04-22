# Project Management API

## Overview
This API is designed to manage "projects," where a project represents a plot of land analyzed using satellite imagery captured within a selected date range. It supports operations like Create, Read, List, Delete, and Update for project management.

## Tech Stack
- **FastAPI** for the API framework
- **PostgreSQL** for data persistence
- **SQLAlchemy** as ORM for python to work with database
- **GEOAlchemy** for handling geospatial data within SQLAlchemy
- **Pydantic** for data validation
- **Alembic** for database migration
- **Docker** and **Docker Compose** for containerization
- **Poetry** package and dependency management

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Configuration
Before running the application, you need to set up your environment variables:

- Rename the `.env_copy` file in the root directory to `.env`.
- Open the .env file and update the environment variables with your own settings.
Make sure to set a password for `POSTGRES_PASSWORD`.

### Running the Application
1. Pull the project to your local machine.
2. Navigate to the root directory of the project.
3. Start the application using
```
docker compose up:
```
4. To initialize the database with the required tables, run in another terminal:
```
docker compose run --rm api alembic upgrade head
```

The API documentation can be accessed at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Endpoints

### Create Project
- **POST** `/projects/`
- Creates a new project with the specified information.

### Read Project
- **GET** `/projects/{name}`
- Retrieves details of a project by its name. Returns a geojson.

### List Projects
- **GET** `/projects/`
- Lists all projects, optionally with pagination.

### Delete Project
- **DELETE** `/projects/{name}`
- Deletes a project by its name.

### Update Project
- **PATCH** `/projects/{name}`
- Updates the details of an existing project.

### Get Projects within a Bounding Box
- **POST** `/projects/bbox`
- Retrieves projects within a specified bounding box.

### Get One GeoJSON with All Projects
- **GET** `/projects/geojson/`
- Returns a single GeoJSON FeatureCollection of all projects.

## Assumptions and Improvements

### Assumptions
- Projects have unique names.
- The daterange can be split up into 2 Fields; start- and end_date.

### Potential Improvements
- Implement soft delete functionality for projects.
- Add docstrings to each function for better code documentation.
- Write unit tests to ensure reliability and maintainability.
- Implement best practices for project structure


## Author

[@1-Sean](https://github.com/1-Sean)
