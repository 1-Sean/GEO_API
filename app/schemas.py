from datetime import date, datetime
from typing import Optional, List, Union

from pydantic import BaseModel, Field, field_validator
from geojson_pydantic.geometries import MultiPolygon, Polygon
from pydantic_core.core_schema import FieldValidationInfo

example_project = {
    "name": "project_name",
    "description": "An example project description",
    "start_date": "2023-04-01",
    "end_date": "2024-04-30",
    "aoi": {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [-52.8430645648562, -5.63351005831322],
                    [-52.8289481608136, -5.674529420529012],
                    [-52.8114438198008, -5.6661010219506664],
                    [-52.8430645648562, -5.63351005831322],
                ]
            ]
        ],
    },
}


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=32)
    description: Optional[str] = None
    start_date: date
    end_date: date
    aoi: Union[Polygon, MultiPolygon]

    @field_validator("end_date")
    def check_dates(cls, end_date: date, info: FieldValidationInfo) -> date:
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        return end_date

    class Config:
        schema_extra = {"example": example_project}


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=32)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    aoi: Optional[MultiPolygon] = None


# class Project(BaseModel):
#     id: UUID4
#     name: str = Field(..., max_length=32)
#     description: Optional[str] = None
#     start_date: date
#     end_date: date
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     aoi: MultiPolygon
#
#     class Config:
#         orm_mode = True
#         from_attributes = True


class ProjectResponseBase(BaseModel):
    name: str = Field(..., max_length=32)
    description: Optional[str] = None
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProjectResponseWKT(ProjectResponseBase):
    aoi: str


class ProjectResponseGeoJSON(BaseModel):
    type: str = "Feature"
    geometry: MultiPolygon
    properties: ProjectResponseBase


class ProjectGeoJSONFeatureCollection(BaseModel):
    type: str = Field(default="FeatureCollection")
    features: List[ProjectResponseGeoJSON]
