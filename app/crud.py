from typing import Sequence, Optional, List, Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Project
from .schemas import ProjectCreate, ProjectUpdate
from utils.geojson_conversion import geojson_to_wkt, wkb_element_to_wkt


async def create_project(db: AsyncSession, project: ProjectCreate) -> Project:
    aoi_wkt = geojson_to_wkt(project.aoi.dict(by_alias=True))

    db_project = Project(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        aoi=aoi_wkt,
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def get_projects(
    db: AsyncSession, skip: int = 0, limit: Optional[int] = None
) -> List[Any]:
    projects = await db.execute(select(Project).offset(skip).limit(limit))
    projects_wkt = []
    for project in projects.scalars().all():
        project_data = dict(project.__dict__)
        project_data["aoi"] = wkb_element_to_wkt(project.aoi) if project.aoi else None
        projects_wkt.append(project_data)
    return projects_wkt


async def get_project_by_name(db: AsyncSession, name: str) -> Optional[Project]:
    async with db as session:
        query = select(Project).filter(Project.name == name)
        result = await session.execute(query)
        project = result.scalars().first()
        return project


async def get_projects_raw(
    db: AsyncSession, skip: int = 0, limit: Optional[int] = None
) -> Sequence[Project]:
    result = await db.execute(select(Project).offset(skip).limit(limit))
    return result.scalars().all()


async def get_projects_within_bbox(db: AsyncSession, bbox: List[float]) -> List[Any]:
    min_lon, min_lat, max_lon, max_lat = bbox
    query = select(Project).where(
        func.ST_Intersects(
            Project.aoi,
            func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326),
        )
    )
    projects = await db.execute(query)
    projects_wkt = []
    for project in projects.scalars().all():
        project_data = dict(project.__dict__)
        project_data["aoi"] = wkb_element_to_wkt(project.aoi) if project.aoi else None
        projects_wkt.append(project_data)
    return projects_wkt


async def update_project(
    db: AsyncSession, name: str, update_data: ProjectUpdate
) -> Optional[Project]:
    async with db as session:
        query = select(Project).filter(Project.name == name)
        result = await session.execute(query)
        project_to_update = result.scalars().first()

        if not project_to_update:
            return None

        new_name = update_data.name
        if new_name and new_name != name:
            existing_project_query = select(Project).filter(Project.name == new_name)
            existing_project = (
                (await session.execute(existing_project_query)).scalars().first()
            )
            if existing_project:
                raise HTTPException(
                    status_code=400, detail="Project with this name already exists"
                )

        if "aoi" in update_data.dict():
            aoi_wkt = geojson_to_wkt(update_data.aoi)
            update_data.aoi = aoi_wkt

        update_values = update_data.dict(exclude_unset=True, exclude={"aoi"})
        if "aoi" in update_data.dict():
            update_values["aoi"] = aoi_wkt

        for key, value in update_values.items():
            setattr(project_to_update, key, value)

        session.add(project_to_update)
        await session.commit()
        await session.refresh(project_to_update)

        return project_to_update


async def delete_project(db: AsyncSession, name: str):
    async with db as session:
        query = select(Project).filter(Project.name == name)
        result = await session.execute(query)
        project_to_delete = result.scalars().first()
        if project_to_delete:
            await session.delete(project_to_delete)
            await session.commit()
        else:
            raise HTTPException(status_code=404, detail="Project not found")
