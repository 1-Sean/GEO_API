"""Add aoi column to projects

Revision ID: 0f6f85c832a8
Revises: 580574bff74a
Create Date: 2024-03-14 19:26:28.938831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "0f6f85c832a8"
down_revision: Union[str, None] = "580574bff74a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### auto generation did not work at all - command added manually ###
    op.add_column(
        "projects",
        sa.Column("aoi", Geometry("MULTIPOLYGON", srid=4326), nullable=False),
        schema="project_data",
    )  # ### end Alembic commands ###


def downgrade() -> None:
    # ### auto generation did not work at all - command added manually ###
    op.drop_column("projects", "aoi", schema="project_data")
    # ### end Alembic commands ###
