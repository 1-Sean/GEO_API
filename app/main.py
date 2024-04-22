# main.py
from fastapi import FastAPI, HTTPException, Depends, Body
from typing import List, Optional, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from utils.geojson_conversion import wkb_element_to_wkt, wkb_to_geojson
from .crud import get_projects_within_bbox
from .database import SessionLocal
from . import crud
from .schemas import (
    ProjectResponseWKT,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponseGeoJSON,
    ProjectResponseBase,
    ProjectGeoJSONFeatureCollection,
    example_project,
)

app = FastAPI()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db


@app.post(
    "/projects/", response_model=ProjectResponseWKT, status_code=status.HTTP_201_CREATED
)
async def create_project(
    project: ProjectCreate = Body(..., example=example_project),
    db: AsyncSession = Depends(get_db),
):
    db_project = await crud.get_project_by_name(db, name=project.name)
    if db_project:
        raise HTTPException(status_code=400, detail="Project already registered")
    created_project = await crud.create_project(db=db, project=project)

    project_dict = created_project.__dict__.copy()
    project_dict["aoi"] = (
        wkb_element_to_wkt(created_project.aoi) if created_project.aoi else ""
    )
    response_model = ProjectResponseWKT(**project_dict)
    return response_model


@app.get("/projects/{name}", response_model=ProjectResponseGeoJSON)
async def read_project_by_name(name: str, db: AsyncSession = Depends(get_db)):
    project = await crud.get_project_by_name(db, name=name)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    project_geojson = ProjectResponseGeoJSON(
        geometry=wkb_to_geojson(project.aoi),
        properties=ProjectResponseBase(
            name=project.name,
            description=project.description,
            start_date=project.start_date,  # type: ignore #"Date"; expected "date"
            end_date=project.end_date,  # type: ignore
            created_at=project.created_at,  # type: ignore
            updated_at=project.updated_at,  # type: ignore
        ),
    )

    return project_geojson


@app.get("/projects/", response_model=List[ProjectResponseWKT])
async def read_projects(
    skip: int = 0, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    projects = await crud.get_projects(db, skip=skip, limit=limit)
    return projects


@app.get("/projects/geojson/", response_model=ProjectGeoJSONFeatureCollection)
async def get_all_projects_geojson(db: AsyncSession = Depends(get_db)):
    db_projects = await crud.get_projects_raw(db)
    features = [
        ProjectResponseGeoJSON(
            type="Feature",
            geometry=wkb_to_geojson(db_project.aoi),
            properties=ProjectResponseBase(
                name=db_project.name,
                description=db_project.description,
                start_date=db_project.start_date,  # type: ignore #"Date"; expected "date"
                end_date=db_project.end_date,  # type: ignore
                created_at=db_project.created_at,  # type: ignore
                updated_at=db_project.updated_at,  # type: ignore
            ),
        )
        for db_project in db_projects
    ]
    return ProjectGeoJSONFeatureCollection(features=features)


@app.post("/projects/bbox", response_model=List[ProjectResponseWKT])
async def read_projects_within_bbox(
    bbox: List[float] = Body(..., example=[-53.8431, -5.6745, -52.8114, -5.6335]),
    db: AsyncSession = Depends(get_db),
):
    projects = await get_projects_within_bbox(db, bbox)
    if not projects:
        raise HTTPException(
            status_code=404, detail="No projects found within the given bounding box."
        )
    return projects


@app.patch("/projects/{name}", response_model=ProjectResponseWKT)
async def update_project(
    name: str, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    updated_project = await crud.update_project(
        db=db, name=name, update_data=project_update
    )
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dict = updated_project.__dict__.copy()
    project_dict["aoi"] = (
        wkb_element_to_wkt(updated_project.aoi) if updated_project.aoi else ""
    )
    response_model = ProjectResponseWKT(**project_dict)
    return response_model


@app.delete("/projects/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_(name: str, db: AsyncSession = Depends(get_db)):
    await crud.delete_project(db=db, name=name)
