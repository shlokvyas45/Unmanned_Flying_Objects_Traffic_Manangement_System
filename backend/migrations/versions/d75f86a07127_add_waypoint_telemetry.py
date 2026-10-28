
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d75f86a07127"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waypoint_telemetry",
        sa.Column("telemetry_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("drone_id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=True),
        sa.Column("lat", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("lon", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("altitude_m", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("speed_mps", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("heading", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("battery_pct", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["drone_id"],
            ["drone.drone_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservation.reservation_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("telemetry_id"),
    )
    op.create_index(
        "idx_telemetry_drone_recorded",
        "waypoint_telemetry",
        ["drone_id", "recorded_at"],
        unique=False,
    )
    op.create_index(
        "ix_waypoint_telemetry_drone_id",
        "waypoint_telemetry",
        ["drone_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_waypoint_telemetry_drone_id",
        table_name="waypoint_telemetry",
    )
    op.drop_index(
        "idx_telemetry_drone_recorded",
        table_name="waypoint_telemetry",
    )
    op.drop_table("waypoint_telemetry")

